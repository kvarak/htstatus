# HTStatus Documentation Architecture Guide

> **Purpose**: Decision matrix and guidelines for where to document what. Ensures consistent documentation practices and prevents information fragmentation.

## Documentation Hierarchy

### Quick Decision Matrix

| What to Document | Where to Put It | When to Update |
|------------------|----------------|----------------|
| **Development rules & standards** | [.project/rules.md](.project/rules.md) | When coding conventions or quality gates change |
| **Active tasks & priorities** | [.project/backlog.md](.project/backlog.md) | When starting/completing tasks or discovering new work |
| **Current project status** | [.project/progress.md](.project/progress.md) | After milestones, when metrics change, or status shifts |
| **System architecture** | [.project/architecture.md](.project/architecture.md) | When structure, data flow, or tech stack changes |
| **Strategic vision** | [.project/goals.md](.project/goals.md) | When project direction or objectives evolve |
| **Long-term planning** | [.project/plan.md](.project/plan.md) | When roadmap or priorities change |
| **AI agent prompts** | [.project/prompts.json](.project/prompts.json) | When agent workflows or validation rules change |
| **Completed task history** | [.project/history/](.project/history/) | When archiving completed tasks (never delete) |
| **User setup instructions** | [README.md](../README.md) | When setup process or dependencies change |
| **User-visible changes** | [CHANGELOG.md](../CHANGELOG.md) | For every release with new features or bug fixes |
| **Technical implementation** | [TECHNICAL.md](../TECHNICAL.md) | When patterns, architecture, or design decisions change |
| **Deployment procedures** | [DEPLOYMENT.md](../DEPLOYMENT.md) | When deployment process or infrastructure changes |
| **Detailed workflows** | [docs/](../docs/) | When creating comprehensive guides for complex processes |
| **Script documentation** | [scripts/README.md](../scripts/README.md) | When adding/modifying development utilities |
| **Config documentation** | [configs/README.md](../configs/README.md) | When changing configuration management |
| **Environment setup** | [environments/README.md](../environments/README.md) | When environment requirements change |

## Documentation Categories

### 1. Development Metadata (`.project/`)

**Purpose**: Internal project management and AI agent coordination

**Audience**: Developers, AI agents, project maintainers

**Key Files**:
- **rules.md**: Authoritative standards and conventions (READ THIS FIRST)
- **backlog.md**: Prioritized task tracking with 7-level priority system
- **progress.md**: Current state, metrics, accomplishments, blockers
- **architecture.md**: System structure, components, data flow
- **goals.md**: Strategic objectives and success criteria
- **plan.md**: Long-term roadmap and future opportunities
- **prompts.json**: AI agent behavior definitions
- **documentation-guide.md** _(this file)_: Meta-documentation about documentation

**Update Frequency**: Continuously during development

**Visibility**: Internal only (not user-facing)

### 2. Historical Documentation (`.project/history/`)

**Purpose**: Audit trail and learning from past decisions

**Audience**: Future developers, retrospective analysis

**Key Principles**:
- **Never delete**: Permanent record of project evolution
- Archive completed tasks from backlog.md here
- Document implementation decisions and their rationale
- Preserve bug investigations and resolutions

**Examples**:
- `backlog-done.md`: Completed task archive
- `bug-report-*.md`: Detailed bug investigations
- `implementation-guide-*.md`: Feature implementation retrospectives

**Update Frequency**: When archiving completed work

**Visibility**: Internal historical record

### 3. User Documentation (Root Level)

**Purpose**: Help users understand, install, and use HTStatus

**Audience**: End users, new developers, external contributors

**Key Files**:
- **README.md**: First-touch experience, quick start, feature overview
- **CHANGELOG.md**: Release history, what's new, upgrade notes
- **TECHNICAL.md**: Architecture for developers understanding the system
- **DEPLOYMENT.md**: How to deploy and configure HTStatus

**Update Frequency**: With user-visible changes

**Visibility**: Public-facing, version controlled

### 4. Specialized Documentation (`docs/`, `scripts/`, etc.)

**Purpose**: Deep-dive guides for specific topics

**Audience**: Developers working on specific features or subsystems

