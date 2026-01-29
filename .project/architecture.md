# HattrickPlanner Architecture

> **Purpose**: System structure, components, data flow, and technical architecture of HattrickPlanner
> **Audience**: Developers understanding or modifying the system structure
> **Update Frequency**: When architecture changes, new components added, or data flow modified
> **Standards**: Follow [htplanner-ai-agent.md](../.github/agents/htplanner-ai-agent.md) for editing guidelines

## Quick Navigation
🔗 **Project Context**: [Goals](goals.md) • [Backlog](backlog.md)
🛠️ **Setup Instructions**: [README.md](../README.md) for user setup • [DEPLOYMENT.md](../DEPLOYMENT.md) for production

*This file preserves all 2.0 architecture documentation, adapted to the new format. Update as the project evolves.*

## System Overview

HT Status is a **hobby project** for Hattrick team management built with Flask and server-side templates, integrating with Hattrick's official CHPP API to provide comprehensive team and player analysis tools.

**Target Audience**: Hattrick game enthusiasts and data geeks who love diving deep into player statistics and team optimization.

**Project Philosophy**:
- **Simplicity Over Enterprise Features**: Built for spare-time maintenance, not enterprise scalability
- **Database Protection Priority**: Production data integrity is the highest priority
- **Hattrick-Centric Design**: Features focus on enhancing actual Hattrick gameplay experience

## High-Level Architecture

```
┌──────────────┐    ┌───────────────┐    ┌──────────────┐
│  Flask Web   │    │  Flask Backend│    │   Hattrick   │
│ (Jinja2 UI)  │◄──►│  (Routes/API) │◄──►│   CHPP API   │
│  Port 5000   │    │  Port 5000    │    │              │
└──────────────┘    └───────────────┘    └──────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   PostgreSQL     │
                    │   Database       │
		       └──────────────────┘
```

## Component Breakdown

### 1. Frontend Layer (Flask-Only Architecture)

#### Flask Frontend
- **Location**: `/app/templates/`
- **Technology**: Jinja2 templates + Flask-Bootstrap 3.x + CSS
- **Purpose**: Server-rendered HTML pages for all application functionality
- **Key Templates**: `player.html`, `matches.html`, `team.html`, `main.html`
- **Features**: Responsive design, WCAG 2.1 accessibility, football-themed UI

### 2. Backend Layer

### 2. Backend Layer

#### Flask Application Core
- **Application Factory**: `/app/factory.py` - Creates and configures Flask application with blueprint registration
- **Blueprint Organization**: `/app/blueprints/` - Modular route organization (**100% COMPLETE** ✅ REFACTOR-007)
  - `auth.py` - Authentication and OAuth handling
  - `main.py` - Home page and administrative functions
  - `player.py` - Player management and skill tracking
  - `team.py` - Team information and data updates
  - `matches.py` - Match history and analysis
  - `training.py` - Player training progression
- **Authentication Utilities**: `/app/auth_utils.py` - Unified authentication patterns with @require_authentication decorator (**NEW** ✅ REFACTOR-008)
- **Error Handling**: `/app/error_handlers.py` - Standardized error handling with HattrickPlannerError exception hierarchy (**NEW** ✅ REFACTOR-008)
- **Test Utilities**: `/app/test_factories.py` - Simplified fixture creation for testing infrastructure (**NEW** ✅ REFACTOR-008)
- **Constants Module**: `/app/constants.py` - Hattrick data definitions (match types, roles, behaviors, column specs)
- **Shared Utilities**: `/app/utils.py` - Common functions shared across blueprints (create_page, dprint, team statistics)
- **Legacy Compatibility**: `/app/routes_bp.py` - Maintained for backward compatibility during migration
- **Database**: `/models.py` - SQLAlchemy models
- **Configuration**: `/config.py` - Environment-based configuration with Config/TestConfig/ProductionConfig classes
- **Route Architecture**: Pure blueprint-based architecture - legacy routes.py monolith eliminated (2,335 lines removed)

#### Authentication & API Integration
- **Hattrick OAuth**: CHPP (Community Hattrick Public Platform) integration using `pychpp` library
- **Session Management**: Flask sessions store OAuth tokens and team data
- **Error Handling**: Enhanced with comprehensive try/catch blocks and user-friendly error messages (FEAT-020)

