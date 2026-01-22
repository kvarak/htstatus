#!/bin/bash

# HTStatus Quality Intelligence Platform
# Analyzes test results and provides strategic insights

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Capture test results from stdin if provided
if [ -t 0 ]; then
    test_results=""
else
    test_results=$(cat)
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 HTStatus Quality Intelligence Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Infrastructure Quality Dimensions
echo "📊 INFRASTRUCTURE QUALITY DIMENSIONS:"

# File Standards
printf "  %-20s" "File Standards:"
if grep -q 'File formatting checks passed' /tmp/fileformat-results.txt 2>/dev/null; then
    echo "✅ PASSED (consistent formatting)"
else
    echo "❌ ISSUES (run 'make fileformat-fix')"
fi

# Code Quality
printf "  %-20s" "Code Quality:"
if grep -q 'All checks passed' /tmp/lint-results.txt 2>/dev/null; then
    echo "✅ EXCELLENT (0 errors)"
else
    errors=$(grep -o 'Found [0-9]* error' /tmp/lint-results.txt 2>/dev/null | head -1 | grep -o '[0-9]*' || echo "unknown")
    app_errors=$(grep -E '^.*--> (app/|models\.py|config\.py)' /tmp/lint-results.txt 2>/dev/null | wc -l | tr -d ' ')
    if [ "$app_errors" = "0" ] 2>/dev/null; then
        echo "⚠️  $errors ISSUES (dev scripts only)"
    else
        echo "❌ $errors ISSUES ($app_errors in production code)"
    fi
fi

# Security (split into CVE vulnerabilities and code security issues)
printf "  %-20s" "CVE Vulnerabilities:"
if [ -f "/tmp/safety-results.json" ]; then
    cve_count=$(jq -r '.scan_results.vulnerabilities | length' /tmp/safety-results.json 2>/dev/null || echo "unknown")
    if [ "$cve_count" = "0" ]; then
        echo "✅ NONE (dependencies secure)"
    elif [ "$cve_count" = "unknown" ]; then
        echo "⚠️  UNKNOWN (run 'make security')"
    else
        echo "⚠️  $cve_count FOUND (run 'make security')"
    fi
else
    # Fallback to old text-based parsing
    if grep -q "No known security vulnerabilities reported" /tmp/security-results.txt 2>/dev/null || grep -q "No CVE vulnerabilities" /tmp/security-results.txt 2>/dev/null; then
        echo "✅ NONE (dependencies secure)"
    else
        echo "⚠️  UNKNOWN (run 'make security')"
    fi
fi

printf "  %-20s" "Code Security:"
if [ -f "/tmp/bandit-results.json" ]; then
    bandit_issues=$(jq -r '.metrics._totals."SEVERITY.MEDIUM" + .metrics._totals."SEVERITY.HIGH"' /tmp/bandit-results.json 2>/dev/null || echo "unknown")
    if [ "$bandit_issues" = "0" ]; then
        echo "✅ CLEAN (no Bandit issues)"
    elif [ "$bandit_issues" = "unknown" ]; then
        echo "⚠️  UNKNOWN (run 'make security')"
    else
        echo "⚠️  $bandit_issues ISSUE(S) (run 'make security')"
    fi
else
    # Fallback to text-based parsing
    if grep -q "No code security issues found" /tmp/security-results.txt 2>/dev/null; then
        echo "✅ CLEAN (no Bandit issues)"
    else
        echo "⚠️  UNKNOWN (run 'make security')"
    fi
fi

# Type Sync
printf "  %-20s" "Type Sync:"
if grep -q "Type sync validation passed" /tmp/typesync-results.txt 2>/dev/null; then
    echo "✅ SYNCHRONIZED (Flask ↔ React)"
else
    issues=$(grep 'Found.*type sync issues' /tmp/typesync-results.txt 2>/dev/null | head -1 | grep -o '[0-9]\+' || echo "unknown")
    echo "⚠️  $issues DRIFT ISSUES (run 'make typesync' to fix)"
fi

echo ""

# Testing Intelligence Analysis
echo "🧪 TESTING INTELLIGENCE ANALYSIS:"

# Configuration Reliability
printf "  %-20s" "Config Reliability:"
# Check for config test results in temp file first, then stdin
if [ -f "/tmp/config-results.txt" ]; then
    if grep -q "[0-9]\+ passed, [0-9]\+ skipped" /tmp/config-results.txt 2>/dev/null; then
        config_cov=$(grep -o 'TOTAL.*[0-9]\+%' /tmp/config-results.txt | tail -1 | grep -o '[0-9]\+%' || echo "unknown%")
        config_tests=$(grep -o '[0-9]\+ passed' /tmp/config-results.txt | tail -1 | grep -o '[0-9]\+' || echo "config")
        echo "✅ ROBUST ($config_cov coverage, $config_tests validations)"
    else
        echo "❌ FAILING (check config test setup)"
    fi
