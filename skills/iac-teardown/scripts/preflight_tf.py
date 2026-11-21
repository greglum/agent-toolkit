#!/usr/bin/env python3
"""Static preflight checker for Terraform and OpenTofu stack teardowns.

Scans HCL files (plus optional state-list and plan-JSON outputs) for common outage
and failure traps before destroy: unapplied or stale import blocks, shared DNS or
email records, lifecycle and deletion-protection locks, non-empty versioned stores,
and unexpected plan drift or deferred database updates. Exit 0 means clean, 2 means
findings reported, and 1 means an invocation or input error.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

TOP_RESOURCE_RE = re.compile(r'(resource|data)\s+"([^"]+)"\s+"([^"]+)"\s*\{')
TOP_IMPORT_RE = re.compile(r'import\s*\{')
HEREDOC_RE = re.compile(r'<<-?([A-Za-z_][A-Za-z0-9_-]*)[ \t]*\r?\n')
IMPORT_TO_RE = re.compile(r'\bto\s*=\s*((?:[^\s#/{}"\[]+|\[(?:"(?:\\.|[^"\\])*"|[^\]])*\])+)')
LIFECYCLE_LOCK_RE = re.compile(r'\b(prevent_destroy|skip_destroy)\s*=\s*true\b')
DEL_PROT_RE = re.compile(
    r'\b(deletion_protection(?:_enabled)?)\s*=\s*(?:true|"ACTIVE")'
)
DNS_ZONE_TYPES = frozenset({'aws_route53_zone', 'google_dns_managed_zone'})
DNS_TYPES = frozenset({'aws_route53_record', 'google_dns_record_set', 'cloudflare_record', 'cloudflare_dns_record'}) | DNS_ZONE_TYPES
HIGH_DNS_RE = re.compile(
    r'(?:^|[^A-Za-z0-9])(?:MX|CAA|TXT|SPF|DKIM|DMARC|validation|site_apex|site_www)(?:$|[^A-Za-z0-9])'
    r'|_dmarc|v=spf1|_domainkey|acm-validations',
    re.I,
)
STORE_NO_FORCE = {
    'aws_s3_bucket': re.compile(r'\bforce_destroy\s*=\s*true\b'),
    'google_storage_bucket': re.compile(r'\bforce_destroy\s*=\s*true\b'),
    'aws_ecr_repository': re.compile(r'\bforce_delete\s*=\s*true\b'),
}


def strip_hcl_comments(text: str) -> str:
    """Replace #/ // line comments and /* */ block comments with spaces, keeping newlines."""
    out: list[str] = []
    n = len(text)
    i = 0
    in_string = False
    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if ch == '\\' and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue
        if ch == '<' and i + 1 < n and text[i + 1] == '<':
            after_hd = _consume_heredoc(text, i)
            if after_hd is not None:
                out.append(text[i:after_hd])
                i = after_hd
                continue
        if ch == '#' or (ch == '/' and i + 1 < n and text[i + 1] == '/'):
            while i < n and text[i] != '\n':
                out.append(' ')
                i += 1
            continue
        if ch == '/' and i + 1 < n and text[i + 1] == '*':
            out.append(' ')
            out.append(' ')
            i += 2
            while i < n:
                if text[i] == '*' and i + 1 < n and text[i + 1] == '/':
                    out.append(' ')
                    out.append(' ')
                    i += 2
                    break
                out.append('\n' if text[i] == '\n' else ' ')
                i += 1
            continue
        out.append(ch)
        i += 1
    return ''.join(out)


def _consume_heredoc(text: str, pos: int) -> int | None:
    match = HEREDOC_RE.match(text, pos)
    if not match:
        return None
    indented = text[pos + 2:pos + 3] == '-'
    marker = match.group(1)
    cursor = match.end()
    n = len(text)
    while cursor < n:
        nl = text.find('\n', cursor)
        line_end = nl if nl != -1 else n
        line = text[cursor:line_end].rstrip('\r')
        if (line.strip() if indented else line) == marker:
            return (nl + 1) if nl != -1 else n
        cursor = (nl + 1) if nl != -1 else n
    return n


