# Database Backup Directory

This directory contains backups created by database maintenance scripts.

## Current Backups

- **Match Data Backups**: Created by `clean_historical_matches.py`
  - Format: `matches_backup_YYYYMMDD_HHMMSS.json`
  - Contains: Complete match data with metadata for rollback capability

## Rollback Procedures

### Match Cleanup Rollback
If you need to restore matches after running the cleanup script:

```bash
# Run the auto-generated rollback script
python scripts/database/rollback_match_cleanup.py
```

## Backup Retention

- Keep backups for at least 30 days after major operations
- Large backup files can be compressed: `gzip backup_file.json`
- Critical backups should be copied to external storage

## Manual Backup Commands

```bash
# Create manual match backup
uv run python scripts/database/backup_matches.py

# List all backups
ls -la scripts/database/backups/
```