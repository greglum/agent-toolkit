# Comment-Ban Ratchet Patterns

> **Observed:** 2026-11-20. Checked tool and rule scope: ESLint v9+ flat config
> (`context.sourceCode.getAllComments()`), Biome (no general comment-ban lint rule), and Ruff rule
> groups `ERA001`, `FIX`, `RUF100`, `TD`.
> **Recheck trigger:** Re-verify when adopting a new ESLint, Biome, or Ruff major version, or when
> `scripts/scanners.py` `DIRECTIVE_PREFIXES` changes.

A ratchet lets a repository ban new non-directive comments immediately without forcing a massive
upfront cleanup PR. Existing files keep a per-file ceiling that only moves downward until it
reaches zero.

## 1. Universal multi-language ratchet (bundled script)

Once the bundled `comment_audit.py` and `scanners.py` runner and `.comment-ratchet.json` are
authorized and initialized per the ratchet section in `SKILL.md`, run the check in CI or locally:

```sh
python3 scripts/comment_audit.py check --ratchet .comment-ratchet.json
```

Files omitted from `.comment-ratchet.json` have an implicit ceiling of `0`, so every newly created
code file is blocked from adding non-directive comments on day one.

## 2. ESLint (JavaScript and TypeScript)

ESLint has no built-in "ban all comments" rule, so combine `eslint-comments` controls (to require
reasons or forbid unused disables) with a lightweight local plugin rule or the bundled ratchet
script.

If you want a custom ESLint flat-config plugin that bans non-directive comments on new or cleaned
files while allowing overrides for legacy files:

```js
const DIRECTIVE_RE =
  /^\s*(?:eslint(?:-disable|-enable|\s)|(?:global|exported)\s|@ts-(?:ignore|expect-error|nocheck|check)|prettier-ignore|biome-ignore|oxlint-ignore|istanbul ignore|c8 ignore|v8 ignore|webpackChunkName|vite-ignore|@__PURE__|#__PURE__)/i;

export const noCommentsPlugin = {
  rules: {
    "no-non-directive-comments": {
      meta: { type: "suggestion", schema: [] },
      create(context) {
        return {
          Program() {
            for (const comment of context.sourceCode.getAllComments()) {
              if (comment.type === "Shebang") continue;
              if (DIRECTIVE_RE.test(comment.value)) continue;
              context.report({
                loc: comment.loc,
                message: "Remove non-directive comment or extract architectural rationale to docs/adr/.",
              });
            }
          },
        };
      },
    },
  },
};
```

Pair that plugin with a file-scoped `ignores` or override list generated from `.comment-ratchet.json`,
or run `comment_audit.py check --ratchet .comment-ratchet.json` directly alongside ESLint.

## 3. Biome (JavaScript and TypeScript)

Biome does not ship a general "forbid all comments" rule (`noUnusedTemplateLiteral` and formatting
rules do not flag comments). Keep Biome for formatting and lint checks, and run
`comment_audit.py check --ratchet .comment-ratchet.json` as the comment-ratchet gate right after
`npx biome check .`.

## 4. Python (Ruff + tokenizer ratchet)

Ruff catches commented-out code (`ERA001`), TODO/FIXME tags (`TD`, `FIX`), and suppression hygiene
(`RUF100`), while `comment_audit.py` uses Python's `tokenize` module so docstrings remain valid
and `#` comments are ratcheted per file:

```toml
[tool.ruff.lint]
extend-select = ["ERA001", "FIX", "RUF100", "TD"]
```

Run both in CI:

```sh
ruff check .
python3 scripts/comment_audit.py check --ratchet .comment-ratchet.json
```

## 5. Git pre-commit hook and GitHub Actions CI

### `.githooks/pre-commit` (or `.pre-commit-config.yaml`)

```sh
#!/bin/sh
set -eu
python3 scripts/comment_audit.py check --ratchet .comment-ratchet.json
```

For `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: comment-ratchet
        name: Check non-directive comment ratchet
        entry: python3 scripts/comment_audit.py check --ratchet .comment-ratchet.json
        language: system
        pass_filenames: false
```

### GitHub Actions workflow snippet

```yaml
- name: Comment ratchet check
  run: python3 scripts/comment_audit.py check --ratchet .comment-ratchet.json
```
