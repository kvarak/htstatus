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

#### Flask Application Core
- **Main File**: `/app/routes.py` (1976 lines - primary application logic)
- **Database**: `/models.py` - SQLAlchemy models
- **Configuration**: `/config.py` - Environment-based configuration with Config/TestConfig/ProductionConfig classes
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
...existing code...
# HTStatus Architecture

*This architecture documentation reflects the current HTStatus project structure and design decisions.*

## System Overview

HTStatus is designed as a web-based platform for managing and visualizing football team statistics and player data. The architecture emphasizes maintainability, modularity, and clear separation of concerns.

## Architecture Principles

- **Modular Design**: Separation of core logic, routes, templates, and static assets
- **On-Demand Data Processing**: Data is processed and visualized as needed for user interactions
- **Configuration-Driven**: Use of configuration files and environment variables for flexible deployment
- **Security**: Sensitive data managed via environment variables or secure config files

## Technical Stack
- **Backend**: Python (Flask or similar framework)
- **Frontend**: HTML, CSS, JavaScript (with Chart.js, Plotly, etc.)
- **Data Storage**: File-based or database (as implemented)
- **Testing**: Automated tests (if present)

## File Structure (Updated January 2026)
- `app/` - Flask application code (routes, logic, templates, static assets)
- `src/` - React frontend components and pages
- `scripts/` - Utility scripts (migrations, changelog, database tools)
- `environments/` - Environment configuration templates (.env examples)
- `configs/` - Tool configurations and Docker compose overrides
- `models.py` - Database models
- `tests/` - Test suites and fixtures
- `pyproject.toml` - Python dependencies (UV-managed)
- `docker-compose.yml` - Development services
- `Makefile` - Development automation
- `.project/` - Development documentation and planning

## Security & Maintenance
- Use `.env` or similar for secrets (not committed)
- Document all architectural changes in this file

---

*Update this file with any major architectural changes or new integrations.*

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