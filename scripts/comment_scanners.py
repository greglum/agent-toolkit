"""Language-specific comment scanners and directive exemptions."""

from __future__ import annotations

from dataclasses import dataclass
import io
from pathlib import Path
import tokenize

CODE_SUFFIXES = {".py", ".sh", ".js", ".ts", ".mjs", ".cjs"}
SPECIAL_FILES = {".githooks/pre-commit"}
JS_SUFFIXES = {".js", ".ts", ".mjs", ".cjs"}

HASH_DIRECTIVES = (
    "noqa", "type: ignore", "pragma: no cover", "ruff:", "pylint:", "mypy:",
    "pyright:", "fmt:", "isort:", "shellcheck", "-*-", "coding:",
)
SLASH_DIRECTIVES = ("eslint-disable", "@ts-", "prettier-ignore", "biome-ignore")
BLOCK_DIRECTIVES = ("eslint-disable", "istanbul ignore", "c8 ignore", "v8 ignore")

REGEX_PREFIX_KEYWORDS = {
    "await", "case", "default", "delete", "do", "else", "export", "extends",
    "in", "instanceof", "new", "of", "return", "throw", "typeof", "void", "yield",
}
REGEX_PREFIX_OPS = set("([{:;,?=!~&|^+-*/%<>")
SH_BOUNDARY_CHARS = set(" \t\r\n;|&(){}<>")


@dataclass(frozen=True)
class CommentFinding:
    """A single comment found in a source file."""

    line: int
    end_line: int
    col: int
    text: str
    standalone_lines: int
    is_inline: bool
    exempt: bool


def file_kind(rel_path: str) -> str | None:
    """Return the scanner kind for a code file, or None when unsupported."""
    if rel_path in SPECIAL_FILES:
        return "sh"
    suffix = Path(rel_path).suffix
    if suffix == ".py":
        return "py"
    if suffix == ".sh":
        return "sh"
    if suffix in JS_SUFFIXES:
        return "js"
    return None


def _matches_directive(body: str, prefixes: tuple[str, ...]) -> bool:
    for prefix in prefixes:
        if prefix.endswith((":", "-")):
            if body.startswith(prefix):
                return True
        elif body == prefix:
            return True
        elif body.startswith(prefix):
            next_char = body[len(prefix)]
            if not (next_char.isalnum() or next_char == "_"):
                return True
    return False


def is_exempt_comment(text: str, line: int, kind: str) -> bool:
    """Return True when a comment is a line-1 shebang or an allowed tool directive."""
    if kind in ("py", "sh") and line == 1 and text.startswith("#!"):
        return True
    if kind in ("py", "sh"):
        return _matches_directive(text[1:].lstrip(), HASH_DIRECTIVES)
    if text.startswith("//"):
        return _matches_directive(text[2:].lstrip(), SLASH_DIRECTIVES)
    if text.startswith("/*"):
        body = text[2:-2] if text.endswith("*/") else text[2:]
        return _matches_directive(body.strip(), BLOCK_DIRECTIVES)
    return False


def _line_offsets(text: str) -> list[int]:
    offsets = [0]
    for idx, ch in enumerate(text):
        if ch == "\n":
            offsets.append(idx + 1)
    return offsets


def _pos_to_line_col(offsets: list[int], pos: int) -> tuple[int, int]:
    lo, hi = 0, len(offsets) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if offsets[mid] <= pos:
            lo = mid + 1
        else:
            hi = mid - 1
    return hi + 1, pos - offsets[hi]


def _single_line_layout(lines: list[str], line: int, col: int, end_col: int | None = None) -> tuple[int, bool]:
    line_text = lines[line - 1]
    before_blank = line_text[:col].strip() == ""
    after_blank = True if end_col is None else line_text[end_col:].strip() == ""
    return (1, False) if (before_blank and after_blank) else (0, True)


