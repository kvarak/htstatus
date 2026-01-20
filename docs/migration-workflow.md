# Database Migration Workflow

## Overview

This document establishes the operational framework for safe database schema evolution in HTStatus 2.0. All migrations use Alembic with SQLAlchemy to manage schema changes across development, staging, and production environments.

**Critical Principle**: Database migrations must maintain backward compatibility with multiple deployed versions accessing the same database simultaneously.

---

## Alembic Best Practices

### Migration Structure

All migrations are located in `/migrations/versions/` with Alembic version control:

```
migrations/
├── alembic.ini          # Alembic configuration
├── env.py               # Alembic environment setup
├── script.py.mako       # Migration template
└── versions/            # Migration files
    ├── 00bc1ca5fec0_.py
    ├── 0bcca23528ce_.py
    └── [30 migration files total]
```

### Naming Conventions

Migrations follow Alembic's auto-generated naming: `<revision_id>_<description>.py`

When creating migrations manually:
```bash
uv run alembic revision --autogenerate -m "Description of change"
```

**Description Guidelines**:
- Be specific and concise (e.g., "add_user_email_column", "rename_player_skill_columns")
- Use lowercase with underscores
- Describe the change, not the reason

### Migration Components

Each migration file contains:

```python
"""Description of change."""

from alembic import op
import sqlalchemy as sa

revision = '<unique_id>'
down_revision = '<previous_id>'
branch_labels = None
depends_on = None

def upgrade():
    """Forward migration - apply changes."""
    # Schema modifications here
    pass

def downgrade():
    """Reverse migration - revert changes."""
    # Reverse operations here
    pass
```

---

## Pre-Migration Validation

### Development Environment Checklist

Before applying any migration:

**1. Schema Validation**
```bash
# Check current migration status
uv run alembic current

# Check heads
uv run alembic heads

# List all migrations
uv run alembic branches
```

**2. Migration Review**
- [ ] Read migration code line by line
- [ ] Verify `upgrade()` and `downgrade()` are symmetric
- [ ] Confirm no data loss from destructive operations
- [ ] Check for type compatibility changes
- [ ] Verify constraints and indices

**3. Database Integrity Check**
```bash
# Test migration on copy (manual procedure)
1. Create backup of development database
2. Apply migration to backup
3. Run test suite against migrated database
4. Verify all tests pass
5. Confirm data integrity
```

**4. Backward Compatibility Review**
- [ ] Does application code support both old and new schema?
- [ ] Are old columns preserved during transition?
- [ ] Do queries work against new schema?
- [ ] Can rollback proceed cleanly?

---

## Safe Migration Application

### Development Workflow

```bash
# 1. Verify migration status
uv run alembic current

# 2. Apply migration
uv run alembic upgrade head

# 3. Run test suite
uv run make test

# 4. Verify data integrity
uv run python scripts/validate_schema.py
```

### Staging Environment Procedure

```bash
# 1. Backup staging database (automated in deploy scripts)
# See: scripts/apply_migrations.py

# 2. Test migration with actual data
uv run python scripts/apply_migrations.py --environment staging --dry-run

# 3. Apply migration
uv run python scripts/apply_migrations.py --environment staging

# 4. Run comprehensive test suite
uv run make test-integration

# 5. Verify application functionality
# - Test all core workflows
# - Verify data consistency
# - Check performance impact
```

### Production Workflow

**Prerequisites**:
- [ ] Migration tested in staging with 100% success
- [ ] All tests passing in staging environment
- [ ] Rollback procedure verified and documented
- [ ] Database backup completed and verified
- [ ] Maintenance window scheduled if necessary
- [ ] Stakeholders notified of deployment

**Procedure**:
```bash
# 1. Create automated backup
# Scripts/apply_migrations.py handles this

# 2. Dry-run to verify
uv run python scripts/apply_migrations.py \
  --environment production \
  --dry-run \
  --verify

# 3. Apply migration
uv run python scripts/apply_migrations.py \
  --environment production \
  --backup-first \
  --verify-after

# 4. Monitor application
# - Watch error logs for 15 minutes
# - Verify user transactions processing
# - Monitor database performance
# - Check application response times
```

---

## Rollback Procedures

### Emergency Rollback (Under 30 Minutes)

If migration causes critical issues:

```bash
# 1. Immediate application pause (if needed)
# Contact operations team

# 2. Identify last working migration
uv run alembic current

# 3. Rollback one step
uv run alembic downgrade -1

# 4. Verify application recovery
# Monitor logs and application health

# 5. Investigate root cause
# Review migration code and logs
```

### Standard Rollback (Planned)

```bash
# 1. Backup current database state
# (for analysis)

# 2. Identify target migration
uv run alembic branches
uv run alembic log

# 3. Downgrade
uv run alembic downgrade <target_revision>

# 4. Verify schema integrity
uv run python scripts/validate_schema.py

# 5. Run test suite
uv run make test
```

