#!/bin/bash

# HTStatus Quality Intelligence JSON Generator
# Creates standardized QI JSON files using jq for proper formatting

usage() {
    echo "Usage: $0 <output_file> <title> <makecommand> <status> <warnings> <errors> [metric] [details] [extra_fields...]"
    echo ""
    echo "Required fields:"
    echo "  output_file  - Path to output JSON file"
    echo "  title        - Human readable gate name"
    echo "  makecommand  - Make command to run this gate"
    echo "  status       - PASSED, ISSUES, or FAILED"
    echo "  warnings     - Number of warnings (integer)"
    echo "  errors       - Number of errors (integer)"
    echo ""
    echo "Optional fields:"
    echo "  metric       - Summary metric string"
    echo "  details      - Additional details string"
    echo "  extra_fields - Additional key=value pairs"
    echo ""
    echo "Examples:"
    echo "  $0 out/tests/lint.json 'Code Quality' 'make lint' PASSED 0 0 '0 errors' 'excellent code quality'"
    echo "  $0 out/tests/security.json 'Security Analysis' 'make security' PASSED 0 0 'clean' 'no issues' cve=NONE bandit=CLEAN"
    exit 1
}

if [ $# -lt 6 ]; then
    usage
fi

output_file="$1"
title="$2"
makecommand="$3"
status="$4"
warnings="$5"
errors="$6"
metric="${7:-}"
details="${8:-}"

# Validate required fields
if [ -z "$output_file" ] || [ -z "$title" ] || [ -z "$makecommand" ] || [ -z "$status" ]; then
    echo "Error: Missing required fields"
    usage
fi

# Validate status values
if [[ ! "$status" =~ ^(PASSED|ISSUES|FAILED)$ ]]; then
    echo "Error: Invalid status '$status'. Must be PASSED, ISSUES, or FAILED"
    exit 1
fi

# Validate numeric fields
if ! [[ "$warnings" =~ ^[0-9]+$ ]] || ! [[ "$errors" =~ ^[0-9]+$ ]]; then
    echo "Error: warnings and errors must be integers"
    exit 1
fi

# Create output directory if needed
mkdir -p "$(dirname "$output_file")"

# Build base JSON object
json_obj=$(jq -n \
    --arg title "$title" \
    --arg makecommand "$makecommand" \
    --arg status "$status" \
    --argjson warnings "$warnings" \
    --argjson errors "$errors" \
    '{
        title: $title,
        makecommand: $makecommand,
        status: $status,
        warnings: $warnings,
        errors: $errors
    }')

# Add optional fields
if [ -n "$metric" ]; then
    json_obj=$(echo "$json_obj" | jq --arg metric "$metric" '. + {metric: $metric}')
fi

if [ -n "$details" ]; then
    json_obj=$(echo "$json_obj" | jq --arg details "$details" '. + {details: $details}')
fi

# Add extra key=value fields
shift 8  # Remove the first 8 arguments
for extra_field in "$@"; do
    if [[ "$extra_field" =~ ^([^=]+)=(.*)$ ]]; then
        key="${BASH_REMATCH[1]}"
        value="${BASH_REMATCH[2]}"
        json_obj=$(echo "$json_obj" | jq --arg key "$key" --arg value "$value" '. + {($key): $value}')
    else
        echo "Warning: Invalid extra field format '$extra_field', expected key=value"
    fi
done

# Write formatted JSON to file
echo "$json_obj" | jq '.' > "$output_file"

echo "✅ QI JSON written to $output_file"