def _block_layout(lines: list[str], start_line: int, start_col: int, end_line: int, end_col: int) -> tuple[int, bool]:
    if end_line > len(lines):
        end_line = len(lines)
        end_col = len(lines[-1]) if lines else 0
    if start_line == end_line:
        return _single_line_layout(lines, start_line, start_col, end_col)
    first_blank = lines[start_line - 1][:start_col].strip() == ""
    last_blank = lines[end_line - 1][end_col:].strip() == ""
    standalone = max(0, end_line - start_line - 1) + int(first_blank) + int(last_blank)
    return standalone, not (first_blank and last_blank)


def scan_python(text: str) -> list[CommentFinding]:
    """Extract Python comments using tokenize so docstrings and strings are ignored."""
    lines = text.splitlines()
    findings: list[CommentFinding] = []
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if tok.type != tokenize.COMMENT:
            continue
        line, col = tok.start
        standalone_lines, is_inline = _single_line_layout(lines, line, col)
        findings.append(CommentFinding(
            line, line, col, tok.string, standalone_lines, is_inline, is_exempt_comment(tok.string, line, "py"),
        ))
    return findings


def scan_shell(text: str) -> list[CommentFinding]:
    """Extract POSIX/Bash comments outside quotes and parameter expansions."""
    lines = text.splitlines()
    offsets = _line_offsets(text)
    findings: list[CommentFinding] = []
    n = len(text)
    i = 0
    state = "normal"
    param_depth = 0
    param_quote_stack: list[str] = []

    while i < n:
        ch = text[i]
        if state == "single":
            if ch == "'":
                state = param_quote_stack.pop() if param_quote_stack else "normal"
            i += 1
            continue
        if state == "ansi_single":
            if ch == "\\" and i + 1 < n:
                i += 2
                continue
            if ch == "'":
                state = param_quote_stack.pop() if param_quote_stack else "normal"
            i += 1
            continue
        if state == "double":
            if ch == "\\" and i + 1 < n:
                i += 2
                continue
            if text.startswith("${", i):
                param_depth += 1
                param_quote_stack.append("double")
                state = "normal"
                i += 2
                continue
            if ch == '"':
                state = param_quote_stack.pop() if param_quote_stack else "normal"
            i += 1
            continue

        if ch == "\\" and i + 1 < n:
            i += 2
            continue
        if text.startswith("$'", i):
            if param_depth > 0:
                param_quote_stack.append("normal")
            state = "ansi_single"
            i += 2
            continue
        if text.startswith("${", i):
            param_depth += 1
            param_quote_stack.append("normal")
            i += 2
            continue
        if param_depth > 0 and ch == "}":
            param_depth -= 1
            state = param_quote_stack.pop() if param_quote_stack else "normal"
            i += 1
            continue
        if ch in ("'", '"'):
            if param_depth > 0:
                param_quote_stack.append("normal")
            state = "single" if ch == "'" else "double"
            i += 1
            continue
        if ch == "#" and param_depth == 0:
            prev = text[i - 1] if i > 0 else "\n"
            if prev in SH_BOUNDARY_CHARS:
                end = text.find("\n", i)
                if end == -1:
                    end = n
                comment_text = text[i:end]
                line, col = _pos_to_line_col(offsets, i)
                standalone_lines, is_inline = _single_line_layout(lines, line, col)
                findings.append(CommentFinding(
                    line, line, col, comment_text, standalone_lines, is_inline, is_exempt_comment(comment_text, line, "sh"),
                ))
                i = end
                continue
        i += 1
    return findings


def _scan_js_quoted(text: str, start: int, quote: str) -> int:
    n = len(text)
    i = start + 1
    while i < n:
        ch = text[i]
        if ch == "\\" and i + 1 < n:
            i += 2
            continue
        if ch == quote or ch == "\n":
            return i + 1
        i += 1
    return n


def _try_scan_js_regex(text: str, start: int) -> int | None:
    n = len(text)
    i = start + 1
    in_class = False
    while i < n:
        ch = text[i]
        if ch in ("\n", "\r"):
            return None
        if ch == "\\":
            if i + 1 < n and text[i + 1] not in ("\n", "\r"):
                i += 2
                continue
            return None
        if ch == "[" and not in_class:
            in_class = True
        elif ch == "]" and in_class:
            in_class = False
        elif ch == "/" and not in_class:
            i += 1
            while i < n and text[i].isalpha():
                i += 1
            return i
        i += 1
    return None


