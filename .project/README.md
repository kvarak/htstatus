# HTStatus Development Methodology Guide

*This file provides a structured, AI-assisted development workflow for the HTStatus project.*

## Overview

This guide documents the professional development methodology for HTStatus, featuring systematic task execution, quality assurance, documentation standards, and infrastructure setup for efficient, maintainable development.

## Development Philosophy

HTStatus development follows a **structured, quality-gated methodology**:
- **Systematic Development**: Prompt-based workflows for consistent task execution
- **Quality Assurance**: Testing gates before completion
- **Documentation Integrity**: Clear separation of user, technical, and development documentation
- **Infrastructure Reliability**: Standardized development and deployment patterns

## Development Workflow

### Core Development Cycle

1. **Plan**: Analyze tasks and create an implementation strategy
2. **Execute**: Implement according to plan with quality gates
3. **Review**: Validate completeness and alignment
4. **Update**: Update project documentation and status

### AI-Assisted Development Setup

- Use VS Code with an AI assistant extension for prompt-based workflows
- Access structured prompts from `.project/prompts.json` (if present)

### Workflow Commands

- **Plan**: Analyze next development task with strategic alignment
- **Execute**: Implement planned solution with testing and documentation
- **Review**: Validate previous work against requirements
- **Update**: Update project status and planning documents

## File Organization

### .project Directory Structure

**Active Documentation** (keep in `.project/`):
- `README.md` - Development methodology guide
- `architecture.md` - Current system architecture
- `backlog.md` - Active task backlog
- `goals.md` - Strategic goals and objectives
- `plan.md` - Development plan and requirements
- `progress.md` - Current progress tracking
- `prompts.json` - AI workflow prompts

**Historical Documentation** (move to `.project/history/`):
- `backlog-done.md` - Completed tasks archive
- Implementation guides (e.g., `PWA-IMPLEMENTATION.md`)
- Bug investigation reports (e.g., `BUG-001-REVIEW.md`)
- "How I implemented" retrospectives
- Archived analysis documents

**Rule**: Any documentation describing past implementation details, debugging processes, or historical context should be moved to `.project/history/` to keep the main directory focused on current development needs.

---

*This methodology ensures maintainable, high-quality development for HTStatus.*