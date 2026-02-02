#!/bin/bash
# Generate JSON changelog files from git commits and release notes

# 1. Generate commit history JSON
echo '{"source": "commits", "entries": [' > app/static/changelog.json
first_entry=true
git log --format='%ci|%h|%s' | while IFS='|' read -r date hash message; do
    if [ "$first_entry" = true ]; then
        first_entry=false
    else
        echo ',' >> app/static/changelog.json
    fi
    # Strip timezone from date to match release format
    clean_date=$(echo "$date" | sed 's/ [+-][0-9]*$//')
    # Get version for this commit using git describe and format it properly
    version_raw=$(git describe --tags "$hash" 2>/dev/null)
    if [ -z "$version_raw" ]; then
        # For commits before first tag, create version like "0.0-N-ghash" where N is commits from start
        commit_count=$(git rev-list --count "$hash")
        version="0.0-${commit_count}-g${hash}"
    else
        # Convert format from "3.15-8-g5015d35" to "3.15.8-g5015d35" (replace first hyphen with dot)
        version=$(echo "$version_raw" | sed 's/-/./')
    fi
    # Escape JSON strings
    message_escaped=$(echo "$message" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g')
    echo -n "{\"date\": \"$clean_date\", \"hash\": \"$hash\", \"version\": \"$version\", \"message\": \"$message_escaped\", \"type\": \"commit\"}" >> app/static/changelog.json
done
echo '' >> app/static/changelog.json
echo ']}' >> app/static/changelog.json

# 2. Generate user releases JSON from RELEASES.md
echo '{"source": "user_releases", "entries": [' > app/static/releases.json
first_entry=true
while IFS= read -r line; do
    if [[ $line =~ ^##\ ([0-9]+\.[0-9]+)\ -\ (.+)$ ]]; then
        version="${BASH_REMATCH[1]}"
        date_str="${BASH_REMATCH[2]}"

        # Convert date for sorting - use actual git commit timestamp for the tag
        commit_hash=$(git rev-list -n 1 "$version" 2>/dev/null)
        if [ -n "$commit_hash" ]; then
            sort_date=$(git log -1 --format="%ci" "$commit_hash" 2>/dev/null | sed 's/ +.*//')
        else
            # Fallback for manual mapping if git commands fail
            case "$date_str" in
                *"January 2026"*) sort_date="2026-01-15 06:00:00" ;;
                *"February 2026"*) sort_date="2026-02-01 06:00:00" ;;
                *"December 2025"*) sort_date="2025-12-15 06:00:00" ;;
                *"February 2023"*) sort_date="2023-02-15 06:00:00" ;;
                *) sort_date="2026-01-01 06:00:00" ;;
            esac
        fi

        # Get first feature
        first_feature=""
        while IFS= read -r feature_line; do
            if [[ $feature_line =~ ^-\ (.+)$ ]]; then
                first_feature="${BASH_REMATCH[1]}"
                first_feature=$(echo "$first_feature" | sed 's/\*\*[^*]*\*\*: *//' | sed 's/\*\*//g')
                break
            fi
        done <<< "$(grep -A 10 "^## $version" RELEASES.md | tail -n +2)"

        if [ "$first_entry" = true ]; then
            first_entry=false
        else
            echo ',' >> app/static/releases.json
        fi

        echo -n "{\"date\": \"$sort_date\", \"version\": \"$version\", \"period\": \"$date_str\", \"message\": \"$first_feature\", \"type\": \"user_release\"}" >> app/static/releases.json
    fi
done < RELEASES.md
echo ']}' >> app/static/releases.json

