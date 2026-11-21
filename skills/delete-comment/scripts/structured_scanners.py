"""Comment scanners for YAML, TOML, SQL, and HCL/Terraform files."""

from __future__ import annotations

import re

from scanners import CommentHit, _block_metrics, is_directive

_YAML_BLOCK_RE = re.compile(r"^[|>](?:([+-])([1-9])?|([1-9])([+-])?)?$")
_SQL_DOLLAR_RE = re.compile(r"\$(?:[A-Za-z_][A-Za-z0-9_]*)?\$")
_HCL_HEREDOC_RE = re.compile(r"<<(-?)([A-Za-z_][A-Za-z0-9_-]*)[ \t]*(?=\r?\n|$)")


def _make_line_hit(
    rel_path: str, lines: list[str], line: int, col: int, raw: str, prefix_len: int
) -> CommentHit:
    before = lines[line - 1][:col] if line - 1 < len(lines) else ""
    inline = bool(before.strip())
    return CommentHit(
        file=rel_path,
        line=line,
        end_line=line,
        col=col,
        kind="line",
        inline=inline,
        standalone_lines=0 if inline else 1,
        text=raw,
        exempted=is_directive(raw[prefix_len:]),
    )


def _yaml_can_start_quote(raw_line: str, pos: int) -> bool:
    if pos == 0:
        return True
    if raw_line[pos - 1] not in (" ", "\t", ":", "[", "{", ",", "-", "?"):
        return False
    before = raw_line[:pos].rstrip(" \t")
    if not before or before[-1] in (":", "[", "{", ","):
        return True
    tokens = before.split()
    idx = len(tokens) - 1
    while idx >= 0 and (
        (tokens[idx].startswith("&") and len(tokens[idx]) > 1) or tokens[idx].startswith("!")
    ):
        idx -= 1
    if idx < 0 or tokens[idx].endswith(":"):
        return True
    return all(tok in ("-", "?") for tok in tokens[: idx + 1])


def _yaml_block_header(raw_line: str, comment_col: int | None) -> tuple[int, int | None] | None:
    code_part = raw_line if comment_col is None else raw_line[:comment_col]
    trimmed = code_part.rstrip(" \t")
    tokens = trimmed.split()
    if not tokens:
        return None
    match = _YAML_BLOCK_RE.fullmatch(tokens[-1])
    if match is None:
        return None
    prev_tokens = [tok for tok in tokens[:-1] if not tok.startswith(("&", "!"))]
    if prev_tokens and not (
        prev_tokens[-1].endswith(":") or prev_tokens[-1] in ("-", "?", "---")
    ):
        return None
    leading = len(raw_line) - len(raw_line.lstrip(" "))
    if not prev_tokens or prev_tokens == ["---"]:
        parent_indent = -1
    elif tokens[0] in ("-", "?") and len(prev_tokens) >= 2 and prev_tokens[-1].endswith(":"):
        parent_indent = code_part.find(prev_tokens[1], leading)
    elif tokens[0] in ("-", "?") and prev_tokens == [tokens[0]]:
        parent_indent = leading
    elif prev_tokens[-1] in ("-", "?"):
        parent_indent = code_part.rfind(prev_tokens[-1])
    else:
        parent_indent = leading
    digit_text = match.group(2) or match.group(3)
    if digit_text is None:
        return parent_indent, None
    digit = int(digit_text)
    return parent_indent, digit if parent_indent < 0 else parent_indent + digit


def scan_yaml(rel_path: str, text: str) -> list[CommentHit]:
    """Scan YAML files for # comments outside quoted and block scalars."""
    hits: list[CommentHit] = []
    raw_lines = text.split("\n")
    lines = [ln[:-1] if ln.endswith("\r") else ln for ln in raw_lines]
    quote_state: str | None = None
    block_active = False
    block_parent_indent = 0
    block_indent: int | None = None

    for line_no, raw_line in enumerate(lines, 1):
        if block_active:
            if raw_line.strip(" \t") == "":
                continue
            indent = len(raw_line) - len(raw_line.lstrip(" "))
            if block_parent_indent < 0 and (
                raw_line.startswith("---") or raw_line.startswith("...")
            ):
                block_active = False
            elif block_indent is not None:
                if indent >= block_indent:
                    continue
                block_active = False
            elif indent > block_parent_indent:
                block_indent = indent
                continue
            else:
                block_active = False

        comment_col: int | None = None
        i, n = 0, len(raw_line)
        while i < n:
            ch = raw_line[i]
            if quote_state == '"':
                if ch == "\\":
                    i += 2 if i + 1 < n else 1
                    continue
                if ch == '"':
                    quote_state = None
                i += 1
                continue
            if quote_state == "'":
                if ch == "'":
                    if i + 1 < n and raw_line[i + 1] == "'":
                        i += 2
                        continue
                    quote_state = None
                i += 1
                continue
            if ch in ('"', "'") and _yaml_can_start_quote(raw_line, i):
                quote_state = ch
                i += 1
                continue
            if ch == "#" and (i == 0 or raw_line[i - 1] in (" ", "\t")):
                comment_col = i
                raw = raw_line[i:]
                hits.append(_make_line_hit(rel_path, lines, line_no, i, raw, 1))
                break
            i += 1

        if quote_state is None:
            header = _yaml_block_header(raw_line, comment_col)
            if header is not None:
                block_active = True
                block_parent_indent, block_indent = header
    return hits


