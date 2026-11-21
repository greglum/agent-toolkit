"""Multi-language source comment scanners and directive exemptions."""

from __future__ import annotations

import ast
import io
import tokenize
import warnings
from dataclasses import dataclass
from pathlib import Path

PYTHON_SUFFIXES = {".py", ".pyi"}
SHELL_SUFFIXES = {".sh", ".bash", ".zsh", ".ksh"}
JS_TS_SUFFIXES = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts"}
GO_SUFFIXES = {".go"}
RUST_SUFFIXES = {".rs"}
C_JAVA_SUFFIXES = {".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hh", ".java"}
DIRECTIVE_PREFIXES = (
    "noqa", "type: ignore", "pragma: no cover", "pragma: no branch", "ruff:", "pylint:",
    "mypy:", "pyright:", "fmt: off", "fmt: on", "fmt: skip", "isort:", "bandit:", "nosec",
    "coverage:", "shellcheck", "-*-", "coding:", "coding=", "eslint-disable", "eslint-enable",
    "eslint ", "global ", "exported ", "@ts-ignore", "@ts-expect-error", "@ts-nocheck",
    "@ts-check", "prettier-ignore", "biome-ignore", "oxlint-ignore", "istanbul ignore",
    "c8 ignore", "v8 ignore", "webpackchunkname", "vite-ignore", "@__pure__", "#__pure__",
    "go:generate", "go:embed", "go:build", "go:noinline", "go:linkname", "+build ", "nolint",
    "clippy::", "rustfmt::skip", "clang-format off", "clang-format on", "noinspection",
)
REGEX_PRECEDING_KEYWORDS = {
    "return", "case", "throw", "typeof", "void", "delete", "await", "yield",
    "in", "of", "else", "do", "new",
}
REGEX_PRECEDING_CHARS = set("([,{:;=!?&|^~+-%<}")


@dataclass
class CommentHit:
    file: str
    line: int
    end_line: int
    col: int
    kind: str
    inline: bool
    standalone_lines: int
    text: str
    exempted: bool


class ScanError(Exception):
    """Raised when a source file cannot be read or parsed."""


def is_directive(body: str) -> bool:
    """Return True when stripped comment body starts with a recognized tool directive."""
    lowered = body.lstrip().lower()
    return any(lowered.startswith(prefix) for prefix in DIRECTIVE_PREFIXES)


def detect_language(path: Path, first_line: str) -> str | None:
    """Map file extension or line-1 shebang to a supported scanner family."""
    suffix = path.suffix.lower()
    if suffix in PYTHON_SUFFIXES:
        return "python"
    if suffix in SHELL_SUFFIXES:
        return "shell"
    if suffix in JS_TS_SUFFIXES:
        return "js"
    if suffix in GO_SUFFIXES:
        return "go"
    if suffix in RUST_SUFFIXES:
        return "rust"
    if suffix in C_JAVA_SUFFIXES:
        return "c"
    if suffix == "" and first_line.startswith("#!"):
        head = first_line.lower()
        if "python" in head:
            return "python"
        if any(sh in head for sh in ("/sh", " sh", "bash", "zsh", "ksh")):
            return "shell"
        if any(rt in head for rt in ("node", "deno", "bun")):
            return "js"
    return None


def scan_python(rel_path: str, text: str) -> list[CommentHit]:
    """Extract Python comments with tokenize so docstrings and strings stay exempt."""
    hits: list[CommentHit] = []
    lines = text.splitlines()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            ast.parse(text, filename=rel_path)
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
        for tok in tokens:
            if tok.type != tokenize.COMMENT:
                continue
            start_line, start_col = tok.start
            end_line, _ = tok.end
            raw = tok.string
            shebang = start_line == 1 and start_col == 0 and raw.startswith("#!")
            exempted = shebang or is_directive(raw[1:])
            before = lines[start_line - 1][:start_col] if start_line - 1 < len(lines) else ""
            inline = bool(before.strip())
            hits.append(
                CommentHit(
                    file=rel_path,
                    line=start_line,
                    end_line=end_line,
                    col=start_col,
                    kind="line",
                    inline=inline,
                    standalone_lines=0 if inline else 1,
                    text=raw,
                    exempted=exempted,
                )
            )
    except (tokenize.TokenError, IndentationError, SyntaxError) as exc:
        raise ScanError(f"{rel_path}: {exc}") from exc
    return hits


