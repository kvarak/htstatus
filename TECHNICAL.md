# HTStatus Technical Documentation

*This file provides technical implementation details for the HTStatus 2.0 project.*

## Architecture Overview

HTStatus 2.0 is a Hattrick team management application with a dual frontend architecture (legacy Flask and modern React) and a PostgreSQL backend. It integrates with the Hattrick CHPP API for live football data.

## Key Technologies
- **Backend**: Python (Flask), SQLAlchemy ORM
- **Frontend**: React (Vite, TypeScript, TailwindCSS, Radix UI), Jinja2 templates (legacy)
- **Database**: PostgreSQL
- **API Integration**: pychpp (OAuth, CHPP API)
- **Dev Tools**: Makefile, Docker Compose, UV (Python deps), pytest, ruff, mypy

## Implementation Details
- **Session Management**: Flask sessions store OAuth tokens and team data
- **Player/Match Data**: Synced from CHPP API, stored in Players, Match, MatchPlay tables
- **Testing**: pytest with fixtures, CHPP API mocking, test coverage tracked
- **CI/CD**: GitHub Actions for linting and basic CI
- **Security**: .env for secrets, never committed; database migrations tested on copies of production structure

## File Structure
- `/app/routes.py`: Main Flask app logic
- `/models.py`: SQLAlchemy models
- `/src/`: React frontend
- `/app/templates/`: Jinja2 templates
- `/docker/`, `docker-compose.yml`: Container orchestration
- `/Makefile`: Standardized dev commands
- `/tests/`: Test suite

## Development Standards
- See `.project/plan.md` for requirements and standards
- See `.project/architecture.md` for system design
- See `.project/prompts.json` for AI/DevAgent workflows

---

*Update this file as technical implementation evolves. Ensure all major changes are documented here and referenced in plan.md and architecture.md as needed.*