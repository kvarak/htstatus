# HattrickPlanner Backlog

**Mindset**: Hobby project. Good enough is perfect. Only fix what actually bothers us (bugs, risk to the database, slowness we notice, code that's painful to change). No audits, no coverage-chasing, no process for its own sake.
**Scope**: Improvements, bug fixes, cleanup and infra. New features go in [features.md](features.md).
**Rule**: Pick whatever is most useful. When done, DELETE the line (and any `tasks/` file); Git history is the archive. Delete items that stop making sense, too.
**Task IDs**: `./scripts/get-next-task-id.sh <TYPE>` (BUG, REFACTOR, TEST, INFRA, UI, DOC). Estimates are optional.

---

## P1: Broken or risky 🔥

*Nothing right now*

## P2: Worth doing 🎯

*Nothing right now*

## P3: When you're in that code anyway 🔧

- **[INFRA-088]** Trim tooling and docs - Makefile targets, quality-intelligence scripts and 60+ doc files are more than a hobby project needs. Delete what nobody uses when it gets in the way (was REFACTOR-049, DOC-032, REFACTOR-101, REFACTOR-028 changelog, REFACTOR-052..056) → [Details](tasks/INFRA-088.md)

---

**Testing**: Add a test when fixing a bug or changing behaviour. No coverage targets beyond what CI already enforces (50%).
