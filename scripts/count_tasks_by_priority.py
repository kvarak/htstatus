#!/usr/bin/env uv run python3
"""
Count tasks by priority level in the project backlog.

Inspired by: grep -e "^\\#\\# " -e "^\\- \\*\\*\\[" .project/backlog.md

Usage:
    uv run python scripts/count_tasks_by_priority.py
    uv run python scripts/count_tasks_by_priority.py --detailed
    uv run python scripts/count_tasks_by_priority.py --summary-only
"""

import argparse
import re
from pathlib import Path


def parse_backlog(file_path: Path) -> dict:
    """Parse backlog.md and return task counts by priority."""
    if not file_path.exists():
        raise FileNotFoundError(f"Backlog file not found: {file_path}")

    content = file_path.read_text()
    lines = content.split('\n')

    # Pattern for priority headers: ## P0: Production-Breaking 🚨
    priority_pattern = re.compile(r'^## (P\d+):\s*(.+)')
    # Pattern for task lines: - **[TASK-ID]** Description
    task_pattern = re.compile(r'^\- \*\*\[([A-Z]+-\d+)\]\*\*\s*(.+)')

    priorities = {}
    current_priority = None

    for line_num, line in enumerate(lines, 1):
        # Check for priority header
        priority_match = priority_pattern.match(line)
        if priority_match:
            priority_level = priority_match.group(1)
            priority_title = priority_match.group(2)
            current_priority = priority_level
            priorities[current_priority] = {
                'title': priority_title,
                'tasks': [],
                'line_num': line_num
            }
            continue

        # Check for task line
        task_match = task_pattern.match(line)
        if task_match and current_priority:
            task_id = task_match.group(1)
            task_desc = task_match.group(2)
            priorities[current_priority]['tasks'].append({
                'id': task_id,
                'description': task_desc,
                'line_num': line_num
            })

    return priorities


def print_summary(priorities: dict) -> None:
    """Print a summary of task counts."""
    total_tasks = sum(len(p['tasks']) for p in priorities.values())

    print("📊 Task Count Summary")
    print("=" * 50)

    for priority_level in sorted(priorities.keys()):
        priority_info = priorities[priority_level]
        task_count = len(priority_info['tasks'])
        title = priority_info['title']

        # Format with emoji and status
        status_emoji = "✅" if task_count == 0 else "📋"
        print(f"{priority_level}: {task_count:2d} tasks {status_emoji} - {title}")

    print("-" * 50)
    print(f"Total: {total_tasks} tasks across {len(priorities)} priority levels")


def print_detailed(priorities: dict) -> None:
    """Print detailed breakdown with task IDs."""
    total_tasks = sum(len(p['tasks']) for p in priorities.values())

    print("📋 Detailed Task Breakdown")
    print("=" * 70)

    for priority_level in sorted(priorities.keys()):
        priority_info = priorities[priority_level]
        task_count = len(priority_info['tasks'])
        title = priority_info['title']

        print(f"\n{priority_level}: {title} ({task_count} tasks)")
        print("-" * 60)

        if task_count == 0:
            print("  ✅ No tasks")
        else:
            # Group by task type
            task_types = {}
            for task in priority_info['tasks']:
                task_type = task['id'].split('-')[0]
                if task_type not in task_types:
                    task_types[task_type] = []
                task_types[task_type].append(task)

            for task_type in sorted(task_types.keys()):
                type_tasks = task_types[task_type]
                print(f"  {task_type}: {len(type_tasks)} tasks")
                for task in type_tasks:
                    # Truncate long descriptions
                    desc = task['description']
                    if len(desc) > 80:
                        desc = desc[:77] + "..."
                    print(f"    - {task['id']}: {desc}")

    print(f"\n{'=' * 70}")
    print(f"Total: {total_tasks} tasks across {len(priorities)} priority levels")


def print_summary_line(priorities: dict) -> None:
    """Print a one-line summary suitable for backlog.md updates."""
    total_tasks = sum(len(p['tasks']) for p in priorities.values())
    priority_count = len(priorities)

    # Find highest priority level
    max_priority = max(int(p[1:]) for p in priorities) if priorities else 0

    distribution = []
    for i in range(max_priority + 1):
        priority_key = f"P{i}"
        if priority_key in priorities:
            count = len(priorities[priority_key]['tasks'])
            distribution.append(f"{priority_key}={count}")
        else:
            distribution.append(f"{priority_key}=0")

    print(f"**{total_tasks} tasks across {priority_count} priority levels (P0-P{max_priority})**")
    print(f"📊 Status: {', '.join(distribution)}")


def main():
    parser = argparse.ArgumentParser(description="Count tasks by priority level")
    parser.add_argument("--detailed", "-d", action="store_true",
                       help="Show detailed breakdown with task IDs")
    parser.add_argument("--summary-only", "-s", action="store_true",
                       help="Show only summary counts")
    parser.add_argument("--line", "-l", action="store_true",
                       help="Show one-line summary for backlog.md")
    parser.add_argument("--backlog", default=".project/backlog.md",
                       help="Path to backlog.md file (default: .project/backlog.md)")

    args = parser.parse_args()

    try:
        backlog_path = Path(args.backlog)
        priorities = parse_backlog(backlog_path)

        if args.line:
            print_summary_line(priorities)
        elif args.detailed:
            print_detailed(priorities)
        elif args.summary_only:
            print_summary(priorities)
        else:
            # Default: summary + basic stats
            print_summary(priorities)
            print()
            print("💡 Use --detailed for task IDs, --line for backlog.md format")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
