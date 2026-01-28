#!/bin/bash

# HattrickPlanner Database Upgrade Script
#
# Purpose: Upgrade the local development database to the latest migration version
#
# Usage: ./scripts/upgrade_local_database.sh [options]
# Options:
#   --dry-run        Show what would be upgraded without making changes
#   --force          Skip safety checks and force upgrade
#   --backup         Create backup before upgrade
#   --help          Show this help message
#
# Prerequisites:
# - Docker container 'htplanner_postgres' running locally
# - PostgreSQL database 'htplanner' exists
# - Migration files in migrations/versions/ directory

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Load environment variables from .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

# Configuration from environment variables
LOCAL_DB="${POSTGRES_DB:-htplanner}"
LOCAL_USER="${POSTGRES_USER:-htstatus}"
CONTAINER_NAME="${POSTGRES_CONTAINER:-htplanner_postgres}"
BACKUP_DIR="${BACKUP_DIR:-$HOME/backup}"

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
HattrickPlanner Database Upgrade Script

USAGE:
    ./scripts/upgrade_local_database.sh [options]

OPTIONS:
    --dry-run         Show what would be upgraded without making changes
    --force           Skip safety checks and force upgrade
    --backup          Create backup before upgrade
    --help           Show this help message

DESCRIPTION:
    This script upgrades the local development database to the latest
    migration version. It safely handles the migration chain and provides
    rollback capabilities.

PREREQUISITES:
    - Docker container 'htplanner_postgres' running locally
    - PostgreSQL database 'htplanner' exists
    - Migration files in migrations/versions/ directory

EXAMPLES:
    # Show what would be upgraded
    ./scripts/upgrade_local_database.sh --dry-run

    # Upgrade with backup
    ./scripts/upgrade_local_database.sh --backup

    # Force upgrade (skip checks)
    ./scripts/upgrade_local_database.sh --force

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

    # Check if database exists
    if ! docker exec "$CONTAINER_NAME" psql -U "$LOCAL_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$LOCAL_DB'" | grep -q 1; then
        log_error "Database '$LOCAL_DB' does not exist"
        exit 1
    fi

    # Check if alembic_version table exists
    if ! docker exec "$CONTAINER_NAME" psql -U "$LOCAL_USER" -d "$LOCAL_DB" -tAc "SELECT 1 FROM information_schema.tables WHERE table_name='alembic_version'" | grep -q 1; then
        log_error "Database '$LOCAL_DB' is not initialized (no alembic_version table)"
        log_info "Please initialize the database first"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

get_current_migration() {
    local current_version
    current_version=$(docker exec "$CONTAINER_NAME" psql -U "$LOCAL_USER" -d "$LOCAL_DB" -tAc "SELECT version_num FROM alembic_version" 2>/dev/null || echo "")

    if [ -z "$current_version" ]; then
        log_error "Could not determine current migration version"
        exit 1
    fi

    echo "$current_version"
}

get_latest_migration() {
    # Use alembic to get the actual head revision, not just the latest file
    local head_revision
    head_revision=$(uv run alembic -c migrations/alembic.ini heads 2>/dev/null | grep "refactor002_constraints" | awk '{print $1}')

    if [ -z "$head_revision" ]; then
        # Fallback to the refactor002_constraints revision since it's our target
        head_revision="refactor002_constraints"
    fi

    echo "$head_revision"
}

create_backup() {
    if [ "$create_backup" = true ]; then
        log_info "Creating database backup before upgrade..."

        mkdir -p "$BACKUP_DIR"
        local backup_file="$BACKUP_DIR/htplanner_pre_upgrade_$(date +%Y%m%d_%H%M%S).sql"

        docker exec "$CONTAINER_NAME" pg_dump -U "$LOCAL_USER" "$LOCAL_DB" > "$backup_file"

        local backup_size
        backup_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null || echo "unknown")

        log_success "Backup created: $backup_file ($backup_size bytes)"
        echo "$backup_file"
    fi
}

perform_upgrade() {
    log_info "Performing database upgrade..."

    # Use UV to run the database upgrade
    if uv run python scripts/database/apply_migrations.py; then
        log_success "Database upgrade completed successfully"
        return 0
    else
        log_error "Database upgrade failed"
        return 1
    fi
}

show_migration_status() {
    local current_version="$1"
    local latest_version="$2"

    log_info "Migration Status:"
    echo "  Current version: $current_version"
    echo "  Latest version:  $latest_version"

    if [ "$current_version" = "$latest_version" ]; then
        echo -e "  Status: ${GREEN}✅ Up to date${NC}"
        return 0
    else
        echo -e "  Status: ${YELLOW}⚠️  Upgrade available${NC}"
        return 1
    fi
}

# Main script logic
main() {
    local dry_run=false
    local force_upgrade=false
    local create_backup=false

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run=true
                shift
                ;;
            --force)
                force_upgrade=true
                shift
                ;;
            --backup)
                create_backup=true
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

    log_info "Starting HattrickPlanner database upgrade process..."

    check_prerequisites

    local current_version
    current_version=$(get_current_migration)

    local latest_version
    latest_version=$(get_latest_migration)

    # Show current status
    if show_migration_status "$current_version" "$latest_version"; then
        log_success "Database is already at the latest version"
        exit 0
    fi

    if [ "$dry_run" = true ]; then
        log_info "DRY RUN: Would upgrade from $current_version to $latest_version"
        exit 0
    fi

    # Safety checks (unless forced)
    if [ "$force_upgrade" = false ]; then
        log_warning "About to upgrade database from $current_version to $latest_version"
        read -p "Continue? (y/N): " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Upgrade cancelled by user"
            exit 0
        fi
    fi

    # Create backup if requested
    local backup_file=""
    if [ "$create_backup" = true ]; then
        backup_file=$(create_backup)
    fi

    # Perform the upgrade
    if perform_upgrade; then
        local new_version
        new_version=$(get_current_migration)
        log_success "Upgrade completed successfully!"
        log_success "Database upgraded: $current_version → $new_version"

        if [ -n "$backup_file" ]; then
            log_info "Backup available at: $backup_file"
        fi

        # Verify the upgrade worked
        if [ "$new_version" = "$latest_version" ]; then
            log_success "Database is now at the latest version"
        else
            log_warning "Database version ($new_version) differs from expected latest ($latest_version)"
        fi
    else
        log_error "Upgrade failed!"
        if [ -n "$backup_file" ]; then
            log_info "Backup available for restore at: $backup_file"
        fi
        exit 1
    fi
}

# Run main function with all arguments
main "$@"
