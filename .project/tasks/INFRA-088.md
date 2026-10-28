# INFRA-088: Trim tooling and docs

The repo has more machinery than a hobby project needs: several docker-compose files, many Makefile targets and quality-intelligence scripts, a JSON-based changelog generator, and 60+ docs.

**Approach:** whenever something gets in the way or confuses you, delete or merge it. Candidates:
- Merge the docker-compose files in `configs/` if one is enough.
- Remove Makefile targets/scripts nobody runs (the quality-intelligence JSON reporting, coverage report script).
- Fold overlapping docs together; keep README, TECHNICAL, DEPLOYMENT and `docs/chpp/`.

There's no deadline and no checklist; small bites are fine.
