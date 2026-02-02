# Development Scripts

**Usage**: Most scripts are integrated into the Makefile:
- `make dev` - Start development server
- `make changelog` - Generate changelog
- `./restore_production_backup.sh --help` - Backup/restore options
- `make db-migrate` and `make db-upgrade` instead of direct script calls

## Direct Usage

If you need to run scripts directly:

```bash
# Run from project root
./scripts/script_name.py

# Or with UV for Python scripts
uv run ./scripts/script_name.py
```

## Task Management

### get-next-task-id.sh
Generates the next sequential task ID for a given task type by analyzing git history.

```bash
./scripts/get-next-task-id.sh FEAT    # Returns next FEAT task ID
./scripts/get-next-task-id.sh DOC     # Returns next DOC task ID
./scripts/get-next-task-id.sh TEST    # Returns next TEST task ID
```

### count_tasks_by_priority.py
Analyzes the project backlog and counts tasks by priority level.

```bash
uv run python scripts/count_tasks_by_priority.py                 # Summary view
uv run python scripts/count_tasks_by_priority.py --detailed      # Detailed breakdown with task IDs
uv run python scripts/count_tasks_by_priority.py --line          # One-line format for backlog.md updates
uv run python scripts/count_tasks_by_priority.py --summary-only  # Just the counts
```

Use this when creating new backlog tasks to ensure sequential numbering.
