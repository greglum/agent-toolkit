# Post-run skill refinement protocol

Use this workflow after running any catalog skill against real codebases when the run reveals cross-project tool friction, stack assumptions, missing failure checks, or wording ambiguity. Keep extraction centralized here rather than duplicating refinement checklists across every skill bundle.

## Six-step capture loop

1. **Collect concrete run evidence**: Record the invoked skill, target stack (framework, build system, OS), commands or scripts run, and the specific friction, false positive, missed bug, or blind spot. Skip routine clean runs that surfaced no reusable gap.
2. **Separate local vs portable lessons**:
   - Keep repository-specific paths, build flags, and project preferences in the destination repo's `AGENTS.md`, `docs/`, or local scripts.
   - Promote a lesson into the catalog skill only when it holds across unrelated repositories in the same class (or corrects a general defect in the skill).
3. **Choose the narrowest target layer**:
   - **`SKILL.md`**: Update only when the operational sequence, scope boundary, fallback rule, or trigger description (`<= 360` chars automatic, `<= 600` chars explicit) misrouted or stalled the agent.
   - **`references/`**: Put stack-specific traps, versioned flags, and environment limits into a dated reference with `Observed:` date and recheck trigger.
   - **`scripts/` + `test_*.py`**: Encode deterministic parser, path, or hygiene fixes in the bundled script paired with a planted-defect unit test that fails on the bug.
4. **Sanitize for public/catalog portability**: Strip repository names, host home paths (write `~` if needed), emails, internal hosts, and raw transcripts. Keep `description`, `compatibility`, and file sizes within catalog limits (`sh scripts/verify.sh` and global pre-commit caps).
5. **Respect authority and installation boundaries**: Never modify global installed skills without task authority. After authorized edits in the skills repository, run:
   - `sh scripts/verify.sh` (catalog metadata, links, comment ban, unit and planted-defect suites)
   - `python3 skills/harden-skill/scripts/inspect_skill.py skills/<name> --profile auto`
6. **Close behavioral validation honestly**: When description triggers or core execution behavior changed meaningfully, recommend an explicit `/harden-skill skills/<name>` (Claude Code) or `$harden-skill skills/<name>` (Codex) trial. Report unverified live trigger selection separately from static checks and fixture tests.

## Five-field post-run lesson record

```yaml
skill: <catalog-skill-name>
stack: <language / framework / build tool / OS>
evidence: <command, error, missed check, or path friction observed>
portability: <why this applies beyond one repository, or why it stays repo-local>
target_layer: <SKILL.md | references/<file>.md | scripts/<tool>.py + planted-defect test>
```
