# Project Tasks Directory

This directory contains detailed specifications for individual development tasks. Each task has its own file following the naming convention `<TASK-ID>.md`.

## Structure

```
.project/tasks/
├── BUG-001.md     # Bug fix tasks
├── FEAT-001.md    # Feature development tasks
├── REFACTOR-001.md # Code refactoring tasks
├── UI-001.md      # User interface tasks
├── DOC-001.md     # Documentation tasks
├── INFRA-001.md   # Infrastructure tasks
└── TEST-001.md    # Testing tasks
```

## Task File Format

Each task file contains:

- **Status**: Current task status (🎯 Ready, 🚀 Active, etc.)
- **Effort**: Time estimate
- **Priority**: Priority level (P0-P6)
- **Impact**: Expected impact description
- **Dependencies**: Prerequisites or blockers
- **Strategic Value**: Business/technical value

### Sections:
- **Problem Statement**: Clear description of what needs to be solved
- **Implementation**: Detailed steps and phases
- **Acceptance Criteria**: Success conditions
- **Expected Outcomes**: Benefits and results

## Lifecycle

1. **Creation**: New tasks get individual files via `add-to-backlog` prompt
2. **Reference**: `backlog.md` contains summary with links to task files
3. **Execution**: Agents read task files for detailed requirements
4. **Completion**: Task files are **deleted** when work is complete (git preserves history)

## File Management Rules

- **Create**: When adding new tasks to backlog
- **Read**: When planning or executing tasks
- **Delete**: When tasks are completed (use `update` prompt)
- **Never Edit**: Task requirements should be stable; create new tasks for changes

## Integration

- `backlog.md`: Summary view with priority and links to task files
- `prompts.json`: Updated to handle task file creation and deletion
- `htplanner-ai-agent.md`: Documents task file workflow for AI agents

This structure keeps the backlog clean and focused while providing detailed specifications when needed.