#!/bin/bash

# HTStatus Quality Intelligence Platform - Generic JSON-Based Implementation
# Dynamically discovers and reports on all quality gates defined in out/tests/*.json

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Function to truncate title to max width
truncate_title() {
    local title="$1"
    local max_width=23  # Adjust this to fit the table nicely

    if [ ${#title} -gt $max_width ]; then
        echo "${title:0:$((max_width-1))}..."
    else
        echo "$title"
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BOLD}🎯 HTStatus Quality Intelligence Report - Detailed Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

## Check if --expected-results argument is provided
EXPECTED_RESULTS=0
while [[ $# -gt 0 ]]; do
    case $1 in
        --expected-results)
            EXPECTED_RESULTS="$2"
            shift 2
            ;;
        *)
            echo "❌ Unknown argument: $1"
            ;;
    esac
done

# Function to validate QI JSON standards
validate_qi_json() {
    local file="$1"
    local filename=$(basename "$file" .json)

    if ! command -v jq >/dev/null 2>&1; then
        echo "⚠️  Warning: jq not available, skipping JSON validation for $filename"
        return 0
    fi

    # Check if file is valid JSON
    if ! jq empty "$file" 2>/dev/null; then
        echo "⚠️  Warning: $filename - Invalid JSON format"
        return 1
    fi

    # Detect JSON format and validate accordingly
    if jq -e '.title and .makecommand and .status' "$file" >/dev/null 2>&1; then
        # QI JSON format - validate QI fields
        local missing_fields=""
        for field in title makecommand status warnings errors; do
            if ! jq -e "has(\"$field\")" "$file" >/dev/null 2>&1; then
                missing_fields="$missing_fields $field"
            fi
        done

        if [ -n "$missing_fields" ]; then
            echo "⚠️  Warning: $filename - Missing required QI fields:$missing_fields"
            return 1
        fi

        # Check status values
        local status=$(jq -r '.status' "$file" 2>/dev/null)
        if [[ ! "$status" =~ ^(PASSED|ISSUES|FAILED)$ ]]; then
            echo "⚠️  Warning: $filename - Invalid status '$status' (must be PASSED, ISSUES, or FAILED)"
            return 1
        fi

    elif jq -e '.summary and .tests and .exitcode' "$file" >/dev/null 2>&1; then
        # pytest JSON format - validate pytest fields
        local missing_fields=""
        for field in summary tests exitcode; do
            if ! jq -e "has(\"$field\")" "$file" >/dev/null 2>&1; then
                missing_fields="$missing_fields $field"
            fi
        done

        if [ -n "$missing_fields" ]; then
            echo "⚠️  Warning: $filename - Missing required pytest fields:$missing_fields"
            return 1
        fi

        # Validate exit code is a number
        local exitcode=$(jq -r '.exitcode' "$file" 2>/dev/null)
        if ! [[ "$exitcode" =~ ^[0-9]+$ ]]; then
            echo "⚠️  Warning: $filename - Invalid exitcode '$exitcode' (must be a number)"
            return 1
        fi

    else
        echo "⚠️  Warning: $filename - Unknown JSON format (not QI or pytest)"
        return 1
    fi

    return 0
}

# Function to extract data from QI JSON or pytest JSON
parse_qi_json() {
    local file="$1"

    if ! command -v jq >/dev/null 2>&1; then
        echo "Unknown|UNK|-|-|unknown"
        return 1
    fi

    # Detect JSON format
    if jq -e '.title and .makecommand and .status' "$file" >/dev/null 2>&1; then
        # QI JSON format
        local title=$(jq -r '.title' "$file" 2>/dev/null || echo "Unknown")
        local status=$(jq -r '.status' "$file" 2>/dev/null || echo "UNK")
        local warnings=$(jq -r '.warnings' "$file" 2>/dev/null || echo "0")
        local errors=$(jq -r '.errors' "$file" 2>/dev/null || echo "0")
        local makecommand=$(jq -r '.makecommand' "$file" 2>/dev/null || echo "unknown")
        local coverage="N/A"  # QI JSON doesn't typically have coverage

    elif jq -e '.summary and .tests and .exitcode' "$file" >/dev/null 2>&1; then
        # pytest JSON format
        local basename=$(basename "$file" .json)
        local passed=$(jq -r '.summary.passed // 0' "$file")
        local failed=$(jq -r '.summary.failed // 0' "$file")
        local errors_count=$(jq -r '.summary.error // 0' "$file")
        local skipped=$(jq -r '.summary.skipped // 0' "$file")
        local exit_code=$(jq -r '.exitcode // 0' "$file")

        # Extract coverage data if available - check for separate coverage JSON file
        local coverage="N/A"
        local coverage_file="${file%-test-each-*-cov.json}"
        if [[ "$file" == *"test-each-"* ]]; then
            # For test-each files, look for corresponding -cov.json file
            local base_name=$(echo "$basename" | sed 's/test-each-//')
            local cov_file_path="$(dirname "$file")/test-each-${base_name}-cov.json"
            if [[ -f "$cov_file_path" ]]; then
                # Extract total coverage percentage from coverage JSON
                local total_coverage=$(jq -r '.totals.percent_covered // empty' "$cov_file_path" 2>/dev/null)
                if [[ -n "$total_coverage" && "$total_coverage" != "null" ]]; then
                    coverage=$(printf "%.1f%%" "$total_coverage")
                fi
            fi
        fi

        # Convert test type from filename to title
        case "$basename" in
            test-core) local title="Core Tests" ;;
            test-db) local title="Database Tests" ;;
            test-routes) local title="Route Tests" ;;
            test-config) local title="Configuration Tests" ;;
            test-each-test_*)
                # Clean up individual test names
                local clean_name=$(echo "$basename" | sed 's/test-each-test_//' | sed 's/_/ /g' | sed 's/\b\w/\u&/g')
                local title="$(truncate_title "$clean_name")"
                ;;
            *) local title="$(truncate_title "$(echo "$basename" | sed 's/-/ /g' | sed 's/\b\w/\u&/g')")" ;;
        esac

        # Generate make command - simplify for individual tests
        case "$basename" in
            test-each-test_*)
                local test_name=$(echo "$basename" | sed 's/test-each-//')
                local makecommand="make test-single FILE=tests/$test_name.py"
                ;;
            *)
                local makecommand="make $basename"
                ;;
        esac
        local total_issues=$((failed + errors_count))

        # Determine status
        if [ "$total_issues" -eq 0 ] && [ "$exit_code" -eq 0 ]; then
            local status="PASSED"
        else
            local status="FAILED"
        fi

        # Use skipped as warnings, total issues as errors for display
        local warnings="$skipped"
        local errors="$total_issues"

    else
        echo "Unknown|UNK|-|-|N/A|unknown"
        return 1
    fi

    # Convert status to display format
    case "$status" in
        "PASSED") status="PASS" ;;
        "ISSUES") status="ISSUE" ;;
        "FAILED") status="FAIL" ;;
        *) status="UNK" ;;
    esac

    # Format display values
    if [ "$warnings" = "0" ]; then warnings="   -"; fi
    if [ "$errors" = "0" ]; then errors="   -"; fi

    echo "$title|$status|$warnings|$errors|$coverage|$makecommand"
}

