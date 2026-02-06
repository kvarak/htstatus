#!/bin/bash
#
# Automated Database Backup to kloker.local
# Part of INFRA-033: Database Protection Enhancement
#
# Purpose: Creates daily database backups and transfers them to kloker.local
# Usage: Deploy this script on glader.local and run via cron
# Schedule: Recommended daily at 2 AM: 0 2 * * * /path/to/backup_to_kloker.sh
#
# Prerequisites:
# - SSH key authentication set up between glader.local and kloker.local
# - ~/backup/htstatus/ directory exists on kloker.local
# - HattrickPlanner application deployed on glader.local
#
# Author: HTStatus Development Team
# Created: February 6, 2026 (INFRA-033 Database Protection)

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
BACKUP_HOST="kloker.local"
BACKUP_REMOTE_DIR="~/backup/htstatus"
LOCAL_BACKUP_DIR="$PROJECT_ROOT/scripts/database/backups"
LOG_FILE="/var/log/htstatus-backup.log"
RETENTION_DAYS=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] [INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] [SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] [WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR]${NC} $1" | tee -a "$LOG_FILE" >&2
}

# Error handling
cleanup_on_error() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_error "Script failed with exit code $exit_code"
        # Clean up any partial backup files if they exist
        if [ -n "${BACKUP_FILE:-}" ] && [ -f "$BACKUP_FILE" ]; then
            log_info "Cleaning up partial backup file: $BACKUP_FILE"
            rm -f "$BACKUP_FILE"
        fi
    fi
    exit $exit_code
}

trap cleanup_on_error EXIT

# Main backup function
create_and_transfer_backup() {
    log_info "=== Starting automated database backup ==="

    # Change to project directory
    cd "$PROJECT_ROOT"

    # Check if project is properly set up
    if [ ! -f ".env" ]; then
        log_error "Project .env file not found. Please ensure HattrickPlanner is properly deployed."
        return 1
    fi

    if [ ! -f "scripts/database/backup_database.py" ]; then
        log_error "Database backup script not found. Please ensure INFRA-033 is deployed."
        return 1
    fi

    # Create local backup
    log_info "Creating database backup..."

    if ! BACKUP_OUTPUT=$(uv run python scripts/database/backup_database.py --output-dir "$LOCAL_BACKUP_DIR" 2>&1); then
        log_error "Failed to create database backup"
        log_error "Backup output: $BACKUP_OUTPUT"
        return 1
    fi

    # Extract backup file path from output
    BACKUP_FILE=$(echo "$BACKUP_OUTPUT" | grep "Backup created successfully:" | sed 's/.*Backup created successfully: //' | tr -d ' ')

    if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
        log_error "Could not determine backup file path or file does not exist"
        log_error "Backup output: $BACKUP_OUTPUT"
        return 1
    fi

    BACKUP_FILENAME=$(basename "$BACKUP_FILE")
    BACKUP_SIZE=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE" 2>/dev/null)

    log_success "Local backup created: $BACKUP_FILE"
    log_info "Backup size: $((BACKUP_SIZE / 1024 / 1024)) MB"

    # Test SSH connection to kloker.local
    log_info "Testing connection to $BACKUP_HOST..."
    if ! ssh -o ConnectTimeout=10 -o BatchMode=yes "$BACKUP_HOST" "echo 'Connection test successful'" >/dev/null 2>&1; then
        log_error "Cannot connect to $BACKUP_HOST via SSH"
        log_error "Please ensure SSH key authentication is set up"
        return 1
    fi

    # Create remote backup directory if it doesn't exist
    log_info "Ensuring remote backup directory exists..."
    if ! ssh "$BACKUP_HOST" "mkdir -p $BACKUP_REMOTE_DIR"; then
        log_error "Failed to create remote backup directory: $BACKUP_REMOTE_DIR"
        return 1
    fi

    # Transfer backup to kloker.local
    log_info "Transferring backup to $BACKUP_HOST:$BACKUP_REMOTE_DIR/"
    if ! scp "$BACKUP_FILE" "$BACKUP_HOST:$BACKUP_REMOTE_DIR/"; then
        log_error "Failed to transfer backup to $BACKUP_HOST"
        return 1
    fi

    # Verify remote backup
    REMOTE_SIZE=$(ssh "$BACKUP_HOST" "stat -c%s '$BACKUP_REMOTE_DIR/$BACKUP_FILENAME' 2>/dev/null || echo 0")
    if [ "$REMOTE_SIZE" -ne "$BACKUP_SIZE" ]; then
        log_error "Remote backup size mismatch. Local: $BACKUP_SIZE, Remote: $REMOTE_SIZE"
        return 1
    fi

    log_success "Backup transferred successfully to $BACKUP_HOST"
    log_info "Remote file: $BACKUP_HOST:$BACKUP_REMOTE_DIR/$BACKUP_FILENAME"
    log_info "Remote size: $((REMOTE_SIZE / 1024 / 1024)) MB"

    # Clean up local backup (keep remote copy only)
    log_info "Cleaning up local backup file..."
    rm -f "$BACKUP_FILE"

    return 0
}

# Cleanup old backups on remote host
cleanup_old_backups() {
    log_info "Cleaning up backups older than $RETENTION_DAYS days on $BACKUP_HOST..."

    # Remove old backup files
    OLD_BACKUP_COUNT=$(ssh "$BACKUP_HOST" "find $BACKUP_REMOTE_DIR -name 'htstatus_full_backup_*.sql' -type f -mtime +$RETENTION_DAYS | wc -l" 2>/dev/null || echo "0")

    if [ "$OLD_BACKUP_COUNT" -gt 0 ]; then
        log_info "Found $OLD_BACKUP_COUNT old backup(s) to remove"
        ssh "$BACKUP_HOST" "find $BACKUP_REMOTE_DIR -name 'htstatus_full_backup_*.sql' -type f -mtime +$RETENTION_DAYS -delete"
        log_success "Removed $OLD_BACKUP_COUNT old backup(s)"
    else
        log_info "No old backups to remove"
    fi

    # Show current backup count
    CURRENT_BACKUP_COUNT=$(ssh "$BACKUP_HOST" "find $BACKUP_REMOTE_DIR -name 'htstatus_full_backup_*.sql' -type f | wc -l" 2>/dev/null || echo "0")
    log_info "Current backup count on $BACKUP_HOST: $CURRENT_BACKUP_COUNT"
}

# Main execution
main() {
    # Ensure log file exists and is writable
    sudo touch "$LOG_FILE" 2>/dev/null || LOG_FILE="$HOME/htstatus-backup.log"

    log_info "HattrickPlanner Automated Backup Starting"
    log_info "Project root: $PROJECT_ROOT"
    log_info "Target host: $BACKUP_HOST"
    log_info "Remote directory: $BACKUP_REMOTE_DIR"

    # Create backup and transfer
    if create_and_transfer_backup; then
        log_success "Database backup and transfer completed successfully"

        # Clean up old backups
        cleanup_old_backups

        log_success "=== Automated backup process completed ==="
        exit 0
    else
        log_error "=== Automated backup process failed ==="
        exit 1
    fi
}

# Run main function
main "$@"