def _parse_heredoc_delimiter(text: str, pos: int) -> tuple[str, bool, int] | None:
    n = len(text)
    strip_tabs = False
    if pos < n and text[pos] == "-":
        strip_tabs = True
        pos += 1
    while pos < n and text[pos] in " \t":
        pos += 1
    if pos >= n or text[pos] in "\r\n;|&()#<>":
        return None
    parts: list[str] = []
    has_quote = False
    while pos < n:
        ch = text[pos]
        if ch in " \t\r\n;|&()<>":
            break
        if ch == "'":
            has_quote = True
            pos += 1
            while pos < n and text[pos] != "'":
                if text[pos] == "\n":
                    return None
                parts.append(text[pos])
                pos += 1
            if pos >= n:
                return None
            pos += 1
            continue
        if ch == '"':
            has_quote = True
            pos += 1
            while pos < n and text[pos] != '"':
                if text[pos] == "\n":
                    return None
                if text[pos] == "\\" and pos + 1 < n and text[pos + 1] in ('"', "\\", "$", "`"):
                    parts.append(text[pos + 1])
                    pos += 2
                else:
                    parts.append(text[pos])
                    pos += 1
            if pos >= n:
                return None
            pos += 1
            continue
        if ch == "\\" and pos + 1 < n:
            if text[pos + 1] != "\n":
                parts.append(text[pos + 1])
            pos += 2
            continue
        parts.append(ch)
        pos += 1
    if not parts and not has_quote:
        return None
    return "".join(parts), strip_tabs, pos


def _consume_heredocs(
    text: str, start: int, line: int, queue: list[tuple[str, bool]]
) -> tuple[int, int, int]:
    n, i, line_start = len(text), start, start
    for delim, strip_tabs in queue:
        while i < n:
            end_idx = text.find("\n", i)
            raw_line = text[i:] if end_idx == -1 else text[i:end_idx]
            candidate = raw_line.rstrip("\r")
            if strip_tabs:
                candidate = candidate.lstrip("\t")
            if end_idx == -1:
                i = n
                break
            i = end_idx + 1
            line += 1
            line_start = i
            if candidate == delim:
                break
        if i >= n:
            break
    return i, line, line_start


