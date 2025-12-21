# HT Status Architecture

## Overview

HT Status is a Hattrick football team management application built with a dual frontend architecture, integrating with Hattrick's official CHPP API to provide comprehensive team and player analysis tools.

## High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React SPA     │    │   Flask Backend  │    │   Hattrick      │
│  (Modern UI)    │◄──►│  (Legacy + API)  │◄──►│   CHPP API      │
│   Port 8080     │    │   Port 5000      │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
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
- **Configuration**: `/config.py` - CHPP credentials and app settings
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
        │
        ├── Players (historical skill tracking)
        │   └── data_date (time-series player data)
        │
        ├── Match (game records)
        │   └── MatchPlay (player performance per match)
        │
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

```
├── app/                    # Flask application
│   ├── routes.py          # Main application logic (1976 lines)
│   ├── templates/         # Jinja2 templates (legacy UI)
│   └── static/            # CSS, JS, assets
├── src/                   # React application
│   ├── components/        # React components
│   ├── pages/            # Route components
│   └── types/            # TypeScript interfaces
├── models.py             # SQLAlchemy database models
├── config.py             # Configuration (CHPP credentials)
├── migrations/           # Database migrations
├── run.py               # Flask entry point
├── manage.py            # Database management
└── package.json         # React dependencies
```

## Technology Stack

### Backend
- **Framework**: Flask 2.3.2
- **Dependencies**: UV for fast dependency management (replaces pip)
- **Database**: PostgreSQL with SQLAlchemy 2.0.32
- **API Integration**: pychpp 0.3.12
- **Migrations**: Flask-Migrate 4.0.7
- **Authentication**: Werkzeug security + OAuth
- **Development Environment**: Docker Compose for services

### Frontend (Legacy)
- **Templates**: Jinja2 + Flask-Bootstrap 3.3.7.1
- **Charts**: Chart.js for skill progression
- **Styling**: Bootstrap 3.x

### Frontend (Modern)
- **Framework**: React with TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **Components**: Radix UI
- **State**: React Query (TanStack Query)

## Key Design Patterns

### 1. Hattrick Domain Modeling
- **Skills**: 7 core skills tracked with numeric levels
- **Positions**: 15+ match roles with specific IDs (HTmatchrole constants)
- **Matches**: Different types (league, cup, friendly) with HTmatchtype constants
- **Contributions**: Position-specific skill calculation algorithms

### 2. Session-Based Multi-Team Support
```python
# Stored in Flask session
session['all_teams']      # List of team IDs user owns
session['all_team_names'] # Corresponding team names
session['current_user']   # Active user identifier
session['access_key']     # OAuth access token
session['access_secret']  # OAuth access secret
```

### 3. Historical Data Tracking
- Players table uses `data_date` for time-series skill progression
- `player_diff()` functions calculate skill changes over time periods
- Match performance tracking via MatchPlay junction table

### 4. Debug System
```python
# Custom debugging throughout codebase
dprint(level, message)  # Respects DEBUG_LEVEL config (0-3)
```

## Development Workflow

### Local Development with UV + Docker Compose
```bash
# Start all services (PostgreSQL, Redis, etc.)
docker-compose up -d

# Install/update Python dependencies with UV
uv sync
uv sync --extra dev  # Include development dependencies

# Run Flask backend (with services from Docker Compose)
source .venv/bin/activate  # or just use `uv run`
uv run python run.py
# or
./run.sh

# React frontend (in separate terminal)
npm run dev              # Starts Vite on port 8080

# Database management (using UV)
uv run python manage.py db migrate   # Create migration
uv run python manage.py db upgrade   # Apply migration

# Stop services
docker-compose down
```

### Configuration Requirements
- Docker and Docker Compose for services (PostgreSQL, Redis)
- UV for Python dependency management
- Valid Hattrick CHPP credentials in `config.py`
- Python 3.9+ (managed by UV)

## Security Considerations

- OAuth tokens stored in Flask sessions (server-side)
- CHPP credentials in config.py (not version controlled in production)
- Database connections via SQLAlchemy with parameterized queries
- Session-based authentication for multi-team access

## Performance Considerations

- Historical player data can grow large (time-series by data_date)
- CHPP API rate limits managed by pychpp library
- Complex skill contribution calculations in calculateContribution()
- Database indexing on ht_id fields for Hattrick entity lookups

## Future Architecture Direction

- Migrate from Flask templates to React SPA
- UV-based dependency management (✅ completed)
- Docker Compose for development environment (🔄 in progress)
- Enhanced real-time data synchronization
- Improved tactical analysis algorithms
- Production containerization with multi-stage Docker builds