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
# Look for patterns like FEAT-123, DOC-456, EPIC-007, etc.
PATTERN="${TASK_TYPE}-[0-9]+"

# Get all matching task IDs from git history
TASK_IDS=$(git log --all --grep="$PATTERN" --oneline 2>/dev/null | grep -oE "$PATTERN" || true)

# Also search file contents in git history
FILE_TASK_IDS=$(git log --all -p .project/backlog.md .project/tasks/ 2>/dev/null | grep -oE "$PATTERN" || true)

# Search current files (uncommitted changes)
if [ "$TASK_TYPE" = "EPIC" ]; then
    # EPICs are section headers, not task lines
    CURRENT_BACKLOG=$(grep -oE "EPIC-[0-9]+" .project/backlog.md 2>/dev/null || true)
else
    # Regular tasks are in task lines starting with -
    CURRENT_BACKLOG=$(grep -E "^\s*-.*$PATTERN" .project/backlog.md 2>/dev/null | grep -oE "$PATTERN" || true)
fi
CURRENT_TASKS=$(find .project/tasks/ -name "*.md" -exec grep -oE "$PATTERN" {} \; 2>/dev/null || true)

# Combine all sources
ALL_TASK_IDS=$(echo -e "$TASK_IDS\n$FILE_TASK_IDS\n$CURRENT_BACKLOG\n$CURRENT_TASKS" | grep -E "^$PATTERN$" | sort -u || true)

# Check /tmp/${TASK_TYPE} for the last generated number to avoid duplicates in the same session
if [ -f "/tmp/${TASK_TYPE}" ]; then
    LAST_NUM=$(cat "/tmp/${TASK_TYPE}")
    if [[ "$LAST_NUM" =~ ^[0-9]+$ ]]; then
        # Add this to the list of existing task IDs to ensure we don't reuse it
        ALL_TASK_IDS=$(echo -e "$ALL_TASK_IDS\n${TASK_TYPE}-$(printf "%03d" "$LAST_NUM")" | sort -u)
    fi
fi

if [ -z "$ALL_TASK_IDS" ]; then
    # No existing tasks found, start with 001
    echo "${TASK_TYPE}-001"
    echo "001" > "/tmp/${TASK_TYPE}"
else
    # Extract numbers, sort numerically, get the highest
    HIGHEST_NUM=$(echo "$ALL_TASK_IDS" | sed "s/${TASK_TYPE}-0*//" | sort -n | tail -1)

    # Calculate next number with zero padding (force base 10 with 10#)
    NEXT_NUM=$((10#$HIGHEST_NUM + 1))
    printf "%s-%03d\n" "$TASK_TYPE" "$NEXT_NUM"
    echo "$NEXT_NUM" > "/tmp/${TASK_TYPE}"
fi
