# Git documentation sources and recheck triggers

Read this reference only when verifying Git documentation citations or recheck triggers.

Observed November 5, 2026 (rechecked November 20, 2026):

- [Git attributes filter documentation](https://git-scm.com/docs/gitattributes#_filter),
  Git project living docs: explains clean/smudge/process filters that `git status` and diff
  operations can execute on tracked paths. Used to skip filter-backed status checks in
  `scripts/inventory.py` rather than executing untrusted repo filter commands.
- [Git status submodule options](https://git-scm.com/docs/git-status#Documentation/git-status.txt---ignore-submodulesltwhengt),
  Git project living docs: `--ignore-submodules=dirty` prevents descending into child Git
  configurations while keeping gitlink changes visible.
- [Git count-objects](https://git-scm.com/docs/git-count-objects), Git project living docs:
  documents `alternate:` lines and unavailable-path diagnostics (including exit-zero
  warnings) used by `scripts/inventory.py` object-storage checks.
- [Git clone shared-object risks](https://git-scm.com/docs/git-clone), Git project living
  docs: documents `--shared` / `--reference` object-store borrowing risks when deleting or
  repacking lender repositories.

Reuse notice: Living documentation pages; prose reuse rights not assessed and no upstream
text copied. Recheck on Git upgrades affecting `worktree`, `count-objects`, `check-attr`,
or `status` behavior, or if an inventory trial uncovers a missed edge case.
