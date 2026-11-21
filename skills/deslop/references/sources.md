# Sources and Vale notes

Read this only when reviewing upstream provenance or Vale rule configuration.

## Upstream tell-list provenance

Observed **2026-10-28** (initial capture in `THIRD_PARTY_NOTICES.md`; `blader/humanizer` checked at `0ef9fe5bc3572734fd3ae6c448fe00a30cd5dcf0` on 2026-10-28, unchanged from 3.0.0 patterns).

| Source | Revision / Locator | License | Role and local departure |
| --- | --- | --- | --- |
| [blader/humanizer](https://github.com/blader/humanizer) | 3.0.0 (`9862685f575c65a8247f90369951df1b3416e3d6`); checked `0ef9fe5bc3572734fd3ae6c448fe00a30cd5dcf0` | MIT, Copyright (c) 2025 Siqi Chen | Tell categories and five-survivor check; `scripts/tells.sh` keeps only short regex patterns in POSIX ERE and omits persona/chat workflow. |
| [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop) | `000650b156983f5159695b441477f4e63b25dc85` | MIT, Copyright (c) 2026 Peter Yang | Audit vs edit mode split and preservation guardrails; rewritten in original local steps without external file dependencies. |
| [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) | Revision not recorded at initial capture | MIT, Copyright (c) 2025 Hardik Pandya | Stock phrase patterns in `scripts/tells.sh`; rejects unvalidated self-score thresholds. |
| [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) | Mutable encyclopedia page | CC BY-SA 4.0 | Origin of humanizer's tell taxonomy; only short keywords and stock phrases appear as search patterns, with zero article prose. |

Recheck trigger: recheck pinned commits and licenses before adding new tell lists or changing `scripts/tells.sh` pattern groups.

## Vale configuration notes

Observed **2026-11-20** against `vale/.vale.ini`.

- Enabled styles: `write-good`, `proselint`, and `Readability` (`write-good.E-Prime` is off because direct plain prose prefers `is`, `are`, and `has`; spelling is off because technical writing contains product and code identifiers).
- Readability grades are advisory for technical writing.
- `scripts/lint.sh` syncs styles into `${XDG_CACHE_HOME:-~/.cache}/deslop/vale` only when `--sync` is passed after confirming network download authority.

Recheck trigger: recheck `vale/.vale.ini` and `scripts/lint.sh` when upgrading Vale or changing configured style packages.