# 3. Generate internal releases JSON from RELEASES-INTERNAL.md
echo '{"source": "internal_releases", "entries": [' > app/static/releases-internal.json
first_entry=true
while IFS= read -r line; do
    if [[ $line =~ ^##\ ([0-9]+\.[0-9]+)\ -\ (.+)$ ]]; then
        version="${BASH_REMATCH[1]}"
        date_str="${BASH_REMATCH[2]}"

        # Convert date for sorting - use actual git commit timestamp for the tag
        if [ "$version" = "0.0" ]; then
            # Special case for v0.0 - use first commit timestamp
            sort_date=$(git log --format="%ci" 9dfa886a1ba96ca39e7d0044abc3f232233934ad 2>/dev/null | sed 's/ +.*//')
        else
            commit_hash=$(git rev-list -n 1 "$version" 2>/dev/null)
            if [ -n "$commit_hash" ]; then
                sort_date=$(git log -1 --format="%ci" "$commit_hash" 2>/dev/null | sed 's/ +.*//')
            else
                # Fallback for manual mapping if git commands fail
                case "$date_str" in
                    *"February 2026"*) sort_date="2026-02-01 04:00:00" ;;
                    *"January 2026"*) sort_date="2026-01-15 04:00:00" ;;
                    *"December 2025"*) sort_date="2025-12-15 04:00:00" ;;
                    *"February 2023"*) sort_date="2023-02-15 04:00:00" ;;
                    *"June 2020"*) sort_date="2020-06-03 04:00:00" ;;
                    *) sort_date="2025-01-01 04:00:00" ;;
                esac
            fi
        fi

        # Get first technical detail
        first_detail=""
        while IFS= read -r detail_line; do
            if [[ $detail_line =~ ^-\ (.+)$ ]]; then
                first_detail="${BASH_REMATCH[1]}"
                break
            fi
        done <<< "$(grep -A 10 "^## $version" RELEASES-INTERNAL.md | tail -n +2)"

        if [ "$first_entry" = true ]; then
            first_entry=false
        else
            echo ',' >> app/static/releases-internal.json
        fi

        echo -n "{\"date\": \"$sort_date\", \"version\": \"$version\", \"period\": \"$date_str\", \"message\": \"$first_detail\", \"type\": \"internal_release\"}" >> app/static/releases-internal.json
    fi
done < RELEASES-INTERNAL.md
echo ']}' >> app/static/releases-internal.json

# 4. Generate full user releases JSON from RELEASES.md with all features
echo '{"source": "user_releases_full", "entries": [' > app/static/releases-full.json
first_entry=true
while IFS= read -r line; do
    if [[ $line =~ ^##\ ([0-9]+\.[0-9]+)\ -\ (.+)$ ]]; then
        version="${BASH_REMATCH[1]}"
        date_str="${BASH_REMATCH[2]}"

        # Convert date for sorting - use actual git commit timestamp for the tag
        commit_hash=$(git rev-list -n 1 "$version" 2>/dev/null)
        if [ -n "$commit_hash" ]; then
            sort_date=$(git log -1 --format="%ci" "$commit_hash" 2>/dev/null | sed 's/ [+-][0-9]*$//')
        else
            # Fallback for manual mapping if git commands fail
            case "$date_str" in
                *"January 2026"*) sort_date="2026-01-15 06:00:00" ;;
                *"February 2026"*) sort_date="2026-02-01 06:00:00" ;;
                *"December 2025"*) sort_date="2025-12-15 06:00:00" ;;
                *"February 2023"*) sort_date="2023-02-15 06:00:00" ;;
                *) sort_date="2026-01-01 06:00:00" ;;
            esac
        fi

        # Get ALL features for this release
        features_json="["
        feature_count=0
        while IFS= read -r feature_line; do
            if [[ $feature_line =~ ^-\ (.+)$ ]]; then
                feature="${BASH_REMATCH[1]}"
                # Clean up markdown formatting but keep more detail
                feature=$(echo "$feature" | sed 's/\*\*//g' | sed 's/\\/\\\\/g' | sed 's/"/\\"/g')
                if [ $feature_count -gt 0 ]; then
                    features_json+=", "
                fi
                features_json+="\"$feature\""
                ((feature_count++))
            elif [[ $feature_line =~ ^##\ [0-9] ]]; then
                # Stop at next release header
                break
            fi
        done <<< "$(grep -A 50 "^## $version" RELEASES.md | tail -n +2)"
        features_json+="]"

        if [ "$first_entry" = true ]; then
            first_entry=false
        else
            echo ',' >> app/static/releases-full.json
        fi

        echo -n "{\"date\": \"$sort_date\", \"version\": \"$version\", \"period\": \"$date_str\", \"features\": $features_json, \"type\": \"user_release\"}" >> app/static/releases-full.json
    fi
done < RELEASES.md
echo ']}' >> app/static/releases-full.json

echo "Generated 4 JSON files:"
echo "- changelog.json: $(jq '.entries | length' app/static/changelog.json) commits"
echo "- releases.json: $(jq '.entries | length' app/static/releases.json) user releases"
echo "- releases-internal.json: $(jq '.entries | length' app/static/releases-internal.json) internal releases"
echo "- releases-full.json: $(jq '.entries | length' app/static/releases-full.json) full user releases"
