#!/bin/bash

# HattrickPlanner Production Database Backup & Restore Script
#
# Purpose: Automate the process of creating a fresh backup from production (glader.local),
#          storing it on kloker.local, and restoring it to the local development database.
#
# Usage: ./scripts/restore_production_backup.sh [options]
# Options:
#   --backup-only    Only create and transfer backup, don't restore locally
#   --restore-only   Only restore from existing backup (skips backup creation)
#   --cleanup        Remove temporary files after successful restore
#   --help          Show this help message
#
# Prerequisites:
# - SSH access to glader.local and kloker.local without password prompts
# - PostgreSQL running locally in Docker (htplanner_postgres container)
# - Production database 'htplanner' running on glader.local
# - Backup directory ~/backup/htplanner/ exists on kloker.local

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Load environment variables from .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

# Configuration from environment variables
PROD_SERVER="${DEPLOY_SERVER:-glader.local}"
BACKUP_SERVER="${BACKUP_SERVER:-kloker.local}"
PROD_DB="${POSTGRES_DB:-htplanner}"
PROD_USER="${DEPLOY_USER:-kvarak}"
LOCAL_DB="${POSTGRES_DB:-htplanner}"
LOCAL_USER="${POSTGRES_USER:-htstatus}"
CONTAINER_NAME="${POSTGRES_CONTAINER:-htplanner_postgres}"

# Backup paths
REMOTE_BACKUP_DIR="/tmp"
STORAGE_BACKUP_DIR="~/backup/htplanner"
LOCAL_BACKUP_DIR="$HOME/backup"

# Generate timestamp for backup filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILENAME="htplanner_backup_${TIMESTAMP}.sql"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