def _skip_block(stripped: str, brace_idx: int) -> int:
    n = len(stripped)
    depth = 0
    in_string = False
    i = brace_idx
    while i < n:
        ch = stripped[i]
        if in_string:
            if ch == '\\' and i + 1 < n:
                i += 2
                continue
            if ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            i += 1
            continue
        if ch == '<' and i + 1 < n and stripped[i + 1] == '<':
            after_hd = _consume_heredoc(stripped, i)
            if after_hd is not None:
                i = after_hd
                continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def extract_top_blocks(stripped: str) -> list[dict]:
    """Extract top-level resource, data, and import blocks at brace depth 0."""
    blocks: list[dict] = []
    n = len(stripped)
    i = 0
    in_string = False
    while i < n:
        ch = stripped[i]
        if in_string:
            if ch == '\\' and i + 1 < n:
                i += 2
                continue
            if ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            i += 1
            continue
        if ch == '<' and i + 1 < n and stripped[i + 1] == '<':
            after_hd = _consume_heredoc(stripped, i)
            if after_hd is not None:
                i = after_hd
                continue
        if i == 0 or not (stripped[i - 1].isalnum() or stripped[i - 1] == '_'):
            res_match = TOP_RESOURCE_RE.match(stripped, i)
            if res_match:
                brace_idx = res_match.end() - 1
                end_idx = _skip_block(stripped, brace_idx)
                blocks.append({
                    'kind': res_match.group(1),
                    'type': res_match.group(2),
                    'name': res_match.group(3),
                    'line': stripped[:res_match.start()].count('\n') + 1,
                    'body': stripped[brace_idx:end_idx],
                })
                i = end_idx
                continue
            imp_match = TOP_IMPORT_RE.match(stripped, i)
            if imp_match:
                brace_idx = imp_match.end() - 1
                end_idx = _skip_block(stripped, brace_idx)
                blocks.append({
                    'kind': 'import',
                    'type': '',
                    'name': '',
                    'line': stripped[:imp_match.start()].count('\n') + 1,
                    'body': stripped[brace_idx:end_idx],
                })
                i = end_idx
                continue
        if ch == '{':
            i = _skip_block(stripped, i)
            continue
        i += 1
    return blocks


def scan_tf_file(path: Path, display: str, state_addrs: set[str] | None) -> list[dict]:
    """Scan one .tf file for teardown hazards."""
    text = path.read_text(encoding='utf-8', errors='replace')
    stripped = strip_hcl_comments(text)
    findings: list[dict] = []

    for blk in extract_top_blocks(stripped):
        kind, rtype, rname, line, body = blk['kind'], blk['type'], blk['name'], blk['line'], blk['body']
        address = f'{rtype}.{rname}' if rtype and rname else kind

        if kind == 'import':
            to_match = IMPORT_TO_RE.search(body)
            target = to_match.group(1) if to_match else '<unknown>'
            if state_addrs is None:
                findings.append({
                    'rule': 'unapplied_import_block',
                    'severity': 'high',
                    'file': display,
                    'line': line,
                    'address': target,
                    'message': f"Import block targets '{target}'; verify state and strip unapplied imports before any apply or destroy.",
                })
            elif target not in state_addrs and not any(a.startswith(target + '[') for a in state_addrs):
                findings.append({
                    'rule': 'unapplied_import_block',
                    'severity': 'high',
                    'file': display,
                    'line': line,
                    'address': target,
                    'message': f"Unapplied import block for '{target}' not in state; running apply before removal will pull live resources into this stack.",
                })
            else:
                findings.append({
                    'rule': 'stale_import_block',
                    'severity': 'medium',
                    'file': display,
                    'line': line,
                    'address': target,
                    'message': f"Import block for '{target}' is already in state; remove the one-shot block before teardown.",
                })
            continue

        if kind != 'resource':
            continue

        if rtype in DNS_TYPES:
            is_high = rtype in DNS_ZONE_TYPES or bool(HIGH_DNS_RE.search(rname) or HIGH_DNS_RE.search(body))
            findings.append({
                'rule': 'shared_dns_or_email_record',
                'severity': 'high' if is_high else 'medium',
                'file': display,
                'line': line,
                'address': address,
                'message': (
                    f"DNS record '{address}' may serve live mail, certificate validation, or sibling services; "
                    'migrate via import + state rm before destroy.'
                ),
            })

        for lock_match in LIFECYCLE_LOCK_RE.finditer(body):
            attr = lock_match.group(1)
            findings.append({
                'rule': 'lifecycle_lock',
                'severity': 'medium',
                'file': display,
                'line': line + body[:lock_match.start()].count('\n'),
                'address': address,
                'message': f"Lifecycle '{attr} = true' on '{address}' will block destroy until cleared in a staged edit.",
            })

        for dp_match in DEL_PROT_RE.finditer(body):
            attr = dp_match.group(1)
            findings.append({
                'rule': 'deletion_protection',
                'severity': 'medium',
                'file': display,
                'line': line + body[:dp_match.start()].count('\n'),
                'address': address,
                'message': f"'{attr}' is active on '{address}'; confirm zero live data before unlocking in a targeted apply.",
            })

        force_re = STORE_NO_FORCE.get(rtype)
        if force_re and not force_re.search(body):
            findings.append({
                'rule': 'versioned_or_nonempty_store',
                'severity': 'medium',
                'file': display,
                'line': line,
                'address': address,
                'message': f"Store '{address}' lacks force delete/destroy; empty object versions, delete markers, or container images before destroy.",
            })

    return findings


