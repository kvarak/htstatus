# Scripts Directory

This directory contains utility scripts for development and maintenance tasks.

## Files

- **`apply_migrations.py`** - Apply database migrations programmatically
- **`changelog.sh`** - Generate changelog from git history (use `make changelog`)
- **`create_tables.py`** - Initialize database tables
- **`manage.py`** - Database management utilities
- **`restore_production_backup.sh`** - Backup and restore production database to development environment
- **`run.sh`** - Development server startup script (deprecated, use `make dev`)

### Database Utilities (`database/`)
- **`test_db_connection.py`** - Test database connectivity with diagnostics

### Production Backup & Restore
- **`restore_production_backup.sh`** - Complete production database backup and restore workflow
  - Creates fresh backup from glader.local production database
  - Stores backup on kloker.local for archival
  - Restores backup to local development environment
  - Supports backup-only, restore-only, and cleanup modes
  - Use `--help` for detailed options and usage examples

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