def scan_js(text: str) -> list[CommentFinding]:
    """Extract // and /* */ comments outside strings, template literals, and regex literals."""
    lines = text.splitlines()
    offsets = _line_offsets(text)
    findings: list[CommentFinding] = []
    n = len(text)
    i = 0
    mode_stack: list[tuple[str, int]] = []
    can_start_regex = True

    while i < n:
        if mode_stack and mode_stack[-1][0] == "template":
            ch = text[i]
            if ch == "\\" and i + 1 < n:
                i += 2
            elif text.startswith("${", i):
                mode_stack.append(("expr", 1))
                can_start_regex = True
                i += 2
            elif ch == "`":
                mode_stack.pop()
                can_start_regex = False
                i += 1
            else:
                i += 1
            continue

        ch = text[i]
        if ch in (" ", "\t", "\r", "\n", "\f", "\v"):
            i += 1
            continue

        if text.startswith("//", i):
            end = text.find("\n", i)
            if end == -1:
                end = n
            comment_text = text[i:end]
            line, col = _pos_to_line_col(offsets, i)
            standalone_lines, is_inline = _single_line_layout(lines, line, col)
            findings.append(CommentFinding(
                line, line, col, comment_text, standalone_lines, is_inline, is_exempt_comment(comment_text, line, "js"),
            ))
            i = end
            continue

        if text.startswith("/*", i):
            close_idx = text.find("*/", i + 2)
            end = n if close_idx == -1 else close_idx + 2
            comment_text = text[i:end]
            start_line, start_col = _pos_to_line_col(offsets, i)
            end_line, end_col = _pos_to_line_col(offsets, end)
            standalone_lines, is_inline = _block_layout(lines, start_line, start_col, end_line, end_col)
            findings.append(CommentFinding(
                start_line, end_line, start_col, comment_text, standalone_lines, is_inline, is_exempt_comment(comment_text, start_line, "js"),
            ))
            i = end
            continue

        if ch in ("'", '"'):
            i = _scan_js_quoted(text, i, ch)
            can_start_regex = False
            continue
        if ch == "`":
            mode_stack.append(("template", 0))
            i += 1
            continue
        if ch == "/" and can_start_regex:
            regex_end = _try_scan_js_regex(text, i)
            if regex_end is not None:
                i = regex_end
                can_start_regex = False
                continue

        if mode_stack and mode_stack[-1][0] == "expr" and ch in ("{", "}"):
            kind, depth = mode_stack[-1]
            if ch == "{":
                mode_stack[-1] = (kind, depth + 1)
                can_start_regex = True
            elif depth == 1:
                mode_stack.pop()
            else:
                mode_stack[-1] = (kind, depth - 1)
                can_start_regex = True
            i += 1
            continue

        if text.startswith("++", i) or text.startswith("--", i):
            can_start_regex = False
            i += 2
        elif text.startswith("=>", i):
            can_start_regex = True
            i += 2
        elif ch.isalpha() or ch in ("_", "$"):
            end = i + 1
            while end < n and (text[end].isalnum() or text[end] in ("_", "$")):
                end += 1
            can_start_regex = text[i:end] in REGEX_PREFIX_KEYWORDS
            i = end
        elif ch.isdigit():
            end = i + 1
            while end < n and (text[end].isalnum() or text[end] in (".", "_")):
                end += 1
            can_start_regex = False
            i = end
        else:
            if ch in REGEX_PREFIX_OPS:
                can_start_regex = True
            elif ch in (")", "]", "}"):
                can_start_regex = False
            i += 1

    return findings


def scan_text(text: str, kind: str) -> list[CommentFinding]:
    """Scan source text for comments using the language-appropriate scanner."""
    if kind == "py":
        return scan_python(text)
    if kind == "sh":
        return scan_shell(text)
    if kind == "js":
        return scan_js(text)
    raise ValueError(f"Unsupported scanner kind: {kind}")
