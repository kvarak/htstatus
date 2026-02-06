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
cp environments/.env.development.example .env
# Edit .env with your CHPP credentials

# Start development
make setup  # Install dependencies + start services
make dev    # Run Flask development server
```

## Make Commands

```bash
make help          # Show all commands
make dev           # Start development server
make test-all      # Run comprehensive tests
make db-migrate    # Create database migration
make db-upgrade    # Apply migrations
make clean         # Clean temporary files
```

## Configuration

**Environment Variables** (`.env`):
```bash
CONSUMER_KEY=your-chpp-key                # Get at https://chpp.hattrick.org/
CONSUMER_SECRETS=your-chpp-secret
CALLBACK_URL=http://localhost:5000/auth
DATABASE_URL=postgresql://user:pass@host:port/db  # Auto-configured for dev
```

**Quick Config**:
```bash
cp config.py.template config.py  # Full config with documentation
# or use environment variables only
```

## Architecture

- **Backend**: Flask 2.x + SQLAlchemy + PostgreSQL
- **Frontend**: Server-rendered Jinja2 templates + Chart.js
- **Authentication**: Hattrick OAuth via CHPP API

## Development

**Key Features**:
- Player statistics and development tracking
- Team management with custom grouping
- Match result analysis
- Training progress monitoring
- Interactive tutorials and onboarding

**Database Protection** (INFRA-033):
```bash
make db-backup                    # Create full database backup
make db-restore BACKUP_FILE=...   # Restore from backup
make db-backup-auto              # Automated backup to kloker.local
```

## Documentation

- **[TECHNICAL.md](TECHNICAL.md)** - Architecture and implementation details
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment procedures
- **[scripts/database/backups/README.md](scripts/database/backups/README.md)** - Database backup and restore procedures
- **[CHANGELOG.md](CHANGELOG.md)** - Technical changes and commits
- **[RELEASES.md](RELEASES.md)** - User-focused feature releases

---

**Project Philosophy**: Simple, reliable hobby project focused on database integrity and Hattrick game enhancement. Built for spare-time maintenance with comprehensive CHPP API integration.
