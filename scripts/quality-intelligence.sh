#!/bin/bash

# HTStatus Quality Intelligence Platform - Enhanced with Coverage Gate
# Provides detailed tabular summary with Coverage as a dedicated quality gate

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BOLD}🎯 HTStatus Quality Intelligence Report - Detailed Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo -e "${BOLD}📊 Quality Gates Overview${NC}"
echo "┌─────────────────────────┬──────────┬──────────┬──────────┬────────────────────────┐"
echo "│ Quality Gate            │ Status   │ Skipped  │ Warnings │ Make Command           │"
echo "├─────────────────────────┼──────────┼──────────┼──────────┼────────────────────────┤"

# Helper function to parse standard test results (unified for all gates)
parse_test_data() {
    local file="$1"
    local skipped="0"
    local warnings="0"
    local status="UNK"

    if [ -f "$file" ]; then
        # Extract QI_RESULT status
        qi_line=$(grep "QI_RESULT:" "$file" 2>/dev/null | tail -1)
        if [ -n "$qi_line" ]; then
            qi_status=$(echo "$qi_line" | sed 's/.*"status":"\([^"]*\)".*/\1/')

            case "$qi_status" in
                "PASSED") status="PASS" ;;
                "ISSUES") status="ISSUE" ;;
                "FAILED") status="FAIL" ;;
                *) status="UNK" ;;
            esac
        fi

        # Extract skipped count
        skipped=$(grep -o '[0-9]* skipped' "$file" 2>/dev/null | tail -1 | grep -o '[0-9]*' || echo "0")

        # Count warnings
        warnings=$(grep -c "warnings summary\|WARNING\|DeprecationWarning" "$file" 2>/dev/null || echo "0")

        # Special case: if no skipped/warnings found but tests passed, show clean state
        if [ "$skipped" = "0" ]; then skipped="   -"; fi
        if [ "$warnings" = "0" ]; then warnings="   -"; fi
    else
        status="SKIP"
        skipped="   -"
        warnings="   -"
    fi

    echo "$status|$skipped|$warnings"
}

# Unified function for all quality gates (eliminates duplication)
print_gate_row() {
    local gate_name="$1"
    local file="$2"
    local make_cmd="$3"

    result=$(parse_test_data "$file")
    IFS='|' read -r status skipped warnings <<< "$result"

    printf "│ %-23s │ %-8s │ %8s │ %8s │ %-22s │\n" \
        "$gate_name" "$status" "$skipped" "$warnings" "$make_cmd"
}

# Generate all quality gate rows using unified function (simplified)
print_gate_row "File Standards" "/tmp/fileformat-results.txt" "make fileformat"
print_gate_row "Code Quality" "/tmp/lint-results.txt" "make lint"
print_gate_row "Security Analysis" "/tmp/security-results.txt" "make security"
print_gate_row "Type Synchronization" "/tmp/typesync-results.txt" "make typesync"
print_gate_row "Coverage Analysis" "/tmp/test-results.txt" "make test-coverage"
print_gate_row "Configuration Tests" "/tmp/config-results.txt" "make test-config"
print_gate_row "Application Tests" "/tmp/test-results.txt" "make test-isolated"

echo "└─────────────────────────┴──────────┴──────────┴──────────┴────────────────────────┘"

echo ""
echo -e "${BOLD}🎯 Deployment Confidence Assessment${NC}"

# Count passed quality gates (simplified logic)
passed_gates=0
total_gates=7

# Check all quality gates uniformly
for result_file in "/tmp/fileformat-results.txt" "/tmp/lint-results.txt" "/tmp/security-results.txt" "/tmp/typesync-results.txt" "/tmp/config-results.txt" "/tmp/test-results.txt"; do
    if [ -f "$result_file" ] && grep -q '"status":"PASSED"' "$result_file" 2>/dev/null; then
        passed_gates=$((passed_gates + 1))
    fi
done

# Note: test-results.txt represents both Coverage Analysis and Application Tests
# If test-results.txt passes, count it as 2 gates (since both use same file)
if [ -f "/tmp/test-results.txt" ] && grep -q '"status":"PASSED"' "/tmp/test-results.txt" 2>/dev/null; then
    passed_gates=$((passed_gates + 1))  # Add one more for the duplicate gate
fi

if [ $passed_gates -ge 6 ]; then
    echo -e "   ${GREEN}HIGH ✅${NC} ($passed_gates/$total_gates quality gates passed)"
elif [ $passed_gates -ge 4 ]; then
    echo -e "   ${YELLOW}MODERATE ⚠️${NC} ($passed_gates/$total_gates quality gates passed)"
else
    echo -e "   ${RED}LOW ❌${NC} ($passed_gates/$total_gates quality gates passed)"
fi

echo ""
echo -e "${BOLD}💡 Quick Actions${NC}"
echo "   Run individual targets: Use the 'Make Command' column above"
echo "   Fix type issues:        make typesync"
echo "   Improve coverage:       make test-coverage"
echo "   Full validation:        make test-all"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Cleanup temp files after analysis
rm -f /tmp/fileformat-results.txt /tmp/lint-results.txt /tmp/security-results.txt /tmp/bandit-results.json /tmp/bandit-results.txt /tmp/safety-results.json /tmp/typesync-results.txt /tmp/config-results.txt /tmp/test-results.txt

echo "✅ Quality Intelligence Platform analysis complete"