def _consume_toml_multiline(text: str, start: int, delim: str, escapes: bool) -> int:
    n, j = len(text), start
    while j < n:
        if escapes and text[j] == "\\" and j + 1 < n:
            j += 2
            continue
        if text[j : j + 3] == delim:
            q = 3
            while j + q < n and text[j + q] == delim[0] and q < 5:
                q += 1
            return j + q
        j += 1
    return n


def scan_toml(rel_path: str, text: str) -> list[CommentHit]:
    """Scan TOML files for # comments outside basic, literal, and multiline strings."""
    hits: list[CommentHit] = []
    lines = text.splitlines()
    n, i, line, line_start = len(text), 0, 1, 0

    def advance(target: int) -> None:
        nonlocal i, line, line_start
        chunk = text[i:target]
        nl = chunk.count("\n")
        if nl:
            line += nl
            line_start = text.rfind("\n", i, target) + 1
        i = target

    while i < n:
        ch = text[i]
        if ch == "\n":
            line += 1
            line_start = i + 1
            i += 1
            continue
        if text[i : i + 3] == '"""':
            advance(_consume_toml_multiline(text, i + 3, '"""', escapes=True))
            continue
        if text[i : i + 3] == "'''":
            advance(_consume_toml_multiline(text, i + 3, "'''", escapes=False))
            continue
        if ch == '"':
            j = i + 1
            while j < n and text[j] != "\n":
                if text[j] == "\\" and j + 1 < n and text[j + 1] != "\n":
                    j += 2
                    continue
                if text[j] == '"':
                    j += 1
                    break
                j += 1
            advance(j)
            continue
        if ch == "'":
            j = i + 1
            while j < n and text[j] != "\n":
                if text[j] == "'":
                    j += 1
                    break
                j += 1
            advance(j)
            continue
        if ch == "#":
            col = i - line_start
            end_idx = text.find("\n", i)
            end_idx = n if end_idx == -1 else end_idx
            raw = text[i:end_idx].rstrip("\r")
            hits.append(_make_line_hit(rel_path, lines, line, col, raw, 1))
            advance(end_idx)
            continue
        i += 1
    return hits


def _consume_doubled_quote(
    text: str, start: int, quote: str, backslash_escape: bool = False
) -> int:
    n, j = len(text), start
    while j < n:
        if backslash_escape and text[j] == "\\" and j + 1 < n:
            j += 2
            continue
        if text[j] == quote:
            if j + 1 < n and text[j + 1] == quote:
                j += 2
                continue
            return j + 1
        j += 1
    return n


def scan_sql(rel_path: str, text: str) -> list[CommentHit]:
    """Scan SQL files for -- line comments and /* */ block comments outside quoted forms."""
    hits: list[CommentHit] = []
    lines = text.splitlines()
    n, i, line, line_start = len(text), 0, 1, 0

    def advance(target: int) -> None:
        nonlocal i, line, line_start
        chunk = text[i:target]
        nl = chunk.count("\n")
        if nl:
            line += nl
            line_start = text.rfind("\n", i, target) + 1
        i = target

    while i < n:
        ch = text[i]
        if ch == "\n":
            line += 1
            line_start = i + 1
            i += 1
            continue
        if (
            ch in ("E", "e")
            and i + 1 < n
            and text[i + 1] == "'"
            and (i == 0 or not (text[i - 1].isalnum() or text[i - 1] in ("_", "$")))
        ):
            advance(_consume_doubled_quote(text, i + 2, "'", backslash_escape=True))
            continue
        if ch in ("'", '"', "`"):
            advance(_consume_doubled_quote(text, i + 1, ch))
            continue
        if ch == "$" and (i == 0 or not (text[i - 1].isalnum() or text[i - 1] in ("_", "$"))):
            match = _SQL_DOLLAR_RE.match(text, i)
            if match is not None:
                tag = match.group(0)
                end_pos = text.find(tag, i + len(tag))
                advance(n if end_pos == -1 else end_pos + len(tag))
                continue
        if text[i : i + 2] == "--":
            col = i - line_start
            end_idx = text.find("\n", i)
            end_idx = n if end_idx == -1 else end_idx
            raw = text[i:end_idx].rstrip("\r")
            hits.append(_make_line_hit(rel_path, lines, line, col, raw, 2))
            advance(end_idx)
            continue
        if text[i : i + 2] == "/*":
            sl, sc, depth, j = line, i - line_start, 1, i + 2
            while j < n and depth > 0:
                if text[j : j + 2] == "/*":
                    depth += 1
                    j += 2
                    continue
                if text[j : j + 2] == "*/":
                    depth -= 1
                    j += 2
                    continue
                j += 1
            raw = text[i:j]
            advance(j)
            inline, standalone = _block_metrics(lines, sl, sc, line, i - line_start)
            inner = raw[2:-2] if raw.endswith("*/") and len(raw) >= 4 else raw[2:]
            hits.append(CommentHit(rel_path, sl, line, sc, "block", inline, standalone, raw, is_directive(inner)))
            continue
        i += 1
    return hits


