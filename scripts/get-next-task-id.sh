#!/bin/bash

# get-next-task-id.sh
# Usage: ./get-next-task-id.sh FEAT
# Returns the next available task ID for the given type

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <TASK_TYPE>" >&2
    echo "Example: $0 FEAT" >&2
    exit 1
fi

TASK_TYPE="$1"

# Validate task type format (should be uppercase letters)
if ! [[ "$TASK_TYPE" =~ ^[A-Z]+$ ]]; then
    echo "Error: Task type should contain only uppercase letters" >&2
    exit 1
fi

# Search git history for task IDs in both backlog.md and .project/tasks/
# Look for patterns like FEAT-123, DOC-456, etc.
PATTERN="${TASK_TYPE}-[0-9]+"

# Get all matching task IDs from git history
TASK_IDS=$(git log --all --grep="$PATTERN" --oneline 2>/dev/null | grep -oE "$PATTERN" || true)

# Also search file contents in git history
FILE_TASK_IDS=$(git log --all -p .project/backlog.md .project/tasks/ 2>/dev/null | grep -oE "$PATTERN" || true)

# Search current files (uncommitted changes)
CURRENT_BACKLOG=$(grep -E "^\s*-.*$PATTERN" .project/backlog.md 2>/dev/null | grep -oE "$PATTERN" || true)
CURRENT_TASKS=$(find .project/tasks/ -name "*.md" -exec grep -oE "$PATTERN" {} \; 2>/dev/null || true)

# Combine all sources
ALL_TASK_IDS=$(echo -e "$TASK_IDS\n$FILE_TASK_IDS\n$CURRENT_BACKLOG\n$CURRENT_TASKS" | grep -E "^$PATTERN$" | sort -u || true)

if [ -z "$ALL_TASK_IDS" ]; then
    # No existing tasks found, start with 001
    echo "${TASK_TYPE}-001"
else
    # Extract numbers, sort numerically, get the highest
    HIGHEST_NUM=$(echo "$ALL_TASK_IDS" | sed "s/${TASK_TYPE}-0*//" | sort -n | tail -1)

    # Calculate next number with zero padding (force base 10 with 10#)
    NEXT_NUM=$((10#$HIGHEST_NUM + 1))
    printf "%s-%03d\n" "$TASK_TYPE" "$NEXT_NUM"
fi