### Rollback Verification Checklist

- [ ] Schema matches expected state
- [ ] All tables present with correct columns
- [ ] Data integrity verified
- [ ] Application starts successfully
- [ ] Core workflows functional
- [ ] No orphaned data remaining

---

## Post-Migration Verification

### Automated Checks

```bash
# Run comprehensive validation
uv run python scripts/validate_schema.py

# Check test coverage
uv run make test-coverage

# Verify migrations status
uv run alembic current
uv run alembic heads
```

### Manual Verification

**Data Integrity**:
```bash
# Connect to database and run checks
uv run python
```

```python
from models import db, Players, User, Match
session = db.session

# Verify key tables
print(f"Users: {session.query(User).count()}")
print(f"Players: {session.query(Players).count()}")
print(f"Matches: {session.query(Match).count()}")

# Check for orphaned records
# (specific queries based on migration changes)
```

**Application Testing**:
- [ ] Authentication workflow
- [ ] Player data display
- [ ] Training page loading
- [ ] Match history access
- [ ] Data update from CHPP
- [ ] Session management
- [ ] Export/download functions

---

## Multi-Version Compatibility

### Problem: Backward Compatibility

Multiple versions of HTStatus may be deployed simultaneously, all accessing the same database. Migrations must accommodate this.

**Solution Patterns**:

**1. Adding Columns**
```python
# Safe: New columns can be nullable
op.add_column('players',
    sa.Column('new_field', sa.String(255), nullable=True)
)
# Old application versions ignore new column
# New versions populate when needed
```

**2. Removing Columns**
```python
# Unsafe: Old versions still reference removed column
# Solution: Deprecate first (v1), remove later (v2)
# OR: Create view that provides backward compatibility
```

**3. Renaming Columns**
```python
# Solution: Create new column, migrate data, keep old for compatibility
# Then remove old in later migration
```

**4. Type Changes**
```python
# Verify new type is compatible with old
# Test thoroughly in staging
# Ensure application code handles both types during transition
```

### Migration Checklist for Compatibility

Before implementing any migration:

- [ ] Does not break old application versions
- [ ] Does not remove columns in current use
- [ ] Makes new columns optional (nullable)
- [ ] Preserves data types when possible
- [ ] Includes reversible downgrade path
- [ ] Tested with multiple code versions

---

## Monitoring and Rollback Readiness

### During Migration Execution

```
Monitor:
├── Database connection health
├── Query performance
├── Error logs for failures
├── Application response times
└── User transaction success rate
```

### After Successful Migration

```
Verify:
├── All tests passing
├── Application stability
├── Database performance metrics
├── Data consistency checks
└── No orphaned records
```

### Before Production Deployment

```
Checklist:
├── ✓ Migration tested in staging
├── ✓ All tests passing (100%)
├── ✓ Rollback procedure documented
├── ✓ Backup procedure verified
├── ✓ Team communication completed
├── ✓ Maintenance window (if needed) scheduled
└── ✓ Performance impact assessed
```

---

## Documentation and Tracking

### Migration Log

Each migration should have:
- **Purpose**: Why this change was needed
- **Impact**: What changes for users/applications
- **Risk Level**: Low (additive) / Medium (data-dependent) / High (breaking)
- **Rollback**: Simple / Complex / Requires manual intervention
- **Testing**: What was verified

Example header in migration file:
```python
"""Add email field to users table for notifications.

Impact: Users table gains email column (nullable).
Risk: Low - additive change, backward compatible.
Rollback: Simple - drop column.
Testing: Verified with 100 test users, data integrity checked.
"""
```

### Version Control

```bash
# Always commit migrations to version control
git add migrations/versions/<new_migration>.py
git commit -m "Add migration: <description>"

# Tag releases that include migrations
git tag -a v1.2.0 -m "Release with database schema changes"
```

---

## Troubleshooting

### Common Issues

**1. Migration Conflict**
```
Error: Can't locate revision identified by '<id>'

Solution:
- Verify migration file exists in versions/
- Check alembic.ini points to correct directory
- Run: uv run alembic upgrade head
```

**2. Foreign Key Constraint**
```
Error: (psycopg2.errors.ForeignKeyViolation)

Solution:
- Verify no orphaned records
- Check migration order (dependencies)
- Review foreign key constraints in migration
```

**3. Type Mismatch**
```
Error: Column type doesn't match expected

Solution:
- Review downgrade() function
- Ensure type conversion is explicit
- Test with sample data
```

### Recovery Procedures

See "Rollback Procedures" section above for detailed recovery steps.

---

## Summary

Safe database migrations require:

1. **Planning**: Understand change impact and compatibility
2. **Testing**: Verify in development, then staging
3. **Documentation**: Record purpose and procedures
4. **Execution**: Follow proven procedures with monitoring
5. **Verification**: Confirm integrity and rollback readiness

Maintain this documentation as migration patterns evolve.
