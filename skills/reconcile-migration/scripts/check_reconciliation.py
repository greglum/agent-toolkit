#!/usr/bin/env python3
"""Check migration reconciliation manifests and per-key extracts without emitting raw row data."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

CATCHALL_TOKENS = frozenset({'', 'other', 'unmapped', 'unknown', 'misc', 'dropped', 'skipped'})
SHA_DIGEST_LEN = 10


def unique_members(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON member')
        result[key] = value
    return result


def short_digest(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8', 'surrogatepass')).hexdigest()[:SHA_DIGEST_LEN]


def normalize_reason(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '_', text.strip().lower()).strip('_')


def check_drop_reason(
    findings: list[dict],
    code_target: str,
    location: str,
    reason: object,
    strict_drops: bool,
    has_impact: bool = True,
) -> None:
    if not isinstance(reason, str) or not reason.strip():
        findings.append({'code': 'catchall_drop_rule', 'target': code_target, 'where': location})
        return
    if normalize_reason(reason) in CATCHALL_TOKENS:
        findings.append({'code': 'catchall_drop_rule', 'target': code_target, 'where': location})
        return
    if strict_drops and has_impact:
        words = [w for w in reason.strip().split() if w]
        if len(words) < 2 or len(reason.strip()) < 8:
            findings.append({'code': 'vague_drop_rule', 'target': code_target, 'where': location})


def require_non_empty_str(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'invalid {label}')
    return value.strip()


def require_non_neg_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f'invalid {label}')
    return value


def resolve_extract_path(base_dir: Path, raw_path: object, label: str) -> Path:
    rel = require_non_empty_str(raw_path, label)
    candidate = Path(rel)
    if candidate.is_absolute():
        raise ValueError(f'{label} must be relative to manifest directory')
    resolved = (base_dir / candidate).resolve()
    if not resolved.is_relative_to(base_dir):
        raise ValueError(f'{label} escapes manifest directory')
    if not resolved.is_file():
        raise ValueError(f'{label} file is missing')
    return resolved


def load_extract(path: Path) -> dict[str, list[str]]:
    by_key: dict[str, list[str]] = defaultdict(list)
    with path.open('r', encoding='utf-8') as stream:
        for raw in stream:
            stripped = raw.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped, object_pairs_hook=unique_members)
            except ValueError as error:
                raise ValueError('invalid extract JSON record') from error
            if not isinstance(record, dict) or 'key' not in record:
                raise ValueError('extract record missing key')
            key = record['key']
            if isinstance(key, bool) or not isinstance(key, (str, int)):
                raise ValueError('extract key must be string or integer')
            key_text = f's:{key}' if isinstance(key, str) else f'i:{key}'
            if 'hash' in record and record['hash'] is not None:
                digest = require_non_empty_str(record['hash'], 'extract hash')
            elif 'payload' in record:
                canonical = json.dumps(record['payload'], sort_keys=True, separators=(',', ':'))
                digest = hashlib.sha256(canonical.encode('utf-8', 'surrogatepass')).hexdigest()
            else:
                raise ValueError('extract record requires hash or payload')
            by_key[key_text].append(digest)
    for digests in by_key.values():
        digests.sort()
    return by_key


def check_tables_and_columns(manifest: dict, strict_drops: bool, findings: list[dict]) -> None:
    source_tables = manifest.get('source_tables')
    mappings = manifest.get('table_mappings')
    dropped_tables = manifest.get('dropped_tables', {})
    column_inventory = manifest.get('column_inventory')
    if (not isinstance(source_tables, list) or not all(isinstance(t, str) and t.strip() for t in source_tables)
            or not isinstance(mappings, dict) or not isinstance(dropped_tables, dict)
            or not isinstance(column_inventory, dict)):
        raise ValueError('invalid table or column manifest collections')
    if len(set(source_tables)) != len(source_tables):
        raise ValueError('duplicate entries in source_tables')

    for table, target in mappings.items():
        require_non_empty_str(table, 'mapped table name')
        require_non_empty_str(target, 'mapped target table name')
    for table, reason in dropped_tables.items():
        require_non_empty_str(table, 'dropped table name')
        check_drop_reason(findings, table, 'dropped_tables', reason, strict_drops, has_impact=True)

    for table in source_tables:
        if table not in mappings and table not in dropped_tables:
            findings.append({'code': 'unaccounted_source_table', 'target': table})
    for table in sorted(set(mappings) & set(dropped_tables)):
        findings.append({'code': 'conflicting_table_disposition', 'target': table})
    for table in sorted(set(mappings) - set(source_tables)):
        findings.append({'code': 'undeclared_mapped_table', 'target': table})
    for table in sorted(set(dropped_tables) - set(source_tables)):
        findings.append({'code': 'undeclared_dropped_table', 'target': table})

    for table in sorted(mappings):
        inv = column_inventory.get(table)
        if not isinstance(inv, dict):
            findings.append({'code': 'missing_column_inventory', 'target': table})
            continue
        schema = inv.get('source_schema')
        if not isinstance(schema, str) or not schema.strip():
            findings.append({'code': 'unscoped_column_inventory', 'target': table})
        src_cols = inv.get('source_columns')
        copied = inv.get('copied_columns')
        transformed = inv.get('transformed_columns', [])
        dropped_cols = inv.get('dropped_columns', {})
        if (not isinstance(src_cols, list) or not isinstance(copied, list)
                or not isinstance(transformed, list) or not isinstance(dropped_cols, dict)
                or not all(isinstance(c, str) and c.strip() for c in src_cols + copied + transformed)):
            raise ValueError(f'invalid column lists for {table}')
        for col, reason in dropped_cols.items():
            require_non_empty_str(col, 'dropped column name')
            check_drop_reason(findings, table, f'dropped_columns:{col}', reason, strict_drops, has_impact=True)
        overlap_cols = sorted((set(copied) | set(transformed)) & set(dropped_cols))
        if overlap_cols:
            findings.append({
                'code': 'conflicting_column_disposition',
                'target': table,
                'count': len(overlap_cols),
                'columns': overlap_cols[:10],
            })
        accounted = set(copied) | set(transformed) | set(dropped_cols)
        missing_cols = sorted(set(src_cols) - accounted)
        if missing_cols:
            findings.append({
                'code': 'unaccounted_source_column',
                'target': table,
                'count': len(missing_cols),
                'columns': missing_cols[:10],
            })


def check_row_checks(
    manifest: dict,
    base_dir: Path,
    strict_drops: bool,
    findings: list[dict],
) -> tuple[int, dict[str, int]]:
    row_checks = manifest.get('row_checks')
    mappings = manifest.get('table_mappings', {})
    if not isinstance(row_checks, list):
        raise ValueError('row_checks must be a list')
    global_cutoff = manifest.get('cutoff_timestamp')
    if global_cutoff is not None:
        global_cutoff = require_non_empty_str(global_cutoff, 'cutoff_timestamp')

    totals = {'source_rows': 0, 'target_rows': 0, 'named_drops': 0, 'folded_rows': 0}
    seen_tables: set[str] = set()
    dup_tables: set[str] = set()
    for idx, entry in enumerate(row_checks):
        if not isinstance(entry, dict):
            raise ValueError('row_check entry must be an object')
        table = require_non_empty_str(entry.get('table'), f'row_checks[{idx}].table')
        if table in seen_tables:
            dup_tables.add(table)
        seen_tables.add(table)
        src_count = require_non_neg_int(entry.get('source_row_count'), f'row_checks[{idx}].source_row_count')
        tgt_count = require_non_neg_int(entry.get('target_row_count'), f'row_checks[{idx}].target_row_count')
        allow_fold = entry.get('allow_fold', False)
        if not isinstance(allow_fold, bool):
            raise ValueError('allow_fold must be boolean')
        folded = require_non_neg_int(entry.get('expected_folded_rows', 0), 'expected_folded_rows')
        if folded > 0 and not allow_fold:
            findings.append({'code': 'undeclared_fold_rows', 'target': table, 'expected_folded_rows': folded})

        named_drops = entry.get('named_drops', {})
        if not isinstance(named_drops, dict):
            raise ValueError('named_drops must be an object')
        drop_sum = 0
        for reason, count in named_drops.items():
            cnt = require_non_neg_int(count, 'named_drops count')
            drop_sum += cnt
            check_drop_reason(findings, table, f'named_drops:{normalize_reason(str(reason)) or "empty"}',
                              reason, strict_drops, has_impact=cnt > 0)

        totals['source_rows'] += src_count
        totals['target_rows'] += tgt_count
        totals['named_drops'] += drop_sum
        totals['folded_rows'] += folded

        src_cutoff = entry.get('source_cutoff')
        tgt_cutoff = entry.get('target_cutoff')
        if src_cutoff is not None or tgt_cutoff is not None:
            src_ok = isinstance(src_cutoff, str) and bool(src_cutoff.strip())
            tgt_ok = isinstance(tgt_cutoff, str) and bool(tgt_cutoff.strip())
            if not src_ok or not tgt_ok:
                findings.append({'code': 'split_cutoff_clock', 'target': table})
            else:
                src_val = src_cutoff.strip()
                tgt_val = tgt_cutoff.strip()
                if src_val != tgt_val or (global_cutoff is not None and src_val != global_cutoff):
                    findings.append({'code': 'split_cutoff_clock', 'target': table})

        expected_target = src_count - drop_sum - folded
        if expected_target != tgt_count:
            findings.append({
                'code': 'unexplained_row_delta',
                'target': table,
                'source_row_count': src_count,
                'named_drops': drop_sum,
                'expected_folded_rows': folded,
                'target_row_count': tgt_count,
                'delta': tgt_count - expected_target,
            })

        src_path = resolve_extract_path(base_dir, entry.get('source_extract'), f'row_checks[{idx}].source_extract')
        tgt_path = resolve_extract_path(base_dir, entry.get('target_extract'), f'row_checks[{idx}].target_extract')
        src_keys = load_extract(src_path)
        tgt_keys = load_extract(tgt_path)

        actual_src_rows = sum(len(v) for v in src_keys.values())
        actual_tgt_rows = sum(len(v) for v in tgt_keys.values())
        expected_src_rows = src_count - drop_sum
        if actual_src_rows != expected_src_rows or actual_tgt_rows != tgt_count:
            findings.append({
                'code': 'extract_count_mismatch',
                'target': table,
                'expected_source_extract_rows': expected_src_rows,
                'actual_source_extract_rows': actual_src_rows,
                'expected_target_extract_rows': tgt_count,
                'actual_target_extract_rows': actual_tgt_rows,
            })

        missing = sorted(short_digest(k) for k in src_keys.keys() - tgt_keys.keys())
        extra = sorted(short_digest(k) for k in tgt_keys.keys() - src_keys.keys())
        if missing:
            findings.append({'code': 'missing_target_key', 'target': table, 'count': len(missing), 'key_digests': missing[:5]})
        if extra:
            findings.append({'code': 'extra_target_key', 'target': table, 'count': len(extra), 'key_digests': extra[:5]})

        common = src_keys.keys() & tgt_keys.keys()
        if not allow_fold:
            collapsed = sorted(
                short_digest(k) for k in common if len(src_keys[k]) > 1 and len(tgt_keys[k]) == 1
            )
            if collapsed:
                findings.append({
                    'code': 'collapsed_duplicate_keys',
                    'target': table,
                    'count': len(collapsed),
                    'key_digests': collapsed[:5],
                })
        else:
            actual_folded = sum(
                len(src_keys[k]) - 1 for k in common if len(src_keys[k]) > 1 and len(tgt_keys[k]) == 1
            )
            if actual_folded != folded:
                findings.append({
                    'code': 'fold_count_mismatch',
                    'target': table,
                    'expected_folded_rows': folded,
                    'actual_folded_rows': actual_folded,
                })
        mismatched = sorted(
            short_digest(k) for k in common
            if src_keys[k] != tgt_keys[k] and not (len(src_keys[k]) > 1 and len(tgt_keys[k]) == 1)
        )
        if mismatched:
            findings.append({
                'code': 'hash_mismatch',
                'target': table,
                'count': len(mismatched),
                'key_digests': mismatched[:5],
            })

    for table in sorted(dup_tables):
        findings.append({'code': 'duplicate_row_check', 'target': table})
    for table in sorted(seen_tables - set(mappings)):
        findings.append({'code': 'unmapped_row_check', 'target': table})
    for table in sorted(set(mappings) - seen_tables):
        findings.append({'code': 'missing_row_check', 'target': table})
    return len(row_checks), totals


def evaluate_manifest(manifest_path: Path, strict_drops: bool, static_only: bool = False) -> dict:
    resolved = manifest_path.resolve()
    if not resolved.is_file():
        raise ValueError('manifest file not found')
    try:
        manifest = json.loads(resolved.read_text(encoding='utf-8'), object_pairs_hook=unique_members)
    except (OSError, UnicodeDecodeError, ValueError) as error:
        raise ValueError('unreadable or invalid manifest JSON') from error
    if not isinstance(manifest, dict):
        raise ValueError('manifest must be a JSON object')
    src_rev = require_non_empty_str(manifest.get('source_schema_revision'), 'source_schema_revision')
    tgt_rev = require_non_empty_str(manifest.get('target_schema_revision'), 'target_schema_revision')
    findings: list[dict] = []
    check_tables_and_columns(manifest, strict_drops, findings)
    if static_only:
        tables_checked = 0
        totals = {'source_rows': 0, 'target_rows': 0, 'named_drops': 0, 'folded_rows': 0}
    else:
        tables_checked, totals = check_row_checks(manifest, resolved.parent, strict_drops, findings)
    return {
        'schema': 'migration-reconciliation/v1',
        'status': 'pass' if not findings else 'fail',
        'source_schema_revision': src_rev,
        'target_schema_revision': tgt_rev,
        'tables_checked': tables_checked,
        'totals': totals,
        'findings': findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Reconcile migration manifests and per-key hash extracts.')
    parser.add_argument('manifest', type=Path, help='Path to reconciliation manifest JSON.')
    parser.add_argument('--strict-drops', action='store_true',
                        help='Reject vague one-word drop explanations on affected tables, columns, or rows.')
    parser.add_argument('--static-only', action='store_true',
                        help='Validate table, column, and drop mappings without running extract row checks.')
    args = parser.parse_args(argv)
    try:
        report = evaluate_manifest(args.manifest, args.strict_drops, args.static_only)
    except (OSError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not report['findings'] else 1


if __name__ == '__main__':
    sys.exit(main())
