"""C-like (JS/TS, Go, Rust, C/C++/Java) source comment scanner."""

from __future__ import annotations

from scanners import CommentHit, _block_metrics, is_directive

REGEX_PRECEDING_KEYWORDS = {
    "return", "case", "throw", "typeof", "void", "delete", "await", "yield",
    "in", "of", "else", "do", "new",
}
REGEX_PRECEDING_CHARS = set("([,{:;=!?&|^~+-%<}")


def _rust_raw_hashes(text: str, idx: int) -> tuple[int, int] | None:
    pos = idx + 1 if text[idx] == "b" else idx
    if pos >= len(text) or text[pos] != "r":
        return None
    pos += 1
    hashes = 0
    while pos < len(text) and text[pos] == "#":
        hashes += 1
        pos += 1
    return (hashes, pos + 1) if pos < len(text) and text[pos] == '"' else None


def _rust_char_end(text: str, idx: int) -> int | None:
    n = len(text)
    if idx + 1 >= n:
        return None
    if text[idx + 1] == "\\":
        j = idx + 2
        while j < n and text[j] not in "\n\r'" and j - idx <= 16:
            j += 1
        return j + 1 if j < n and text[j] == "'" else None
    if text[idx + 1] not in "\n\r'" and idx + 2 < n and text[idx + 2] == "'":
        return idx + 3
    return None


def _scan_template_tail(text: str, start: int, stack: list[int]) -> int:
    n, j = len(text), start
    while j < n:
        if text[j] == "\\" and j + 1 < n:
            j += 2
            continue
        if text[j] == "`":
            return j + 1
        if text[j : j + 2] == "${":
            stack.append(1)
            return j + 2
        j += 1
    return j


def scan_c_like(rel_path: str, text: str, lang: str) -> list[CommentHit]:
    """Scan JS/TS, Go, Rust, or C/C++/Java code for // and /* */ comments."""
    hits: list[CommentHit] = []
    lines = text.splitlines()
    n, i, line, line_start = len(text), 0, 1, 0
    can_start_regex = True
    tpl_stack: list[int] = []

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
        if ch in " \t\r":
            i += 1
            continue
        if lang == "rust" and ch in ("r", "b") and (i == 0 or not (text[i - 1].isalnum() or text[i - 1] == "_")):
            raw_info = _rust_raw_hashes(text, i)
            if raw_info is not None:
                hashes, start_body = raw_info
                closing = '"' + ("#" * hashes)
                end_pos = text.find(closing, start_body)
                advance(n if end_pos == -1 else end_pos + len(closing))
                can_start_regex = False
                continue
        if lang == "rust" and ch == "'":
            char_end = _rust_char_end(text, i)
            if char_end is not None:
                advance(char_end)
            else:
                i += 1
            can_start_regex = False
            continue
        if ch in ('"', "'"):
            j = i + 1
            closed = False
            while j < n:
                if text[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                if text[j] == ch:
                    j += 1
                    closed = True
                    break
                if text[j] == "\n":
                    break
                j += 1
            advance(j if closed else i + 1)
            can_start_regex = False
            continue
        if ch == "`" and lang in ("js", "go"):
            if lang == "go":
                end_pos = text.find("`", i + 1)
                advance(n if end_pos == -1 else end_pos + 1)
                can_start_regex = False
                continue
            advance(_scan_template_tail(text, i + 1, tpl_stack))
            can_start_regex = bool(tpl_stack)
            continue
        if ch == "{" and tpl_stack:
            tpl_stack[-1] += 1
            i += 1
            can_start_regex = True
            continue
        if ch == "}" and tpl_stack:
            tpl_stack[-1] -= 1
            if tpl_stack[-1] == 0:
                tpl_stack.pop()
                advance(_scan_template_tail(text, i + 1, tpl_stack))
                can_start_regex = bool(tpl_stack)
                continue
            i += 1
            can_start_regex = False
            continue
        if text[i : i + 2] == "//":
            col = i - line_start
            end_idx = text.find("\n", i)
            end_idx = n if end_idx == -1 else end_idx
            raw = text[i:end_idx]
            before = lines[line - 1][:col] if line - 1 < len(lines) else ""
            inline = bool(before.strip())
            hits.append(
                CommentHit(rel_path, line, line, col, "line", inline, 0 if inline else 1, raw, is_directive(raw[2:]))
            )
            advance(end_idx)
            continue
        if text[i : i + 2] == "/*":
            sl, sc, depth, j = line, i - line_start, 1, i + 2
            while j < n and depth > 0:
                if lang == "rust" and text[j : j + 2] == "/*":
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
        if text[i : i + 2] == "</" or text[i : i + 2] == "=>":
            can_start_regex = text[i : i + 2] == "=>"
            i += 2
            continue
        if text[i : i + 2] in ("++", "--"):
            can_start_regex = False
            i += 2
            continue
        if lang == "js" and ch == "/" and can_start_regex:
            j, in_class, closed = i + 1, False, False
            while j < n and text[j] != "\n":
                if text[j] == "\\" and j + 1 < n and text[j + 1] != "\n":
                    j += 2
                    continue
                if text[j] == "[":
                    in_class = True
                elif text[j] == "]" and in_class:
                    in_class = False
                elif text[j] == "/" and not in_class:
                    j += 1
                    while j < n and text[j].isalpha():
                        j += 1
                    closed = True
                    break
                j += 1
            if closed:
                advance(j)
                can_start_regex = False
                continue
        if ch.isalpha() or ch in ("_", "$"):
            j = i + 1
            while j < n and (text[j].isalnum() or text[j] in ("_", "$")):
                j += 1
            can_start_regex = text[i:j] in REGEX_PRECEDING_KEYWORDS
            i = j
            continue
        if ch.isdigit():
            j = i + 1
            while j < n:
                if text[j].isalnum() or text[j] in (".", "_"):
                    j += 1
                elif lang == "c" and text[j] == "'" and j + 1 < n and text[j + 1].isalnum():
                    j += 2
                else:
                    break
            can_start_regex = False
            i = j
            continue
        can_start_regex = ch in REGEX_PRECEDING_CHARS
        i += 1
    return hits