def scan_plan_json(plan_path: Path) -> list[dict]:
    """Inspect terraform show -json output for mixed drift or deferred DB updates."""
    data = json.loads(plan_path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('plan JSON root must be an object')
    changes = data.get('resource_changes')
    if changes is None:
        return []
    if not isinstance(changes, list):
        raise ValueError('plan JSON resource_changes must be a list')

    findings: list[dict] = []
    has_delete = False
    updates_and_replaces: list[tuple[str, list[str]]] = []
    for rc in changes:
        if not isinstance(rc, dict):
            continue
        addr = str(rc.get('address') or '<unknown>')
        change = rc.get('change') if isinstance(rc.get('change'), dict) else {}
        actions = [str(a) for a in (change.get('actions') or [])]
        if 'delete' in actions and 'create' not in actions:
            has_delete = True
        if actions in (['update'], ['create']) or set(actions) == {'delete', 'create'}:
            updates_and_replaces.append((addr, actions))

        rtype = str(rc.get('type') or '')
        if rtype in ('aws_rds_cluster', 'aws_db_instance') and 'update' in actions:
            before = change.get('before') if isinstance(change.get('before'), dict) else {}
            after = change.get('after') if isinstance(change.get('after'), dict) else {}
            pw_changed = (
                before.get('manage_master_user_password') != after.get('manage_master_user_password')
                or before.get('master_password_wo_version') != after.get('master_password_wo_version')
            )
            if pw_changed and after.get('apply_immediately') is not True:
                findings.append({
                    'rule': 'deferred_db_change',
                    'severity': 'high',
                    'file': plan_path.name,
                    'line': 1,
                    'address': addr,
                    'message': f"DB password or rotation change on '{addr}' lacks apply_immediately = true and may wait for the maintenance window.",
                })

    if has_delete and updates_and_replaces:
        for addr, actions in updates_and_replaces:
            findings.append({
                'rule': 'plan_unexpected_drift',
                'severity': 'high',
                'file': plan_path.name,
                'line': 1,
                'address': addr,
                'message': f"Plan mixes delete operations with {actions} on '{addr}'; verify whether unrelated drift requires -target= scoping.",
            })

    return findings


def collect_tf_files(targets: list[str]) -> list[tuple[Path, str]]:
    """Resolve CLI path arguments to sorted .tf files, returning error on missing paths."""
    found: list[tuple[Path, str]] = []
    seen: set[Path] = set()
    for raw in targets:
        p = Path(raw)
        if not p.exists():
            raise FileNotFoundError(f'Path does not exist: {raw}')
        if p.is_file():
            if p.suffix != '.tf':
                raise ValueError(f'Not a .tf file: {raw}')
            resolved = p.resolve()
            if resolved not in seen:
                seen.add(resolved)
                found.append((resolved, p.name))
        elif p.is_dir():
            for child in sorted(p.rglob('*.tf')):
                if '.terraform' in child.parts:
                    continue
                resolved = child.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    found.append((resolved, child.relative_to(p).as_posix()))
    return found


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='+', help='Terraform directories or .tf files to preflight.')
    parser.add_argument('--state-list', type=Path, help='Optional file containing output of `terraform state list`.')
    parser.add_argument('--plan-json', type=Path, help='Optional file containing output of `terraform show -json <tfplan>`.')
    args = parser.parse_args(argv)

    try:
        files = collect_tf_files(args.paths)
        state_addrs: set[str] | None = None
        if args.state_list is not None:
            state_addrs = {
                ln.strip() for ln in args.state_list.read_text(encoding='utf-8').splitlines() if ln.strip()
            }
        findings: list[dict] = []
        for path, display in files:
            findings.extend(scan_tf_file(path, display, state_addrs))
        if args.plan_json is not None:
            findings.extend(scan_plan_json(args.plan_json))
    except (OSError, ValueError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1

    counts: dict[str, int] = {}
    for f in findings:
        counts[f['rule']] = counts.get(f['rule'], 0) + 1
    payload = {
        'schema': 'iac-teardown-preflight/v1',
        'files_scanned': len(files),
        'clean': not findings,
        'counts': counts,
        'findings': findings,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 2 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