def _scan_hcl_string_tail(text: str, start: int, interp_stack: list[int]) -> int:
    n, j = len(text), start
    while j < n:
        if text[j] == "\\" and j + 1 < n:
            j += 2
            continue
        if text[j] == '"':
            return j + 1
        if text[j : j + 2] in ("$$", "%%") and j + 2 < n and text[j + 2] == "{":
            j += 2
            continue
        if text[j : j + 2] in ("${", "%{"):
            interp_stack.append(1)
            return j + 2
        j += 1
    return j


def _consume_hcl_heredoc(text: str, start: int, delim: str, indented: bool) -> int:
    n, j = len(text), start
    nl = text.find("\n", j)
    if nl == -1:
        return n
    j = nl + 1
    while j < n:
        end_idx = text.find("\n", j)
        raw_line = text[j:] if end_idx == -1 else text[j:end_idx]
        candidate = raw_line.rstrip("\r")
        if indented:
            candidate = candidate.lstrip(" \t")
        j = n if end_idx == -1 else end_idx + 1
        if candidate == delim:
            return j
    return n


def scan_hcl(rel_path: str, text: str) -> list[CommentHit]:
    """Scan HCL and Terraform files for #, //, and /* */ comments outside strings and heredocs."""
    hits: list[CommentHit] = []
    lines = text.splitlines()
    n, i, line, line_start = len(text), 0, 1, 0
    interp_stack: list[int] = []

    def advance(target: int) -> None:
        nonlocal i, line, line_start
        chunk = text[i:target]
        nl = chunk.count("\n")
        if nl:
            line += nl
            line_start = text.rfind("\n", i, target) + 1
        i = target

    while i < n:
        ch = text[i]
        if ch == "\n":
            line += 1
            line_start = i + 1
            i += 1
            continue
        if ch == '"':
            advance(_scan_hcl_string_tail(text, i + 1, interp_stack))
            continue
        if ch == "{" and interp_stack:
            interp_stack[-1] += 1
            i += 1
            continue
        if ch == "}" and interp_stack:
            interp_stack[-1] -= 1
            if interp_stack[-1] == 0:
                interp_stack.pop()
                advance(_scan_hcl_string_tail(text, i + 1, interp_stack))
                continue
            i += 1
            continue
        if ch == "<" and text[i : i + 2] == "<<":
            match = _HCL_HEREDOC_RE.match(text, i)
            if match is not None:
                advance(_consume_hcl_heredoc(text, match.end(), match.group(2), bool(match.group(1))))
                continue
        if ch == "#":
            col = i - line_start
            end_idx = text.find("\n", i)
            end_idx = n if end_idx == -1 else end_idx
            raw = text[i:end_idx].rstrip("\r")
            hits.append(_make_line_hit(rel_path, lines, line, col, raw, 1))
            advance(end_idx)
            continue
        if text[i : i + 2] == "//":
            col = i - line_start
            end_idx = text.find("\n", i)
            end_idx = n if end_idx == -1 else end_idx
            raw = text[i:end_idx].rstrip("\r")
            hits.append(_make_line_hit(rel_path, lines, line, col, raw, 2))
            advance(end_idx)
            continue
        if text[i : i + 2] == "/*":
            sl, sc, j = line, i - line_start, i + 2
            end_pos = text.find("*/", j)
            j = n if end_pos == -1 else end_pos + 2
            raw = text[i:j]
            advance(j)
            inline, standalone = _block_metrics(lines, sl, sc, line, i - line_start)
            inner = raw[2:-2] if raw.endswith("*/") and len(raw) >= 4 else raw[2:]
            hits.append(CommentHit(rel_path, sl, line, sc, "block", inline, standalone, raw, is_directive(inner)))
            continue
        i += 1
    return hits