**Structure**:
- **docs/**: Cross-cutting technical guides (migration workflows, type synchronization)
- **scripts/README.md**: Development utilities documentation
- **configs/README.md**: Configuration management guide
- **environments/README.md**: Environment setup instructions

**Update Frequency**: When relevant subsystems change

**Visibility**: Internal developer resources

## Decision Framework

### "Where Should I Document This?"

Ask yourself these questions:

1. **Is it a development rule or standard?**
   - ✅ → [.project/rules.md](.project/rules.md)
   - Examples: coding conventions, quality gates, workflow commands

2. **Is it an active task or todo item?**
   - ✅ → [.project/backlog.md](.project/backlog.md)
   - Examples: bug fixes, feature implementations, technical debt

3. **Is it current project status or metrics?**
   - ✅ → [.project/progress.md](.project/progress.md)
   - Examples: test pass rates, deployment status, current focus areas

4. **Is it about system structure or architecture?**
   - ✅ → [.project/architecture.md](.project/architecture.md)
   - Examples: component diagrams, data flow, technology choices

5. **Is it a strategic goal or vision?**
   - ✅ → [.project/goals.md](.project/goals.md)
   - Examples: product vision, success criteria, objectives

6. **Is it long-term planning or roadmap?**
   - ✅ → [.project/plan.md](.project/plan.md)
   - Examples: future features, technical improvements, opportunities

7. **Is it for AI agent behavior?**
   - ✅ → [.project/prompts.json](.project/prompts.json)
   - Examples: prompt definitions, validation rules, agent workflows

8. **Is it completed work that needs archiving?**
   - ✅ → [.project/history/](.project/history/)
   - Examples: finished tasks, bug retrospectives, implementation guides

9. **Is it for users setting up the application?**
   - ✅ → [README.md](../README.md)
   - Examples: installation steps, quick start, feature overview

10. **Is it a user-visible change?**
    - ✅ → [CHANGELOG.md](../CHANGELOG.md)
    - Examples: new features, bug fixes, breaking changes

11. **Is it technical implementation details?**
    - ✅ → [TECHNICAL.md](../TECHNICAL.md)
    - Examples: architecture patterns, database schema, API design

12. **Is it about deployment and operations?**
    - ✅ → [DEPLOYMENT.md](../DEPLOYMENT.md)
    - Examples: server setup, configuration, monitoring

13. **Is it a detailed technical workflow?**
    - ✅ → [docs/](../docs/) or subsystem README
    - Examples: migration procedures, type synchronization guides

## Documentation Maintenance

### Regular Maintenance Schedule

**After Every Task Completion**:
- Update [.project/backlog.md](.project/backlog.md) with task status
- Update [.project/progress.md](.project/progress.md) with accomplishments
- Archive completed tasks to [.project/history/](.project/history/)
- Update relevant technical documentation if architecture changed

**After Every Release**:
- Update [CHANGELOG.md](../CHANGELOG.md) with user-visible changes
- Review and update [README.md](../README.md) if setup process changed
- Review and update [TECHNICAL.md](../TECHNICAL.md) if patterns changed

**Quarterly Reviews**:
- Review [.project/goals.md](.project/goals.md) - are objectives still relevant?
- Review [.project/plan.md](.project/plan.md) - update roadmap priorities
- Clean up [.project/backlog.md](.project/backlog.md) - remove stale tasks
- Audit [.project/rules.md](.project/rules.md) - update standards if needed

**Major Milestone Reviews**:
- Comprehensive update of [.project/architecture.md](.project/architecture.md)
- Update [TECHNICAL.md](../TECHNICAL.md) with lessons learned
- Archive major implementation guides to [.project/history/](.project/history/)

### Red Flags (Documentation Smells)

🚨 **Warning Signs of Documentation Problems**:

- **Duplication**: Same information in multiple places → Consolidate to single source
- **Inconsistency**: Different docs contradict each other → Establish authoritative source
- **Staleness**: Documentation references removed features → Regular reviews needed
- **Ambiguity**: Unclear where to document something → Use this guide's decision matrix
- **Orphaned Docs**: Files referenced nowhere → Delete or integrate into hierarchy
- **Missing Purpose**: File lacks clear audience/purpose → Add purpose header

### Documentation Quality Checklist

Before considering documentation complete:

- [ ] File has clear purpose statement at top
- [ ] Audience is explicitly identified
- [ ] Update frequency is documented
- [ ] Cross-references use relative links
- [ ] Information is in correct location per decision matrix
- [ ] No duplication with other documentation
- [ ] Last updated date is current
- [ ] Referenced by relevant files (if applicable)

## Documentation Templates

### Purpose Header Template
```markdown
> **Purpose**: [One sentence describing what this document is for]
> **Audience**: [Who should read this]
> **Update Frequency**: [When to update this]
```

### Cross-Reference Pattern
```markdown
See [relevant topic](relative/path/to/file.md) for details.
```

### Archive Entry Template
```markdown
## [Task ID] - Task Name

**Completed**: YYYY-MM-DD
**Duration**: X hours/days
**Impact**: [Brief description of what was achieved]

### Summary
[1-2 paragraph summary of the work]

### Key Decisions
- Decision 1 and rationale
- Decision 2 and rationale

### Lessons Learned
- Lesson 1
- Lesson 2

### Related Tasks
- [Task ID]: Task name
```

## Documentation Anti-Patterns

### Things to Avoid

❌ **Don't**: Duplicate rules in multiple places
✅ **Do**: Reference [.project/rules.md](.project/rules.md) as single source of truth

❌ **Don't**: Put development tasks in README.md
✅ **Do**: Keep user docs and developer tasks separate

❌ **Don't**: Mix completed and active tasks in backlog.md
✅ **Do**: Archive completed tasks to history/backlog-done.md

❌ **Don't**: Document current status in architecture.md
✅ **Do**: Put status in progress.md, structure in architecture.md

❌ **Don't**: Put strategic vision in TECHNICAL.md
✅ **Do**: Keep technical details separate from strategic goals

❌ **Don't**: Delete old documentation when it's no longer relevant
✅ **Do**: Archive to .project/history/ for future reference

❌ **Don't**: Create new documentation files without purpose headers
✅ **Do**: Always document the "why" and "who" for each file

## Integration with Development Workflow

### How AI Agents Use This Guide

1. **Before Documentation Updates**: Read this guide to determine correct file
2. **Decision Making**: Use decision matrix for "where to document"
3. **Quality Checks**: Validate against documentation quality checklist
4. **Cross-Referencing**: Follow linking patterns for consistency

### How Developers Use This Guide

1. **Onboarding**: Read this guide second (after README.md) to understand documentation structure
2. **Contributing**: Reference decision matrix when adding documentation
3. **Refactoring**: Use anti-patterns section to identify documentation debt
4. **Reviewing**: Check PRs against documentation quality checklist

---

**Last Updated**: 2025-01-27 (DOC-026 creation)
**Maintained By**: Project maintainers
**Referenced By**: .project/prompts.json, .project/rules.md
