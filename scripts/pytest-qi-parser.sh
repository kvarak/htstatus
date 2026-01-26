#!/bin/bash
# pytest-qi-parser.sh - Convert pytest JSON report to QI JSON format
# Usage: pytest-qi-parser.sh <pytest_json_file> <output_json_file> <title> <makecommand>

set -euo pipefail

if [ $# -ne 4 ]; then
    echo "Usage: $0 <pytest_json_file> <output_json_file> <title> <makecommand>"
    echo ""
    echo "Examples:"
    echo "  $0 /tmp/pytest-core.json out/tests/test-core.json 'Core Tests' 'make test-core'"
    echo "  $0 /tmp/pytest-db.json out/tests/test-db.json 'Database Tests' 'make test-db'"
    exit 1
fi

PYTEST_JSON="$1"
OUTPUT_JSON="$2"
TITLE="$3"
MAKECOMMAND="$4"

# Check if pytest JSON file exists
if [ ! -f "$PYTEST_JSON" ]; then
    echo "❌ ERROR: pytest JSON file not found: $PYTEST_JSON"
    exit 1
fi

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "❌ ERROR: jq is required but not installed"
    exit 1
fi

# Parse pytest JSON results
PASSED=$(jq -r '.summary.passed // 0' "$PYTEST_JSON")
FAILED=$(jq -r '.summary.failed // 0' "$PYTEST_JSON")
ERRORS=$(jq -r '.summary.error // 0' "$PYTEST_JSON")
SKIPPED=$(jq -r '.summary.skipped // 0' "$PYTEST_JSON")
TOTAL=$(jq -r '.summary.total // 0' "$PYTEST_JSON")
DURATION=$(jq -r '.duration // 0' "$PYTEST_JSON")
EXIT_CODE=$(jq -r '.exitcode // 0' "$PYTEST_JSON")

# Calculate status and details
TOTAL_ISSUES=$((FAILED + ERRORS))

if [ "$TOTAL_ISSUES" -eq 0 ] && [ "$EXIT_CODE" -eq 0 ]; then
    STATUS="PASSED"
    METRIC="$PASSED tests passed"
    DETAILS="all tests successful"
    if [ "$SKIPPED" -gt 0 ]; then
        DETAILS="$DETAILS ($SKIPPED skipped)"
    fi
elif [ "$TOTAL_ISSUES" -eq 0 ] && [ "$EXIT_CODE" -ne 0 ]; then
    # Tests passed but pytest failed (e.g., coverage threshold not met)
    STATUS="FAILED"
    METRIC="$PASSED tests passed"
    DETAILS="tests passed but quality threshold not met"
    if [ "$SKIPPED" -gt 0 ]; then
        DETAILS="$DETAILS ($SKIPPED skipped)"
    fi
else
    STATUS="FAILED"
    METRIC="$TOTAL_ISSUES test failures"
    DETAILS="$FAILED failed"
    if [ "$ERRORS" -gt 0 ]; then
        DETAILS="$DETAILS, $ERRORS errors"
    fi
    if [ "$SKIPPED" -gt 0 ]; then
        DETAILS="$DETAILS, $SKIPPED skipped"
    fi
fi

# Format duration nicely
DURATION_STR=$(printf "%.2fs" "$DURATION")

# Use qi-json.sh to generate the final JSON with extra fields
scripts/qi-json.sh "$OUTPUT_JSON" "$TITLE" "$MAKECOMMAND" "$STATUS" 0 "$TOTAL_ISSUES" "$METRIC" "$DETAILS" duration="$DURATION_STR" passed="$PASSED" total="$TOTAL"

echo "✅ Converted pytest results: $PASSED passed, $TOTAL_ISSUES failed, $SKIPPED skipped → $OUTPUT_JSON"
