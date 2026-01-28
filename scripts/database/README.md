# Database Scripts

This directory contains **only the working** database automation scripts for HTStatus development.

## Core Scripts (All Tested & Working)

### Migration Management

**`apply_migrations.py`** - Apply database migrations ✅
```bash
# Apply migrations directly (bypasses Flask startup issues)
uv run python scripts/database/apply_migrations.py
```

**`upgrade_local_database.sh`** - Full database upgrade automation ✅
```bash
# Preview what would be upgraded
./scripts/database/upgrade_local_database.sh --dry-run

# Upgrade with backup
./scripts/database/upgrade_local_database.sh --backup

# Non-interactive upgrade
./scripts/database/upgrade_local_database.sh --force
```

**Creating New Migrations** - Use Alembic directly ✅
```bash
# Create new migration with automatic model detection
uv run alembic -c migrations/alembic.ini revision --autogenerate -m "Migration description"

# Create empty migration for manual changes
uv run alembic -c migrations/alembic.ini revision -m "Manual changes"

# Use make command (calls alembic internally)
make db-migrate MESSAGE="Migration description"
```

### Database Administration

**`restore_production_backup.sh`** - Restore database from production backup ✅
```bash
# Restore with automatic backup validation
./scripts/database/restore_production_backup.sh
```

**`test_db_connection.py`** - Test database connectivity ✅
```bash
# Validate database connection and configuration
uv run python scripts/database/test_db_connection.py
```

## Recommended Workflow

### Development Migration Creation
1. Make model changes in `models.py`
2. Create migration: `make db-migrate MESSAGE="Description"`
3. Review generated migration in `migrations/versions/`
4. Apply migration: `make db-upgrade` or use upgrade script

### Database Maintenance
1. Check status: `./scripts/database/upgrade_local_database.sh --dry-run`
2. Upgrade safely: `./scripts/database/upgrade_local_database.sh --backup`
3. Test connection: `uv run python scripts/database/test_db_connection.py`

### Production Backup Integration
1. Backup current: (automatically done by upgrade script)
2. Restore from prod: `./scripts/database/restore_production_backup.sh`
3. Upgrade to latest: `./scripts/database/upgrade_local_database.sh`

## Script Dependencies

All scripts require:
- UV-managed Python environment (use `uv run python`)
- Proper `.env` configuration with database credentials
- Running Docker services (`make dev` for development)

## Integration Points

- **Makefile**: `make db-migrate`, `make db-upgrade`
- **Docker**: Uses `htplanner_postgres` container
- **Environment**: Loads configuration from `.env`
- **Migration Chain**: Manages Alembic migration dependencies

## Troubleshooting

- **Migration Chain Errors**: Use `upgrade_local_database.sh` to fix broken chains
- **Connection Issues**: Run `test_db_connection.py` for diagnostics
- **Flask Context Issues**: All scripts bypass Flask startup problems
- **Backup/Restore**: Scripts include automatic validation and rollback

---

**Note**: This directory previously contained legacy scripts with Flask context issues. All non-working scripts have been removed to maintain a clean, reliable toolkit.