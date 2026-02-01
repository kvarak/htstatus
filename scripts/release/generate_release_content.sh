#!/bin/bash

# Release Content Generation
# Purpose: Generate user-focused release notes from git commits
# Usage: ./scripts/generate_release_content.sh [version]
# Output: Formatted release content for RELEASES.md

set -e

# Determine version
version="$1"
if [ -z "$version" ]; then
    # Generate version from git describe
    version=$(git describe --tags 2>/dev/null || echo "v0.1.0")
    # Clean up version format (remove commit hash if present)
    version=$(echo "$version" | sed 's/-[0-9]*-g[a-f0-9]*$//')
fi

# Ensure version has v prefix for consistency
if [[ ! "$version" =~ ^v ]]; then
    version="v$version"
fi

# Get the last tag for comparison
last_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

# Get commits since last tag
if [ -n "$last_tag" ]; then
    commits=$(git log --oneline --no-merges "$last_tag..HEAD" 2>/dev/null || echo "")
else
    # First release - get all commits
    commits=$(git log --oneline --no-merges 2>/dev/null || echo "")
fi

if [ -z "$commits" ]; then
    echo "No commits found for release content generation" >&2
    exit 1
fi

echo "## $version - $(date +'%B %Y')"
echo ""

# Extract user-facing features and improvements
echo "$commits" | grep -E "(feat:|add:|implement|Add |Implement |\[feat-)" | head -4 | while IFS= read -r commit; do
    # Clean up commit message for user consumption
    message=$(echo "$commit" | sed 's/^[a-f0-9]* //' | sed 's/\[feat-[^]]*\]//' | sed 's/^feat: *//' | sed 's/^add: *//' | sed 's/^implement *//')

    # Convert technical language to user-friendly descriptions
    case "$message" in
        *"timeline"*|*"visualization"*)
            echo "- Added player timeline to track squad development over time" ;;
        *"feedback"*|*"voting"*)
            echo "- Added community feedback system with voting and status tracking" ;;
        *"PWA"*|*"session"*|*"persistence"*)
            echo "- Fixed session management so you stay logged in across browser tabs" ;;
        *"CHPP"*|*"API"*|*"policy"*)
            echo "- Fixed Hattrick API integration issues for better reliability" ;;
        *"auth"*|*"login"*|*"OAuth"*)
            echo "- Improved login flow and user experience" ;;
        *"database"*|*"migration"*|*"backup"*)
            echo "- Improved database system with enhanced data safety" ;;
        *"test"*|*"coverage"*|*"quality"*)
            echo "- Improved app reliability with better quality checks" ;;
        *"UI"*|*"interface"*|*"design"*)
            echo "- Enhanced user interface and visual design" ;;
        *)
            # Generic fallback - capitalize and clean up
            clean_message=$(echo "$message" | sed 's/^./\U&/' | sed 's/ *$//')
            echo "- $clean_message" ;;
    esac
done
