#!/bin/bash
# check-chpp-usage.sh
# Enforce CHPP API usage policy: ONLY login/callback/update routes may call CHPP API
# See .github/agents/htplanner-ai-agent.md for complete CHPP usage policy

set -euo pipefail

VIOLATIONS=0
OUTPUT_FILE="out/tests/check-chpp.json"

# Create output directory
mkdir -p out/tests

# CHPP usage patterns to detect
declare -a PATTERNS=(
    "CHPP("
    "get_chpp_client"
    "from app.chpp import"
)

# Routes allowed to use CHPP (update, login, OAuth callback)
declare -a ALLOWED_FILES=(
    "app/blueprints/auth.py"
    "app/blueprints/team.py"
)

# Build grep exclude pattern
EXCLUDE_PATTERN=""
for allowed in "${ALLOWED_FILES[@]}"; do
    EXCLUDE_PATTERN="${EXCLUDE_PATTERN:+$EXCLUDE_PATTERN|}$allowed"
done

echo "🔍 Checking CHPP API usage policy compliance..."
echo "   Allowed files: ${ALLOWED_FILES[*]}"
echo ""

VIOLATION_DETAILS=""

# Check each pattern
for pattern in "${PATTERNS[@]}"; do
    echo "  → Checking for: $pattern"

    # Search Python files, exclude allowed files and docstring examples
    matches=$(git grep -n "$pattern" -- 'app/**/*.py' 2>/dev/null | \
              grep -v -E "($EXCLUDE_PATTERN)" | \
              grep -v "# CHPP policy check:" | \
              grep -v ">>> chpp" | \
              grep -v "app/chpp/" || true)

    if [ -n "$matches" ]; then
        echo "    ❌ Found unauthorized CHPP usage:"
        echo "$matches" | while IFS= read -r line; do
            echo "       $line"
            VIOLATION_DETAILS="${VIOLATION_DETAILS}${line}\n"
        done
        VIOLATIONS=$((VIOLATIONS + 1))
    else
        echo "    ✅ No violations"
    fi
done

echo ""

# Generate quality intelligence JSON
if [ $VIOLATIONS -eq 0 ]; then
    echo "✅ CHPP API usage policy: PASSED"
    echo "   All CHPP calls are in approved routes (login, OAuth, update)"

    # Success JSON
    scripts/qi-json.sh "$OUTPUT_FILE" "CHPP Policy" "make check-chpp" "PASSED" 0 0 \
        "policy compliant" "CHPP API only used in login/OAuth/update routes"

    exit 0
else
    echo "❌ CHPP API usage policy: FAILED"
    echo ""
    echo "Found $VIOLATIONS unauthorized CHPP API calls"
    echo ""
    echo "CHPP API Usage Policy:"
    echo "  ✅ ALLOWED: /login, /callback (OAuth), /update (explicit user action)"
    echo "  ❌ FORBIDDEN: All other routes (use session + database queries)"
    echo ""
    echo "Fix: Remove CHPP calls from unauthorized routes"
    echo "See: .github/agents/htplanner-ai-agent.md#chpp-api-usage-critical"

    # Failure JSON
    scripts/qi-json.sh "$OUTPUT_FILE" "CHPP Policy" "make check-chpp" "FAILED" 0 "$VIOLATIONS" \
        "policy violations found" "CHPP API used in unauthorized routes"

    exit 1
fi