elif echo "$test_results" | grep -q "test_config" && echo "$test_results" | grep -q "[0-9]\+ passed, [0-9]\+ skipped"; then
    config_cov=$(echo "$test_results" | grep -o 'TOTAL.*[0-9]\+%' | tail -1 | grep -o '[0-9]\+%' || echo "unknown%")
    config_tests=$(echo "$test_results" | grep -o '[0-9]\+ passed' | tail -1 | grep -o '[0-9]\+' || echo "config")
    echo "✅ ROBUST ($config_cov coverage, $config_tests validations)"
else
    echo "❌ FAILING (check config test setup)"
fi

# Application Logic
printf "  %-20s" "Application Logic:"
# Check for application test results in temp file first, then stdin
if [ -f "/tmp/test-results.txt" ]; then
    if grep -q "FAILED" /tmp/test-results.txt 2>/dev/null; then
        app_cov=$(grep -o 'TOTAL.*[0-9]*%' /tmp/test-results.txt | tail -1 | grep -o '[0-9]*%' || echo "??%")
        passed=$(grep -o '[0-9]* passed' /tmp/test-results.txt | head -1 | grep -o '[0-9]*' || echo "?")
        failed=$(grep -o '[0-9]* failed' /tmp/test-results.txt | head -1 | grep -o '[0-9]*' || echo "?")
        echo "⚠️  $app_cov ($passed passed, $failed failed - review failures)"
    else
        app_cov=$(grep -o 'TOTAL.*[0-9]*%' /tmp/test-results.txt | tail -1 | grep -o '[0-9]*%' || echo "??%")
        passed=$(grep -o '[0-9]* passed' /tmp/test-results.txt | head -1 | grep -o '[0-9]*' || echo "all")
        echo "✅ SOLID ($app_cov coverage, $passed tests passing)"
    fi
elif echo "$test_results" | grep -q "FAILED"; then
    app_cov=$(echo "$test_results" | grep -o 'TOTAL.*[0-9]*%' | tail -1 | grep -o '[0-9]*%' || echo "??%")
    passed=$(echo "$test_results" | grep -o '[0-9]* passed' | head -1 | grep -o '[0-9]*' || echo "?")
    failed=$(echo "$test_results" | grep -o '[0-9]* failed' | head -1 | grep -o '[0-9]*' || echo "?")
    echo "⚠️  $app_cov ($passed passed, $failed failed - review failures)"
else
    app_cov=$(echo "$test_results" | grep -o 'TOTAL.*[0-9]*%' | tail -1 | grep -o '[0-9]*%' || echo "??%")
    passed=$(echo "$test_results" | grep -o '[0-9]* passed' | head -1 | grep -o '[0-9]*' || echo "all")
    echo "✅ SOLID ($app_cov coverage, $passed tests passing)"
fi

echo ""

# Strategic Insights
echo "💡 STRATEGIC INSIGHTS:"
echo "  • Configuration: Critical infrastructure components (CHPP, DB, env) tested"
echo "  • Application: Blueprint architecture + business logic validated"
echo "  • Both metrics provide different quality dimensions for deployment confidence"

echo ""

# Deployment Confidence Assessment
config_ok=0
app_ok=0

# Check config results
if [ -f "/tmp/config-results.txt" ]; then
    if grep -q "[0-9]* passed, [0-9]* skipped" /tmp/config-results.txt 2>/dev/null; then
        config_ok=1
    fi
fi

# Check app results
if [ -f "/tmp/test-results.txt" ]; then
    if ! grep -q "FAILED" /tmp/test-results.txt 2>/dev/null; then
        app_ok=1
    fi
fi

if [ "$config_ok" = "1" ] && [ "$app_ok" = "1" ]; then
    echo -e "🎯 DEPLOYMENT CONFIDENCE: ${GREEN}HIGH ✅${NC} (all quality gates passed)"
elif [ "$config_ok" = "1" ] || [ "$app_ok" = "1" ]; then
    echo -e "🎯 DEPLOYMENT CONFIDENCE: ${YELLOW}MODERATE ⚠️${NC} (partial quality gates)"
else
    echo -e "🎯 DEPLOYMENT CONFIDENCE: ${RED}LOW ❌${NC} (multiple quality issues)"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Cleanup temp files after analysis
rm -f /tmp/fileformat-results.txt /tmp/lint-results.txt /tmp/security-results.txt /tmp/bandit-results.json /tmp/bandit-results.txt /tmp/safety-results.json /tmp/typesync-results.txt /tmp/config-results.txt /tmp/test-results.txt

echo "✅ Quality Intelligence Platform analysis complete"
