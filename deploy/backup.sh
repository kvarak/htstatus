#!/bin/sh
# Database backup: pg_dump of the db container into backups/, and optionally a
# copy on another host over ssh (BACKUP_REMOTE in .env). Run nightly from
# cron, and by update.sh before a new image starts.
set -e
cd "$(dirname "$0")"
umask 077

# Read one setting from .env (without sourcing it: values may contain shell characters)
setting() { sed -n "s/^$1=//p" .env | tail -n 1; }
keep_days=$(setting BACKUP_KEEP_DAYS)
remote=$(setting BACKUP_REMOTE)
remote_dir=$(setting BACKUP_REMOTE_DIR)
remote_keep_days=$(setting BACKUP_REMOTE_KEEP_DAYS)

mkdir -p backups
file="backups/htplanner_$(date +%Y-%m-%d_%H%M).sql.gz"
docker compose exec -T db pg_dump -U htplanner -d htplanner --no-owner | gzip > "$file.tmp"
mv "$file.tmp" "$file"
find backups -name "htplanner_*.sql.gz" -mtime +"${keep_days:-14}" -delete

if [ -n "$remote" ]; then
    remote_dir=${remote_dir:-backup/htplanner}
    ssh -o BatchMode=yes "$remote" "mkdir -p $remote_dir"
    scp -q "$file" "$remote:$remote_dir/"
    ssh -o BatchMode=yes "$remote" "find $remote_dir -name 'htplanner_*.sql.gz' -mtime +${remote_keep_days:-30} -delete"
fi
echo "$(date +'%F %T') backup ok: $file${remote:+ (copied to $remote)}"
