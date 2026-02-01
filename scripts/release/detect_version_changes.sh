#!/bin/bash

# Version Detection for Release Generation
# Purpose: Detect if version changes warrant release documentation update
# Usage: ./scripts/release/detect_version_changes.sh
# Output: Exits 0 if release needed, 1 if not

set -e

# Get current version from git describe
current_version=$(git describe --tags 2>/dev/null || echo "v0.0.0")
echo "Current version: $current_version" >&2

# Get the last tag (for comparison)
last_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -z "$last_tag" ]; then
    echo "No previous tags found - first release" >&2
    exit 0
fi

echo "Last tag: $last_tag" >&2

# Check for feature commits since last tag
feature_commits=$(git log --oneline --grep="\[feat-" "$last_tag..HEAD" 2>/dev/null || echo "")
if [ -n "$feature_commits" ]; then
    echo "Feature commits found since $last_tag:" >&2
    echo "$feature_commits" >&2
    exit 0
fi

# Check for commits that indicate new features or significant changes
significant_commits=$(git log --oneline --grep="feat:" --grep="add:" --grep="implement" --grep="Add " --grep="Implement " -i "$last_tag..HEAD" 2>/dev/null || echo "")
if [ -n "$significant_commits" ]; then
    echo "Significant commits found since $last_tag:" >&2
    echo "$significant_commits" >&2
    exit 0
fi

echo "No feature or significant commits found since $last_tag" >&2
exit 1