#### Database Layer
- **PostgreSQL**: Production database with SQLAlchemy ORM
- **Migrations**: Alembic-based with 30 migration files in `/migrations/versions/`
- **Models**: Complex schema supporting multi-team management, player tracking, match analysis
- **Current Status**: Database schema stable and fully functional with comprehensive testing

#### Testing Infrastructure
- **Framework**: pytest with 218 total tests, 198 passing (90.8% success rate)
- **Coverage**: 41% overall project coverage (improved from 25%, target 80%)
- **Integration**: Docker-based services for realistic testing
- **Mock Systems**: CHPP API mocking in `/tests/mock_chpp.py`
- **Current Status**: Post-refactoring recovery in progress - TEST-006 import fixes needed, then TEST-004/TEST-005 for coverage improvement
- **Fast Test Suite**: 32/32 fast configuration tests passing (100%)

#### Key Backend Components
- **Authentication**: OAuth integration with Hattrick via pyCHPP
- **Data Sync**: Live player/match data fetching from CHPP API
- **Session Management**: Multi-team support via Flask sessions
- **Skill Analysis**: Complex tactical contribution calculations

### 3. Database Layer

#### PostgreSQL Schema (via SQLAlchemy)
```
Users ──┐
	├── Players (historical skill tracking)
	│   └── data_date (time-series player data)
	├── Match (game records)
	│   └── MatchPlay (player performance per match)
	└── PlayerGroup/PlayerSetting (custom player organization)
```

#### Key Tables
- **Players**: Historical skill progression with `data_date` timestamps
- **Match**: Game records with Hattrick match types and results
- **MatchPlay**: Individual player performance in specific matches
- **User**: Authentication and OAuth token storage
- **PlayerGroup/PlayerSetting**: Custom player categorization

### 4. External Integration

#### Hattrick CHPP API
- **Library**: `pychpp` (Python wrapper)
- **Authentication**: OAuth 1.0 flow with request/access tokens
- **Data Sources**: Players, matches, team info, match lineups
- **Rate Limits**: Managed by pyCHPP library

## Data Flow

### 1. Authentication Flow
```
User Login → Flask Session → Hattrick OAuth → CHPP Tokens → Session Storage
```

### 2. Data Update Flow
```
/update route → CHPP API calls → Player/Match data → Database storage → UI refresh
```

### 3. Analysis Flow
```
Database queries → Skill calculations → Template rendering → User interface
```

## Database Protection Standards (CRITICAL)

As a hobby project with valuable user data, **database integrity is the highest priority**:

### Migration Safety
- **Mandatory Migrations**: All schema changes use tested migration scripts via `apply_migrations.py`
- **Backwards Compatibility**: Changes must not break existing data
- **Production Testing**: Migrations tested on production-like data copies
- **Rollback Plans**: Document rollback procedures for each migration

### Data Integrity Protection
- **SQLAlchemy Best Practices**: Use proper model relationships and constraints
- **Transaction Safety**: Database operations wrapped in proper transactions
- **Validation**: Input validation before database writes
- **Backup Validation**: Regular backup testing and restore procedures

### Development Standards
- **Database Changes = P0 Priority**: Any database corruption is highest severity
- **Review Requirements**: Database modifications require extra validation
- **Testing**: Database operations must have comprehensive test coverage
- **Documentation**: Changes to data models require architecture updates

## File Structure

### Root Directory
```
htstatus-2.0/
├── .project/           # Project management (backlog, plan, goals, architecture, progress)
├── app/               # Flask backend application
│   ├── __init__.py
│   ├── factory.py     # Application factory pattern with blueprint registration
│   ├── constants.py   # Hattrick data definitions (166 lines)
│   ├── utils.py       # Shared utility functions
│   ├── routes_bp.py   # Legacy compatibility shim (minimal)
│   ├── blueprints/    # Feature-based route modules (auth, main, player, team, matches, training)
│   ├── static/        # Static assets (CSS, JS, images)
│   └── templates/     # Jinja2 HTML templates
├── migrations/        # Database migrations (30 Alembic versions)
├── tests/            # Test suite (218 tests, 100% passing)
├── environments/      # Environment configuration templates
├── configs/          # Tool and Docker configurations
├── scripts/          # Utility scripts
├── docker/           # Docker-related files
├── models.py         # SQLAlchemy database models (406 lines)
├── config.py         # Application configuration (58 lines)
├── run.py            # Development server entry point
├── Makefile          # Development commands
└── README.md         # User documentation
```

