# Database Management Scripts

This directory contains database backup, restoration, and maintenance scripts for HattrickPlanner.

## Backup System (INFRA-033)

- **Full Database Backups**: Created by `backup_database.py` (INFRA-033)
  - Format: `htstatus_full_backup_YYYYMMDD_HHMMSS.sql`
  - Contains: Complete PostgreSQL database dump with schema and data
  - Purpose: Complete database protection and disaster recovery

- **Match Data Backups**: Created by `backup_matches.py` (legacy)
  - Format: `matches_backup_YYYYMMDD_HHMMSS.json`
  - Contains: Complete match data with metadata for rollback capability

## Backup Commands (Make Targets)

```bash
# Create full database backup
make db-backup

# Restore database from backup
make db-restore BACKUP_FILE="path/to/backup.sql"

# Run automated backup to kloker.local (production)
make db-backup-auto
```

## Direct Script Usage

```bash
# Create full database backup
uv run python scripts/database/backup_database.py [--output-dir PATH]

# Restore database from backup
uv run python scripts/database/restore_database.py BACKUP_FILE [--target-db TARGET]

# Automated backup to kloker.local (requires SSH setup)
./scripts/database/backup_to_kloker.sh
```

## Automated Backup System (Production)

### glader.local Setup

For production deployment on glader.local with automated backups to kloker.local:

1. **SSH Key Setup** (one-time):
```bash
# On glader.local, create SSH key if not exists
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_backup -N ""

# Copy public key to kloker.local
ssh-copy-id -i ~/.ssh/id_ed25519_backup.pub user@kloker.local

# Test connection
ssh kloker.local "mkdir -p ~/backup/htstatus"
```

2. **Cron Schedule** (recommended):
```bash
# Edit crontab on glader.local
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/htstatus-2.0 && ./scripts/database/backup_to_kloker.sh >> /var/log/htstatus-backup.log 2>&1
```

3. **Deployment Integration**:
The deployment script automatically creates backups before updates.

### kloker.local Backup Storage

kloker.local maintains automated backup retention with smart monthly archival:

1. **Storage Location**: `~/backup/[project]/` (e.g., `~/backup/htstatus/`, `~/backup/htplanner/`)

2. **Retention Policy** (automated via `trim-archive.sh`):
   - **Recent backups**: Keep all files newer than 1 month
   - **Archive period**: For files older than 1 month, keep only the newest backup per month
   - **Cleanup schedule**: Runs daily at 4 AM via cron

3. **Manual Operations**:
```bash
# List backups on kloker.local
ssh kloker.local "ls -la ~/backup/htstatus/"

# Run retention cleanup manually
ssh kloker.local "/home/kvarak/backup/trim-archive.sh"

# Download backup from kloker.local
scp kloker.local:~/backup/htstatus/backup_YYYYMMDD_HHMMSS.sql ./
```

## Rollback Procedures

### Full Database Restore
```bash
# List available backups on kloker.local
ssh kloker.local "ls -la ~/backup/htstatus/"

# Download backup from kloker.local
scp kloker.local:~/backup/htstatus/htstatus_full_backup_YYYYMMDD_HHMMSS.sql ./

# Restore (WARNING: This will overwrite existing data!)
make db-restore BACKUP_FILE="htstatus_full_backup_YYYYMMDD_HHMMSS.sql"
```

### Match Cleanup Rollback (Legacy)
If you need to restore matches after running the cleanup script:

```bash
# Run the auto-generated rollback script
python scripts/database/rollback_match_cleanup.py
```

## Security Notes

- Database backups contain sensitive user data
- kloker.local backups should be on encrypted storage
- SSH keys for automation should be dedicated (not personal keys)
- Regular backup integrity testing recommended

## Manual Backup Commands (Legacy)

```bash
# Create manual match backup
uv run python scripts/database/backup_matches.py

# List all backups
ls -la scripts/database/backups/
```
