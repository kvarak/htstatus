#!/bin/bash

# Update RELEASES.md with new version content
# Purpose: Insert new release section at top of RELEASES.md
# Usage: ./scripts/update_releases.sh [version]

set -e

# Determine version
version="$1"
if [ -z "$version" ]; then
    # Generate version from git describe, increment minor
    current=$(git describe --tags 2>/dev/null | sed 's/^v//' | sed 's/-.*$//')
    if [ -z "$current" ]; then
        version="v3.1"
    else
        # Simple increment for demo - in production might parse semantic versioning
        major=$(echo "$current" | cut -d. -f1)
        minor=$(echo "$current" | cut -d. -f2)
        new_minor=$((minor + 1))
        version="v$major.$new_minor"
    fi
fi

releases_file="RELEASES.md"
temp_file=$(mktemp)

echo "Updating $releases_file with version $version" >&2

# Generate new release content
new_content=$(./scripts/release/generate_release_content.sh "$version")

if [ -z "$new_content" ]; then
    echo "No release content generated" >&2
    exit 1
fi

# Read existing file and insert new content after the separator line
{
    # Copy header up to and including the separator
    sed '/^---$/q' "$releases_file"
    echo ""
    # Insert new release content
    echo "$new_content"
    echo ""
    # Add remaining content (skip header section)
    sed '1,/^---$/d' "$releases_file" | sed '/^$/,$d' | tail -n +2
    sed '1,/^---$/d' "$releases_file" | sed -n '/^$/,$p'
} > "$temp_file"

# Replace original file
mv "$temp_file" "$releases_file"

echo "Updated $releases_file with $version" >&2
echo "Release content:"
echo "$new_content" >&2
