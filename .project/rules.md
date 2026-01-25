# HTStatus Development Rules

> **Purpose**: Authoritative source for all development standards, coding conventions, and quality gates for the HTStatus project. Referenced by [prompts.json](prompts.json) for AI agent behavior.

## Core Development Standards

### Architectural Simplification Principles
**Hierarchy**: Holistic view >> Reduce complexity >> Reduce waste >> Consolidate & eliminate duplication

- **Reduce complexity**: Maintain single responsibility per module/script, clear interfaces, avoid monolithic structures
- **Reduce waste**: Remove unused code, eliminate redundant logic within components, clean up obsolete patterns
- **Consolidate duplication**: Merge identical patterns/functions/logic, **NOT** merge distinct tools with different purposes
- **Separation of concerns**: Keep tools/modules focused on single responsibilities (e.g., qi-json.sh for JSON generation, pytest-qi-parser.sh for format conversion, quality-intelligence.sh for reporting)
- **Anti-pattern**: Merging well-separated tools into monoliths (like old routes.py) increases complexity

### Quality Gates
- **Testing**: Run `make test-all` before marking tasks complete (no coverage loss or new failures)
- **Linting**: Run `make lint` before committing (address critical issues)
- **Python**: Always use `uv run python` (never direct python calls)
- **Commands**: Use `make help` for available workflow commands

### Database Standards
- All schema changes must maintain backwards compatibility
- Test migrations on production-like structure copies before deployment
- Use `uv run python scripts/database/apply_migrations.py` for safe migrations
- Document migration rationale in version files

### Security Standards
- Never commit secrets (API keys, tokens, passwords) - use environment variables or config.py (gitignored)
- Subprocess usage limited to static dev tooling only (git version detection)
- Document security rationale for Bandit B404/B607/B603 skips

## Documentation Standards

### Task ID Format
**CRITICAL**: All task IDs must follow [CATEGORY]-[NUMBER] format using existing categories:
- **TEST-**: Testing infrastructure, fixtures, coverage
- **INFRA-**: Infrastructure, deployment, operations, CI/CD
- **UI-**: User interface, design system, frontend
- **REFACTOR-**: Code cleanup, architecture improvements
- **BUG-**: Bug fixes and functionality regressions
- **FEAT-**: New features and functionality
- **DOC-**: Documentation, guides, cleanup
**Never invent new categories** - use existing numbering sequence for category

### Project Documentation Structure

**Development Metadata** (`.project/`)
- **architecture.md**: Update with structural changes
- **plan.md**: Mark completed items and update status
- **backlog.md**: Update with new tasks and milestones
- **progress.md**: Update accomplishments and next steps
- **goals.md**: Strategic vision and objectives - keep up to date
- **prompts.json**: AI agent prompt definitions
- **rules.md** _(this file)_: Development standards and rules

**Historical Documentation** (`.project/history/`)
- Implementation guides, bug reviews, retrospectives
- Completed task archives from backlog.md
- Never delete - audit trail for project decisions

**User Documentation** (root level)
- **README.md**: User-focused setup and usage guide
- **CHANGELOG.md**: Notable changes, new features, bug fixes
- **TECHNICAL.md**: Technical architecture and implementation details
- **DEPLOYMENT.md**: Deployment procedures and configuration