### Key Architectural Notes
- **Flask-Only Frontend**: Server-rendered Jinja2 templates with Flask-Bootstrap 3.x and custom CSS
- **Blueprint Architecture**: Modern Flask blueprint pattern with 6 feature-based blueprints (REFACTOR-007 completed January 2026)
  - Factory pattern in `app/factory.py` handles initialization and registration
  - Each blueprint has `setup_*_blueprint()` function for dependency injection
  - Constants extracted to `app/constants.py` (166 lines)
  - Shared utilities in `app/utils.py` for cross-blueprint functions
  - Clean separation of concerns by feature domain
- **Library Versions**: pychpp 0.3.12, Flask 2.3.3, werkzeug 2.3.8 (stable after BUG-001 resolution, downgrades may be re-evaluated)
- **Testing Foundation**: 215/246 tests passing (87%) enable confident refactoring
- **Multi-environment**: Development, staging, test, production configs ready

## Related Documentation

📋 **Project Management**:
- [Development Plan](plan.md) - Requirements, standards, and development guidelines
- [Current Progress](progress.md) - Implementation status and recent accomplishments
- [Strategic Goals](goals.md) - Vision and objectives driving architectural decisions

🛠️ **Implementation Details**:
- [Technical Documentation](../TECHNICAL.md) - Implementation specifics and development standards
- [Setup Guide](../README.md) - Local development setup and usage instructions
- [Change History](../CHANGELOG.md) - Version history and architectural evolution

📋 **Development Tasks**: [Project Backlog](backlog.md) - Architecture-related tasks and technical debt items

## Implementation Standards

### Hattrick Domain Knowledge

**Critical Ownership Hierarchy**:
- **User ID** (e.g., 182085 "kvarak") owns teams
- **Team ID** (e.g., 9838 "Dalby Stenbrotters") owns players
- `Players.owner` field = Team ID (correct in historical data)
- `session['current_user_id']` = User ID
- `session['all_teams']` = list of Team IDs owned by user

**Important**: Auth fallback code must not use User ID as Team ID when `_teams_ht_id` fails, as URL patterns like `/player?id=USER_ID` will fail to find players owned by TEAM_ID.

### Development Environment

**Python Execution**: Always use `uv run python` (never direct python calls)
**Commands**: Use `make help` for available workflow commands
**Quality Gates**: Run `make test-all` before marking tasks complete

### CHPP Integration

**Feature Flag**: `USE_CUSTOM_CHPP` environment variable toggles between custom CHPP and pychpp client (default: false)
- `USE_CUSTOM_CHPP=false`: Uses pychpp 0.5.10 (legacy fallback, backward compatible)
- `USE_CUSTOM_CHPP=true`: Uses custom CHPP client (app/chpp/) - **PRODUCTION READY**

**Custom CHPP Client**: ✅ ALL ENDPOINTS IMPLEMENTED
- `user()` - Get current user and team IDs
- `team(ht_id)` - Get team details and players
- `player(id_)` - Get individual player details
- `matches_archive(id_, is_youth)` - Get team match history
- YouthTeamId bug fixed (handles as optional field)
- Zero breaking changes from pychpp interface

### Database Migration Standards

**Backward Compatibility**: All schema changes must work with multiple application versions simultaneously

**Safe Patterns**:
- ✅ Adding nullable columns (applications ignore new columns)
- ✅ Adding indices (improves performance, backward compatible)
- ✅ Adding constraints with default values
- ❌ Removing columns in use by active versions
- ❌ Making columns non-nullable without defaults
- ❌ Renaming columns without deprecation period

**Migration Commands**:
```bash
uv run python scripts/database/apply_migrations.py  # Safe migrations
uv run alembic revision --autogenerate -m "description"  # Generate
uv run alembic upgrade head  # Apply
```

### Security Standards

- Never commit secrets (API keys, tokens, passwords) - use environment variables
- Subprocess usage limited to static dev tooling only (git version detection)
- Document security rationale for Bandit B404/B607/B603 skips