show_help() {
    cat << EOF
HattrickPlanner Production Database Backup & Restore Script

USAGE:
    ./scripts/restore_production_backup.sh [options]

OPTIONS:
    --backup-only     Only create and transfer backup, don't restore locally
    --restore-only    Only restore from existing backup (skips backup creation)
    --cleanup         Remove temporary files after successful restore
    --help           Show this help message

DESCRIPTION:
    This script automates the process of backing up the production database
    from glader.local, storing it on kloker.local, and restoring it to your
    local development environment.

PREREQUISITES:
    - SSH access to glader.local and kloker.local
    - Docker container 'htplanner_postgres' running locally
    - Production database 'htplanner' on glader.local
    - Backup directory structure on kloker.local

EXAMPLES:
    # Full backup and restore process
    ./scripts/restore_production_backup.sh

    # Only create backup, don't restore locally
    ./scripts/restore_production_backup.sh --backup-only

    # Restore from most recent backup without creating new one
    ./scripts/restore_production_backup.sh --restore-only

EOF
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if Docker container is running
    if ! docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        log_error "Docker container '${CONTAINER_NAME}' is not running"
        log_info "Please start it with: make dev"
        exit 1
    fi

    # Check SSH connectivity
    if ! ssh -o BatchMode=yes -o ConnectTimeout=5 "$PROD_SERVER" true 2>/dev/null; then
        log_error "Cannot connect to $PROD_SERVER via SSH"
        exit 1
    fi

    if ! ssh -o BatchMode=yes -o ConnectTimeout=5 "$BACKUP_SERVER" true 2>/dev/null; then
        log_error "Cannot connect to $BACKUP_SERVER via SSH"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

create_production_backup() {
    log_info "Creating fresh backup of production database on $PROD_SERVER..."

    # Create backup on production server
    ssh "$PROD_SERVER" "sudo -u $PROD_USER pg_dump $PROD_DB > $REMOTE_BACKUP_DIR/$BACKUP_FILENAME"

    # Check if backup was created successfully
    BACKUP_SIZE=$(ssh "$PROD_SERVER" "ls -la $REMOTE_BACKUP_DIR/$BACKUP_FILENAME | awk '{print \$5}'")
    if [ "$BACKUP_SIZE" -eq 0 ] 2>/dev/null; then
        log_error "Backup creation failed - backup file is empty"
        exit 1
    fi

    log_success "Production backup created: $BACKUP_FILENAME (${BACKUP_SIZE} bytes)"
}

transfer_backup_to_storage() {
    log_info "Transferring backup to storage server ($BACKUP_SERVER)..."

    # Ensure backup directory exists on storage server
    ssh "$BACKUP_SERVER" "mkdir -p $STORAGE_BACKUP_DIR"

    # Transfer backup from production to storage
    ssh "$PROD_SERVER" "cat $REMOTE_BACKUP_DIR/$BACKUP_FILENAME" | \
        ssh "$BACKUP_SERVER" "cat > $STORAGE_BACKUP_DIR/$BACKUP_FILENAME"

    # Verify transfer
    STORAGE_SIZE=$(ssh "$BACKUP_SERVER" "ls -la $STORAGE_BACKUP_DIR/$BACKUP_FILENAME | awk '{print \$5}'")
    if [ "$BACKUP_SIZE" != "$STORAGE_SIZE" ]; then
        log_error "Backup transfer verification failed - size mismatch"
        log_error "Original: $BACKUP_SIZE bytes, Transferred: $STORAGE_SIZE bytes"
        exit 1
    fi

    log_success "Backup transferred to storage server"

    # Clean up temporary backup on production server
    ssh "$PROD_SERVER" "rm -f $REMOTE_BACKUP_DIR/$BACKUP_FILENAME"
    log_info "Temporary backup cleaned up from production server"
}

download_backup_locally() {
    log_info "Downloading backup to local machine..."

    # Create local backup directory
    mkdir -p "$LOCAL_BACKUP_DIR"

    # Download backup from storage server
    scp "$BACKUP_SERVER:$STORAGE_BACKUP_DIR/$BACKUP_FILENAME" "$LOCAL_BACKUP_DIR/"

    log_success "Backup downloaded to $LOCAL_BACKUP_DIR/$BACKUP_FILENAME"
}

restore_local_database() {
    log_info "Restoring backup to local development database..."

    # Get current database statistics for comparison
    OLD_PLAYER_COUNT=$(docker exec "$CONTAINER_NAME" psql -U "$LOCAL_USER" -d "$LOCAL_DB" -t -c "SELECT COUNT(*) FROM players;" 2>/dev/null | tr -d ' ' || echo "0")

    log_info "Current player count: $OLD_PLAYER_COUNT"

    # Drop and recreate database
    log_info "Dropping and recreating database..."
    docker exec "$CONTAINER_NAME" psql -U "$LOCAL_USER" -d postgres -c "DROP DATABASE IF EXISTS $LOCAL_DB;"
    docker exec "$CONTAINER_NAME" psql -U "$LOCAL_USER" -d postgres -c "CREATE DATABASE $LOCAL_DB OWNER $LOCAL_USER;"

    # Restore from backup (ignore ownership errors - they're expected)
    log_info "Restoring data from backup..."
    docker exec -i "$CONTAINER_NAME" psql -U "$LOCAL_USER" -d "$LOCAL_DB" < "$LOCAL_BACKUP_DIR/$BACKUP_FILENAME" 2>/dev/null || true

    # Verify restoration
    NEW_PLAYER_COUNT=$(docker exec "$CONTAINER_NAME" psql -U "$LOCAL_USER" -d "$LOCAL_DB" -t -c "SELECT COUNT(*) FROM players;" | tr -d ' ')
    MIGRATION_VERSION=$(docker exec "$CONTAINER_NAME" psql -U "$LOCAL_USER" -d "$LOCAL_DB" -t -c "SELECT version_num FROM alembic_version;" | tr -d ' ')

    log_success "Database restoration completed!"
    log_success "Player count: $OLD_PLAYER_COUNT → $NEW_PLAYER_COUNT"
    log_success "Migration version: $MIGRATION_VERSION"

    if [ "$NEW_PLAYER_COUNT" -eq 0 ]; then
        log_warning "No players found in restored database - this might indicate a problem"
    fi
}

cleanup_temp_files() {
    log_info "Cleaning up temporary files..."

    if [ -f "$LOCAL_BACKUP_DIR/$BACKUP_FILENAME" ]; then
        rm -f "$LOCAL_BACKUP_DIR/$BACKUP_FILENAME"
        log_success "Local backup file removed"
    fi
}

find_latest_backup() {
    log_info "Finding latest backup on storage server..."

    # Get the most recent backup filename
    BACKUP_FILENAME=$(ssh "$BACKUP_SERVER" "ls -1t $STORAGE_BACKUP_DIR/htplanner_backup_*.sql 2>/dev/null | head -1 | xargs basename" 2>/dev/null || echo "")

    if [ -z "$BACKUP_FILENAME" ]; then
        log_error "No backup files found on storage server"
        exit 1
    fi

    log_success "Using latest backup: $BACKUP_FILENAME"
}

# Main script logic
main() {
    local backup_only=false
    local restore_only=false
    local cleanup=false

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backup-only)
                backup_only=true
                shift
                ;;
            --restore-only)
                restore_only=true
                shift
                ;;
            --cleanup)
                cleanup=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done

    # Validate mutually exclusive options
    if [ "$backup_only" = true ] && [ "$restore_only" = true ]; then
        log_error "Cannot use --backup-only and --restore-only together"
        exit 1
    fi

    log_info "Starting HattrickPlanner database backup and restore process..."

    check_prerequisites

    if [ "$restore_only" = false ]; then
        create_production_backup
        transfer_backup_to_storage
    else
        find_latest_backup
    fi

    if [ "$backup_only" = false ]; then
        download_backup_locally
        restore_local_database

        if [ "$cleanup" = true ]; then
            cleanup_temp_files
        fi
    fi

    log_success "Process completed successfully!"

    if [ "$backup_only" = false ]; then
        echo ""
        log_info "Your development database has been restored with production data."
        log_info "You can now start your development server with: make dev"
    fi
}

# Run main function with all arguments
main "$@"