**Specialized Documentation**
- **docs/**: Detailed technical guides and workflows
- **scripts/README.md**: Development scripts and utilities
- **configs/README.md**: Configuration management
- **File Structure
- **`.project/`**: Development metadata (architecture, backlog, progress, plan, goals, prompts, rules)
- **`.project/history/`**: Completed tasks, implementation guides, retrospectives (never delete)
- **Root**: User docs (README, CHANGELOG, TECHNICAL, DEPLOYMENT)
- **`docs/`**: Technical guides and specialized workflows

### Update Triggers
- **architecture.md**: System structure, data flow, or tech stack changes
- **backlog.md**: Task status changes (starting, completing, discovering)
- **progress.md**: Milestones, accomplishments, status changes
- **plan.md**: Strategic direction or goal changes
- **README.md**: Setup process or user-facing feature changes
- **TECHNICAL.md**: Implementation patterns or technical detail changes
- **CHANGELOG.md**: All user-visible changes, features, bug fixes
# Standard pattern throughout app
chpp = CHPP(consumer_key, consumer_secret, session['access_key'], session['access_secret'])
current_user = chpp.user()
team = chpp.team(ht_id=teamid)
players = team.players  # Live data from Hattrick
```

### File Organization Rules

**Backend Structure**
- `/app/routes_bp.py`: Blueprint organization and registration
- `/app/blueprints/`: Modular route handlers by feature
- `/models.py`: SQLAlchemy models defining database schema
- `/config.py`: Configuration management (not tracked in git)

**Frontend Structure**
- `/app/templates/`: Jinja2 templates for legacy frontend (Flask-Bootstrap 3.x)
- `/src/`: React components for modern frontend (TailwindCSS, TypeScript)
- `/src/types/index.ts`: TypeScript interfaces matching database models

**Test Structure**
- `/tests/conftest.py`: Central test fixture configuration
- `/tests/test_*.py`: Test suites organized by feature area
- Transaction isolation pattern for database tests

## Task Management Rules

### For AI Agents

1. **ALWAYS read .project/ docs before starting work**
   - Read `backlog.md` to understand active tasks
   - Read `rules.md` (this file) for development standards
   - Read relevant documentation for context
Patterns
- **Debugging**: Use `dprint(level, msg)` instead of print() (levels 0-3 controlled by DEBUG_LEVEL config)
- **Routes**: Use `create_page(template='...', title='...', ...)` pattern consistently
- **CHPP**: Initialize with `CHPP(consumer_key, consumer_secret, session['access_key'], session['access_secret'])`

### File Organization
- **Backend**: `/app/blueprints/` (modular routes), `/models.py` (SQLAlchemy), `/config.py` (gitignored)
- **Frontend**: `/app/templates/` (Jinja2/Bootstrap3), `/src/` (React/TypeScript/TailwindCSS)
- **Tests**: `/tests/conftest.py` (fixtures), `/tests/test_*.py` (transaction isolation pattern)

# Make commands
make help  # See all available commands
```

### Configuration Requirements
- **config.py**: Must contain Hattrick CHPP credentials (CONSUMER_KEY, CONSUMER_SECRETS, CALLBACK_URL)
- **PostgreSQL**: Required database with connection string in SQLALCHEMY_DATABASE_URI
- **Debug Levels**: Use DEBUG_LEVEL config (0-3) with `dprint()` function

### Git Workflow
- Commit messages follow conventional format
- Group related changes into logical commits
- Test before committing
- Keep commits focused and atomic

## Critical Patterns

### Hattrick Domain Knowledge
- **Player Skills**: 7 core skills (keeper, defender, playmaker, winger, passing, scorer, set_pieces)
- **Match Roles**: 15+ field positions (GK=100, RB=101, etc.) in `HTmatchrole` constants
- **Match Types**: League matches, cups, friendlies with IDs in `HTmatchtype` constants
- **Skill Development**: Track player progression with `player_diff()` functions

### Database Architecture
- **Multi-team Support**: Users can own multiple teams via `session['all_teams']`
- **Historical Player Data**: `Players` table tracks skill changes by `data_date`
- **Player Grouping**: Custom groups via `PlayerGroup` and `PlayerSetting` junction
- **Match Analysis**: `Match` and `MatchPlay` tables for performance tracking

### Integration Points
- **Hattrick OAuth**: Users authenticate via Hattrick, tokens in session
- **Real-time Data**: Player data fetched live from CHPP API during `/update` route
- **Session State**: Shared between Flask routes for user context
- **Database IDs**: All Hattrick IDs use external `ht_id` fields

## Technology Stack

### Backend
- **Framework**: Flask 2.x with Blueprint architecture
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Hattrick OAuth via pychpp library
- **Testing**: pytest with transaction isolation
- **Deployment**: Docker containers with uWSGI

### Frontend
- **Legacy**: Server-rendered Jinja2 templates with Flask-Bootstrap 3.x
- **Modern**: React SPA with Vite, TypeScript, Radix UI, TailwindCSS
- **Visualization**: Chart.js for player skill progression
- **PWA**: Service Worker with cache-first strategy

### DevOps
- **Common Commands
- `./scripts/run.sh` - Flask dev server (port 5000)
- `npm run dev` - React dev server (port 8080)
- `make test-all` - Run full test suite with coverage
- `make lint` - Run linter
- `uv run python scripts/manage.py db migrate/upgrade` - Database migrations

### Configuration Requirements
- **config.py**: CHPP credentials (CONSUMER_KEY, CONSUMER_SECRETS, CALLBACK_URL), PostgreSQL connection string
- **Environment**: Use DEBUG_LEVEL config (0-3) to control `dprint()` verbosity

### Git Standards
- Conventional commit messages, logical grouping, test before commit, atomic changesDomain Knowledge

### Hattrick Integration
- **Skills**: 7 core (keeper, defender, playmaker, winger, passing, scorer, set_pieces)
- **Positions**: 15+ field roles (GK=100, RB=101, etc.) in `HTmatchrole` constants
- **Match Types**: League, cups, friendlies with IDs in `HTmatchtype` constants
- **Authentication**: OAuth via pychpp, tokens stored in session
- **Data Sync**: Live player data from CHPP API via `/update` route
- **pychpp Reference**: Local git repository in `pychpp/` folder - checkout matching version tag to verify API compatibility and method signatures when debugging CHPP integration issues

### Database Architecture
- **Multi-team**: `session['all_teams']` for user's teams
- **Historical**: `Players` table tracks skills by `data_date`
- **Grouping**: `PlayerGroup` + `PlayerSetting` junction table
- **Matches**: `Match` and `MatchPlay` tables for performance tracking
- **IDs**: All Hattrick entities use external `ht_id` fields

## Technology Stack
- **Backend**: Flask 2.x (Blueprints), PostgreSQL (SQLAlchemy), pytest (transaction isolation), Docker/uWSGI
- **Frontend**: Jinja2/Bootstrap3 (legacy), React/Vite/TypeScript/TailwindCSS (modern), Chart.js (visualization)
- **DevOps**: UV (Python), Make (workflows), GitHub Actions (CI/CD), Git (semantic versioning)6-01-21 (streamlined from 260+ to 150 lines
