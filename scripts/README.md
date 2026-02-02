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

## Quality Intelligence & Testing

### coverage_report.py
Generates detailed coverage analysis with actionable testing recommendations.

```bash
# Basic usage (via Makefile - preferred)
make coverage-report                  # Detailed analysis with recommendations
make coverage-json                    # JSON output for automation

# Direct usage
uv run python scripts/coverage_report.py          # Default: top 10 files
uv run python scripts/coverage_report.py -l 15   # Show top 15 files
uv run python scripts/coverage_report.py --json  # JSON output
```

**Features**:
- Identifies highest-impact files for test coverage improvement
- Categorizes files by type (blueprints, utils, models, CHPP)
- Provides specific recommendations for reaching coverage targets
- Calculates impact scores (low coverage × high line count = high priority)
- Integrates with Quality Intelligence reporting pipeline

### count_tasks_by_priority.py
Analyzes the project backlog and counts tasks by priority level.

```bash
uv run python scripts/count_tasks_by_priority.py                 # Summary view
uv run python scripts/count_tasks_by_priority.py --detailed      # Detailed breakdown with task IDs
uv run python scripts/count_tasks_by_priority.py --line          # One-line format for backlog.md updates
uv run python scripts/count_tasks_by_priority.py --summary-only  # Just the counts
```

Use this when creating new backlog tasks to ensure sequential numbering.