def scan_shell(rel_path: str, text: str) -> list[CommentHit]:
    """Scan shell scripts for # comments outside quotes, heredocs, and parameter expansions."""
    hits: list[CommentHit] = []
    lines = text.splitlines()
    n, i, line, line_start, state = len(text), 0, 1, 0, "normal"
    heredoc_queue: list[tuple[str, bool]] = []
    scopes: list[str] = []

    while i < n:
        ch = text[i]
        if ch == "\n":
            line += 1
            line_start = i + 1
            i += 1
            if state == "normal" and heredoc_queue:
                i, line, line_start = _consume_heredocs(text, i, line, heredoc_queue)
                heredoc_queue.clear()
            continue
        if state == "single":
            if ch == "'":
                state = "normal"
            i += 1
            continue
        if state in ("ansi", "double"):
            if ch == "\\" and i + 1 < n:
                if text[i + 1] == "\n":
                    line += 1
                    line_start = i + 2
                i += 2
                continue
            if (state == "ansi" and ch == "'") or (state == "double" and ch == '"'):
                state = "normal"
            i += 1
            continue
        if ch == "\\" and i + 1 < n:
            if text[i + 1] == "\n":
                line += 1
                line_start = i + 2
            i += 2
            continue
        if text[i : i + 3] == "$((":
            scopes.append("arith")
            i += 3
            continue
        if text[i : i + 2] == "$(":
            scopes.append("cmd")
            i += 2
            continue
        if text[i : i + 2] == "${":
            scopes.append("param")
            i += 2
            continue
        if ch == "{" and scopes and scopes[-1] in ("param", "param_b"):
            scopes.append("param_b")
            i += 1
            continue
        if ch == "}" and scopes and scopes[-1] in ("param", "param_b"):
            scopes.pop()
            i += 1
            continue
        if ch == "(" and scopes and scopes[-1] in ("arith", "arith_p", "cmd", "cmd_p"):
            scopes.append("arith_p" if scopes[-1].startswith("arith") else "cmd_p")
            i += 1
            continue
        if ch == ")" and scopes:
            if scopes[-1] == "arith" and text[i : i + 2] == "))":
                scopes.pop()
                i += 2
                continue
            if scopes[-1] in ("arith_p", "cmd", "cmd_p"):
                scopes.pop()
                i += 1
                continue
        if text[i : i + 2] == "$'":
            state = "ansi"
            i += 2
            continue
        if ch == "'":
            state = "single"
            i += 1
            continue
        if ch == '"':
            state = "double"
            i += 1
            continue
        if text[i : i + 3] == "<<<":
            i += 3
            continue
        if text[i : i + 2] == "<<" and not (scopes and scopes[-1] in ("param", "param_b", "arith", "arith_p")):
            parsed = _parse_heredoc_delimiter(text, i + 2)
            if parsed is not None:
                delim, strip_tabs, next_i = parsed
                heredoc_queue.append((delim, strip_tabs))
                i = next_i
                continue
            i += 2
            continue
        if ch == "#" and not (scopes and scopes[-1] in ("param", "param_b", "arith", "arith_p")):
            prev = text[i - 1] if i > 0 else "\n"
            is_param = text[max(0, i - 1) : i + 1] == "$#" or text[max(0, i - 2) : i + 1] == "${#"
            if (i == 0 or prev in " \t\r\n;|&(){}") and not is_param:
                col = i - line_start
                end_idx = text.find("\n", i)
                end_idx = n if end_idx == -1 else end_idx
                raw = text[i:end_idx]
                shebang = line == 1 and col == 0 and raw.startswith("#!")
                before = lines[line - 1][:col] if line - 1 < len(lines) else ""
                inline = bool(before.strip())
                hits.append(
                    CommentHit(
                        file=rel_path,
                        line=line,
                        end_line=line,
                        col=col,
                        kind="line",
                        inline=inline,
                        standalone_lines=0 if inline else 1,
                        text=raw,
                        exempted=shebang or is_directive(raw[1:]),
                    )
                )
                i = end_idx
                continue
        i += 1
    return hits


def _block_metrics(lines: list[str], sl: int, sc: int, el: int, ec: int) -> tuple[bool, int]:
    before = bool((lines[sl - 1][:sc] if sl - 1 < len(lines) else "").strip())
    after = bool((lines[el - 1][ec:] if el - 1 < len(lines) else "").strip())
    inline = before or after
    if sl == el:
        return inline, 0 if inline else 1
    return inline, (0 if before else 1) + max(0, el - sl - 1) + (0 if after else 1)


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


def scan_file(path: Path, rel_path: str) -> list[CommentHit]:
    """Scan a supported source file and return all detected comment hits."""
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        raise ScanError(f"{rel_path}: {exc}") from exc
    if b"\x00" in raw_bytes[:8192]:
        return []
    text = raw_bytes.decode("utf-8", errors="replace")
    first_line = text.splitlines()[0] if text else ""
    lang = detect_language(path, first_line)
    if lang is None:
        return []
    if lang == "python":
        return scan_python(rel_path, text)
    if lang == "shell":
        return scan_shell(rel_path, text)
    return scan_c_like(rel_path, text, lang)
