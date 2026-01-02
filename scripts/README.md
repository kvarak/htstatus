# Scripts Directory

This directory contains utility scripts for development and maintenance tasks.

## Files

- **`apply_migrations.py`** - Apply database migrations programmatically
- **`changelog.sh`** - Generate changelog from git history (use `make changelog`)
- **`create_tables.py`** - Initialize database tables
- **`manage.py`** - Database management utilities
- **`test_db_connection.py`** - Test database connectivity
- **`run.sh`** - Development server startup script (deprecated, use `make dev`)

## Usage

Most scripts are integrated into the Makefile for easier use:

- `make changelog` instead of `./scripts/changelog.sh`
- `make dev` instead of `./scripts/run.sh`
- `make db-migrate` and `make db-upgrade` instead of direct script calls

## Direct Usage

If you need to run scripts directly:

```bash
# Run from project root
./scripts/script_name.py

# Or with UV for Python scripts
uv run ./scripts/script_name.py
```