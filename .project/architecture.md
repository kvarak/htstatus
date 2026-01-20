# HTStatus Architecture

## Quick Navigation
🔗 **Project Context**: [Plan](plan.md) • [Progress](progress.md) • [Goals](goals.md) • [Backlog](backlog.md)
🛠️ **Technical Details**: [Implementation Guide](../TECHNICAL.md) • [Setup Instructions](../README.md)

*This file preserves all 2.0 architecture documentation, adapted to the new format. Update as the project evolves.*

## System Overview

HT Status is a Hattrick football team management application built with a dual frontend architecture, integrating with Hattrick's official CHPP API to provide comprehensive team and player analysis tools.

## High-Level Architecture

```
┌──────────────┐    ┌───────────────┐    ┌──────────────┐
│   React SPA  │    │  Flask Backend│    │   Hattrick   │
│ (Modern UI)  │◄──►│(Legacy + API) │◄──►│   CHPP API   │
│  Port 8080   │    │  Port 5000    │    │              │
└──────────────┘    └───────────────┘    └──────────────┘
				│
				▼
		       ┌──────────────────┐
		       │   PostgreSQL     │
		       │   Database       │
		       └──────────────────┘
```

## Component Breakdown

### 1. Frontend Layer (Dual Architecture)

#### Legacy Flask Frontend
- **Location**: `/app/templates/`
- **Technology**: Jinja2 templates + Flask-Bootstrap 3.x
- **Purpose**: Server-rendered HTML pages for existing functionality
- **Key Templates**: `player.html`, `matches.html`, `team.html`, `main.html`

#### Modern React Frontend
- **Location**: `/src/`
- **Technology**: React + TypeScript + Vite + TailwindCSS + Radix UI
- **Purpose**: Modern SPA experience (future direction)
- **Key Components**: Dashboard, Players, Matches, Training, Analytics

### 2. Backend Layer

### 2. Backend Layer

#### Flask Application Core
- **Main File**: `/app/routes.py` (1976 lines - primary application logic)
- **Database**: `/models.py` - SQLAlchemy models
- **Configuration**: `/config.py` - Environment-based configuration with Config/TestConfig/ProductionConfig classes
- **Route Architecture**: Manual route registration system in `/app/routes.py` with systematic route ownership strategy established (BUG-001 resolution January 2026)

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
- **Framework**: pytest with 218 total tests, all passing (100% success rate)
- **Coverage**: 96% overall project coverage via `make test-coverage`
- **Integration**: Docker-based services for realistic testing
- **Mock Systems**: CHPP API mocking in `/tests/mock_chpp.py`
- **Current Status**: Testing infrastructure excellence achieved with comprehensive coverage
- **Initialization**: `/app/__init__.py` - Flask app setup

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
Database queries → Skill calculations → Template/React rendering → User interface
```

## File Structure

### Root Directory
```
htstatus-2.0/
├── .project/           # Project management (backlog, plan, goals, architecture, progress)
├── app/               # Flask backend application
│   ├── __init__.py
│   ├── factory.py     # Application factory pattern
│   ├── routes.py      # Legacy routes (1,993 lines) - contains OAuth logic
│   ├── routes_bp.py   # Blueprint routes (stub migration, incomplete)
│   ├── static/        # Static assets (CSS, JS, images)
│   └── templates/     # Jinja2 HTML templates
├── src/               # React frontend application
│   ├── components/    # React components
│   ├── pages/         # Page-level components
│   ├── types/         # TypeScript type definitions
│   └── lib/          # Utility libraries
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
- **Dual Frontend**: Legacy Flask templates + Modern React SPA coexist
- **Routing Resolution**: Manual route registration implemented in factory.py (INFRA-011 completed)
  - Factory imports both Blueprint and legacy routes
  - Manual add_url_rule() registration for 12 legacy route functions
  - Commented @app.route decorators to prevent import failures
  - All 21 routes now properly accessible and functional
  - Requires completion or hybrid approach
- **Testing Foundation**: 218 passing tests enable confident refactoring
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
