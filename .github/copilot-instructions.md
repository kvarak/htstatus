# HT Status - AI Coding Agent Instructions

## Project Overview
**HT Status** is a Hattrick team management application with dual architecture: a legacy Flask backend serving traditional HTML templates and a modern React frontend. It integrates with Hattrick's CHPP (Community Hattrick Public Platform) API for football team data management.

## Architecture Overview

### Dual Frontend Pattern
- **Legacy Flask App**: Traditional server-rendered templates in `/app/templates/` with Flask-Bootstrap
- **Modern React App**: SPA in `/src/` using Vite, TypeScript, Radix UI components, TailwindCSS
- Both frontends can coexist; the React frontend is the future direction

### Key Integration Layer
- **CHPP API Integration**: Uses `pychpp` library for OAuth authentication and data fetching from Hattrick
- **Session Management**: Flask sessions store OAuth tokens (`access_key`, `access_secret`) and team data
- **PostgreSQL Database**: SQLAlchemy models in `models.py` for player tracking, match history, team data

## Essential Patterns

### Hattrick Domain Knowledge
- **Player Skills**: 7 core skills (keeper, defender, playmaker, winger, passing, scorer, set_pieces) with numeric levels
- **Match Roles**: 15+ field positions (GK=100, RB=101, etc.) defined in `HTmatchrole` constants
- **Match Types**: League matches, cups, friendlies with specific IDs in `HTmatchtype` constants
- **Skill Development**: Track player skill progression over time with `player_diff()` functions

### CHPP Authentication Flow
```python
# Pattern used throughout app/routes.py
chpp = CHPP(consumer_key, consumer_secret, session['access_key'], session['access_secret'])
current_user = chpp.user()
team = chpp.team(ht_id=teamid)
players = team.players  # Live data from Hattrick
```

### Database Architecture Specifics
- **Multi-team Support**: Users can own multiple teams via `session['all_teams']`
- **Historical Player Data**: `Players` table tracks skill changes over time by `data_date`
- **Player Grouping**: Custom groups via `PlayerGroup` and `PlayerSetting` junction table
- **Match Analysis**: `Match` and `MatchPlay` tables for game-by-game player performance

### Critical Development Workflows

#### Local Development
```bash
# Start Flask development server
./run.sh  # Sets FLASK_ENV=development, runs on port 5000

# Database migrations
python manage.py db migrate  # Generate migration
python manage.py db upgrade  # Apply migration

# React development (if working on modern frontend)
npm run dev  # Vite dev server on port 8080
```

#### Configuration Requirements
- **config.py**: Must contain Hattrick CHPP credentials (CONSUMER_KEY, CONSUMER_SECRETS, CALLBACK_URL)
- **PostgreSQL**: Required database with connection string in SQLALCHEMY_DATABASE_URI
- **Debug Levels**: Use DEBUG_LEVEL config (0-3) with `dprint()` function throughout codebase

### Project-Specific Conventions

#### Debugging System
```python
# Use throughout codebase instead of print()
dprint(1, "Info level message")
dprint(2, "Debug details")
dprint(3, "Verbose tracing")
```

#### Template Context Pattern
```python
# Standard pattern in route functions
return create_page(
    template='player.html',
    title='Player Details',
    # additional context...
)
```

#### Player Skill Contribution Calculations
- Complex position-specific algorithms in `calculateContribution()` function
- Accounts for experience (XP), loyalty, form multipliers
- Critical for tactical analysis features

### File Organization
- `/app/routes.py`: Main application logic (1976 lines) - the core of Flask backend
- `/models.py`: SQLAlchemy models defining database schema
- `/src/types/index.ts`: TypeScript interfaces matching database models
- `/migrations/versions/`: Database migration files for schema changes
- `/app/templates/`: Jinja2 templates for legacy frontend
- `/src/components/`: React components for modern frontend

### Integration Points
- **Hattrick OAuth**: Users authenticate via Hattrick's OAuth system, tokens stored in session
- **Real-time Data**: Player data fetched live from CHPP API during `/update` route
- **Cross-Component Communication**: Session state shared between Flask routes
- **Database Consistency**: All Hattrick IDs (players, matches, teams) use external `ht_id` fields

### Development Notes
- Version tracking via git tags: `git describe --tags` in routes.py
- Bootstrap 3.x styling in Flask templates vs TailwindCSS in React
- Chart.js used for player skill progression visualization
- Multiple team support requires careful session state management