# Check if out/tests directory exists
if [ ! -d "out/tests" ]; then
    echo "❌ Error: out/tests directory not found. Run 'make test-all' first."
    exit 1
fi

# Check if any JSON files exist
if [ ! "$(ls out/tests/*.json 2>/dev/null)" ]; then
    echo "❌ Error: No QI JSON files found in out/tests/. Run 'make test-all' first."
    exit 1
fi

echo ""
echo "📊 Quality Gates Overview"
printf "${BOLD}%-25s %-10s %10s %10s %10s %-25s${NC}\n" \
    "Quality Gate" "Status" "Warnings" "Errors" "Coverage" "Make Command"

# Process all JSON files in out/tests/
passed_gates=0
total_gates=0
validation_warnings=0
min_coverage=100
least_covered_file=""
least_covered_title=""

for json_file in out/tests/*.json; do
    # Skip coverage JSON files (they are processed separately for coverage data)
    if [[ "$json_file" == *-cov.json ]]; then
        continue
    fi

    if [ -f "$json_file" ]; then
        total_gates=$((total_gates + 1))

        # Validate QI JSON standards
        if ! validate_qi_json "$json_file"; then
            validation_warnings=$((validation_warnings + 1))
        fi

        # Parse and display gate data
        gate_data=$(parse_qi_json "$json_file")
        IFS='|' read -r title status warnings errors coverage makecommand <<< "$gate_data"

        # Track least covered test file
        if [[ "$coverage" != "N/A" && "$coverage" != "   -" ]]; then
            # Extract numeric value from coverage percentage (e.g., "22.1%" -> "22.1")
            coverage_value=$(echo "$coverage" | sed 's/%//')
            if [[ "$coverage_value" =~ ^[0-9]+\.?[0-9]*$ ]]; then
                if (( $(echo "$coverage_value < $min_coverage" | bc -l 2>/dev/null || [ "${coverage_value%.*}" -lt "${min_coverage%.*}" ]) )); then
                    min_coverage="$coverage_value"
                    least_covered_file="$makecommand"
                    least_covered_title="$title"
                fi
            fi
        fi

        # Count passed gates
        if [ "$status" = "PASS" ]; then
            passed_gates=$((passed_gates + 1))
        fi

        printf "%-25s %-10s %10s %10s %10s %-25s\n" \
            "$title" "$status" "$warnings" "$errors" "$coverage" "$makecommand"
    fi
done

# Display validation warnings if any
if [ $validation_warnings -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  $validation_warnings QI JSON validation warning(s) found above${NC}"
fi

echo ""
echo -e "${BOLD}🎯 Deployment Confidence Assessment${NC}"

if [ $EXPECTED_RESULTS -gt 0 ]; then
    echo "   Expected Quality Gates: $EXPECTED_RESULTS"
    if [ $total_gates -lt $EXPECTED_RESULTS ]; then
        echo -e "   ${RED}❌ WARNING: Fewer quality gates than expected (${total_gates} < ${EXPECTED_RESULTS})${NC}"
    fi
fi

# final_gates = max of ($total_gates, $EXPECTED_RESULTS)
final_gates=$total_gates
if [ $EXPECTED_RESULTS -gt $total_gates ]; then
    final_gates=$EXPECTED_RESULTS
fi

if [ $passed_gates -ge $((final_gates - 1)) ]; then
    echo -e "   ${GREEN}HIGH ✅${NC} ($passed_gates/$final_gates quality gates passed)"
elif [ $passed_gates -ge $((final_gates / 2)) ]; then
    echo -e "   ${YELLOW}MODERATE ⚠️${NC} ($passed_gates/$final_gates quality gates passed)"
else
    echo -e "   ${RED}LOW ❌${NC} ($passed_gates/$final_gates quality gates passed)"
fi

echo ""
echo -e "${BOLD}📉 Test Coverage Insight${NC}"
if [[ -n "$least_covered_file" ]]; then
    # Color code the coverage percentage
    if (( $(echo "$min_coverage >= 80" | bc -l 2>/dev/null || [ "${min_coverage%.*}" -ge 80 ]) )); then
        coverage_status="${GREEN}✅${NC}"
    elif (( $(echo "$min_coverage >= 60" | bc -l 2>/dev/null || [ "${min_coverage%.*}" -ge 60 ]) )); then
        coverage_status="${YELLOW}⚠️${NC}"
    else
        coverage_status="${RED}❌${NC}"
    fi

    echo -e "   Least Covered Test: ${BOLD}$least_covered_title${NC} (${min_coverage}%) $coverage_status"
    echo -e "   Command to run: $least_covered_file"
else
    echo "   No coverage data available for analysis"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Quality Intelligence Platform analysis complete"
