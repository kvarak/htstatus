# HattrickPlanner

> **Simple Hattrick Team Management for Game Enthusiasts**
>
> A hobby project built by Hattrick fans for analyzing player development, match statistics, and team management.
> Built for managers who love diving deep into virtual football team data and statistics.

## Quick Start

**Requirements**: Docker, UV package manager, Hattrick CHPP credentials

```bash
# Install UV
brew install uv  # macOS
# or pip install uv

# Setup project
git clone <repo-url> && cd htstatus-2.0
cp .env.example .env            # then add your CHPP credentials
cp config.py.example config.py

# Start development
make install  # Install dependencies
make dev      # Start PostgreSQL and the Flask development server
```

## Make Commands

```bash
make help          # The main commands
make dev           # Start PostgreSQL and the development server
make test-single FILE=tests/test_x.py   # One test file
make test-all      # Format, then all quality gates (tests, lint, templates, bandit, CHPP policy)
make docker-up     # Run the production image locally
```

## Configuration

**Environment Variables** (`.env`):
```bash
CONSUMER_KEY=your-chpp-key                # Get at https://chpp.hattrick.org/
CONSUMER_SECRETS=your-chpp-secret
CALLBACK_URL=http://localhost:5000/login
DATABASE_URL=postgresql://user:pass@host:port/db  # Auto-configured for dev
```

`config.py` (copied from `config.py.example`) reads everything from these variables.

## Architecture

- **Backend**: Flask + SQLAlchemy + PostgreSQL
- **Frontend**: Server-rendered Jinja2 templates + Bootstrap 4 + Chart.js
- **Authentication**: Hattrick OAuth via CHPP API

## Development

**Key Features**:
- Player statistics and development tracking
- Team management with custom grouping
- Match result analysis
- Training progress monitoring
- Interactive tutorials and onboarding

**Database**:
```bash
make db-migrate MESSAGE="..."     # Create a migration
make db-copy-production          # Local dev database := copy of production (test migrations)
make db-upgrade                  # Apply migrations to the dev database
```
Production backs up before every deploy and nightly (see [DEPLOYMENT.md](DEPLOYMENT.md)).

## Documentation

- **[.project/architecture.md](.project/architecture.md)** - Code layout, data model, conventions, database rules
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Hosting (Docker), releasing, backups
- **[docs/CHPP-ENFORCEMENT.md](docs/CHPP-ENFORCEMENT.md)** - When the app may call the Hattrick API
- **[scripts/database/README.md](scripts/database/README.md)** - Migration and database helper scripts
- **[RELEASES.md](RELEASES.md)** - What's new for users

---

**Project Philosophy**: Simple, reliable hobby project focused on database integrity and Hattrick game enhancement. Built for spare-time maintenance.
