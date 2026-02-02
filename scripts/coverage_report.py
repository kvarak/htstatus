#!/usr/bin/env python3
"""Coverage analysis script for Quality Intelligence reporting.

Analyzes test coverage to identify files that need testing focus.
Provides actionable insights for improving coverage.
"""

import argparse
import sys

import coverage


def get_coverage_analysis(quiet=False):
    """Get detailed coverage analysis with actionable insights."""
    try:
        c = coverage.Coverage()
        c.load()

        # Get overall coverage - suppress output in quiet mode
        if quiet:
            import io
            from contextlib import redirect_stdout
            with redirect_stdout(io.StringIO()):
                total_coverage = c.report(show_missing=False, skip_empty=True)
        else:
            total_coverage = c.report(show_missing=False, skip_empty=True, file=sys.stdout)

        print("\n" + "="*70)
        print("COVERAGE ANALYSIS FOR TEST PRIORITIZATION")
        print("="*70)
        print(f"Overall Coverage: {total_coverage:.2f}%")

        # Target for 50% coverage
        target_coverage = 50.0
        gap = max(0, target_coverage - total_coverage)
        print(f"Gap to 50% target: {gap:.2f}%")

        # Analyze individual files
        data = c.get_data()
        file_stats = []

        for filename in sorted(data.measured_files()):
            # Focus on application code (not tests) and only Python files
            if any(pattern in filename for pattern in ['/tests/', '__pycache__', '.pyc']):
                continue

            # Only analyze Python source files
            if not filename.endswith('.py'):
                continue

            try:
                analysis = c.analysis(filename)
                executed_lines = set(analysis[1])
                missing_lines = set(analysis[2])
                total_lines = len(executed_lines) + len(missing_lines)

                if total_lines > 0:
                    coverage_pct = (len(executed_lines) / total_lines) * 100
                    missing_count = len(missing_lines)

                    # Calculate impact score (low coverage + high line count = high impact)
                    impact_score = missing_count * (100 - coverage_pct) / 100

                    file_stats.append({
                        'file': filename.replace('/Users/kvarak/repos/kvarak/htstatus-2.0/', ''),
                        'coverage': coverage_pct,
                        'total_lines': total_lines,
                        'missing_lines': missing_count,
                        'impact_score': impact_score
                    })
            except Exception as e:
                print(f"Error analyzing {filename}: {e}", file=sys.stderr)

        # Sort by impact score (highest impact first)
        file_stats.sort(key=lambda x: x['impact_score'], reverse=True)

        return total_coverage, gap, file_stats

    except Exception as e:
        print(f"Error loading coverage data: {e}", file=sys.stderr)
        print("Make sure to run tests first: uv run pytest", file=sys.stderr)
        return None, None, []


def print_priority_targets(file_stats, limit=10):
    """Print high-priority files for testing."""
    print(f"\nTOP {limit} PRIORITY FILES FOR TEST COVERAGE:")
    print("-" * 70)
    print(f"{'File':<40} {'Coverage':<10} {'Missing':<8} {'Impact':<8}")
    print("-" * 70)

    for _i, stats in enumerate(file_stats[:limit], 1):
        file_short = stats['file']
        if len(file_short) > 37:
            file_short = "..." + file_short[-34:]

        print(f"{file_short:<40} {stats['coverage']:6.1f}% {stats['missing_lines']:6d} {stats['impact_score']:6.1f}")


def print_category_analysis(file_stats):
    """Print analysis by file category."""
    print("\nCOVERAGE BY CATEGORY:")
    print("-" * 50)

    categories = {
        'blueprints': [],
        'utils': [],
        'models': [],
        'chpp': [],
        'other': []
    }

    for stats in file_stats:
        file_path = stats['file']
        if 'blueprints/' in file_path:
            categories['blueprints'].append(stats)
        elif 'utils.py' in file_path:
            categories['utils'].append(stats)
        elif 'models.py' in file_path:
            categories['models'].append(stats)
        elif 'chpp/' in file_path:
            categories['chpp'].append(stats)
        else:
            categories['other'].append(stats)

    for category, files in categories.items():
        if files:
            avg_coverage = sum(f['coverage'] for f in files) / len(files)
            total_missing = sum(f['missing_lines'] for f in files)
            print(f"{category.capitalize():<15}: {avg_coverage:6.1f}% avg, {total_missing:4d} missing lines")


def print_recommendations(file_stats, gap):
    """Print specific recommendations for improvement."""
    print("\nRECOMMENDATIONS:")
    print("-" * 50)

    if gap > 0:
        # Estimate lines needed to cover for 50% target
        high_impact = [f for f in file_stats[:5] if f['coverage'] < 30]

        if high_impact:
            print("🎯 QUICK WINS - Focus on these high-impact files:")
            for f in high_impact[:3]:
                lines_to_cover = min(f['missing_lines'], int(f['missing_lines'] * 0.3))
                print(f"   • {f['file'].split('/')[-1]}: Add ~{lines_to_cover} lines of tests")

        # Look for blueprint routes (often easy to test)
        blueprint_files = [f for f in file_stats if 'blueprints/' in f['file'] and f['coverage'] < 40]
        if blueprint_files:
            print("\n🚀 BLUEPRINT ROUTES - Often easy test targets:")
            for f in blueprint_files[:3]:
                print(f"   • {f['file'].split('/')[-1]}: {f['coverage']:.1f}% coverage")

        # Utils functions are often testable
        utils_files = [f for f in file_stats if 'utils' in f['file'] and f['missing_lines'] > 50]
        if utils_files:
            print("\n🔧 UTILITY FUNCTIONS - High-value testing:")
            for f in utils_files[:2]:
                print(f"   • {f['file'].split('/')[-1]}: {f['missing_lines']} uncovered lines")
    else:
        print("✅ Coverage target met! Focus on quality and edge cases.")


def main():
    """Main script entry point."""
    parser = argparse.ArgumentParser(description="Generate coverage analysis for test prioritization")
    parser.add_argument("--limit", "-l", type=int, default=10,
                       help="Number of priority files to show (default: 10)")
    parser.add_argument("--json", action="store_true",
                       help="Output in JSON format")
    args = parser.parse_args()

    if args.json:
        # JSON mode - suppress coverage table output
        import io
        from contextlib import redirect_stdout

        with redirect_stdout(io.StringIO()):
            total_coverage, gap, file_stats = get_coverage_analysis()

        if total_coverage is None:
            sys.exit(1)

        import json
        output = {
            "total_coverage": total_coverage,
            "gap_to_target": gap,
            "priority_files": file_stats[:args.limit]
        }
        print(json.dumps(output, indent=2))
    else:
        # Normal mode - show coverage table and analysis
        total_coverage, gap, file_stats = get_coverage_analysis()

        if total_coverage is None:
            sys.exit(1)

        print_priority_targets(file_stats, args.limit)
        print_category_analysis(file_stats)
        print_recommendations(file_stats, gap)

        print("\n" + "="*70)
        print("Run this script after 'uv run pytest' to get updated analysis")
        print("Usage: uv run python scripts/coverage_report.py --limit 15")
        print("="*70)


if __name__ == "__main__":
    main()
