# HT Status

## Local Development with UV + Docker + Makefile

This project uses [UV](https://docs.astral.sh/uv/) for fast Python dependency management, Docker Compose for services, and Make for standardized development commands.

### Quick Start

1. **Install Dependencies**:
   ```bash
   # Install UV (if not already installed)
   # macOS:
   brew install uv

   # Linux (Ubuntu/Debian):
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Linux (Arch):
   pacman -S uv

   # Or using pip (cross-platform):
   pip install uv

   # Install Docker and Docker Compose
   # macOS: Docker Desktop includes Docker Compose
   # Linux: Install docker and docker-compose packages
   ```

2. **Setup Project**:
   ```bash
   # Clone and enter project
   git clone <repo-url>
   cd htstatus-2.0

   # Copy environment template and configure
   cp .env.example .env
   # Edit .env with your Hattrick CHPP credentials

   # Copy configuration template and customize if needed
   cp config.py.example config.py
   # Edit config.py if you need custom configuration beyond environment variables

   # Setup complete development environment
   make setup
   ```

3. **Start Development**:
   ```bash
   # Start development server (includes services)
   make dev

   # Stop dev server and services
   make stop
   ```

4. **Access Application**:
   - **Flask App**: http://localhost:5000
   - **React Dev Server**: `npm run dev` (http://localhost:8080)
   - **pgAdmin** (optional): `docker-compose --profile admin up -d` (http://localhost:5050)

### Make Commands

Run `make help` to see all available commands:

**Development Workflow:**
- `make setup` - Initialize development environment (UV sync + Docker services)
- `make dev` - Start development server
- `make services` - Start only Docker Compose services
- `make stop` - Stop Flask dev server and Docker Compose services
- `make test` - Run test suite (**required** by project standards)

**Python Development:**
- `make install` - Install dependencies using UV
- `make update` - Update dependencies and sync environment
- `make shell` - Open Python shell in UV environment

**Code Quality:**
- `make lint` - Run ruff linting (with fixes)
- `make format` - Format code with black and ruff
- `make typecheck` - Run mypy type checking
- `make security` - Run security checks (bandit, safety)

**Testing:**
- `make test` - Run basic test suite
- `make test-coverage` - Run tests with coverage reporting
- `make test-integration` - Run integration tests with services

**Database:**
- `make db-migrate` - Create new database migration
- `make db-upgrade` - Apply database migrations

**Utilities:**
- `make clean` - Remove temporary files and caches
- `make reset` - Clean and rebuild environment
- `make changelog` - Generate changelog

For detailed change history, see [CHANGELOG.md](CHANGELOG.md).

### Legacy Commands (Deprecated but Functional)

The following shell scripts are still available but deprecated in favor of Make commands:
- `./run.sh` → Use `make dev`
- `./scripts/changelog.sh` → Use `make changelog`

### Development Commands

**Python Dependencies (UV):**
- `uv sync` - Install/update dependencies
- `uv sync --extra dev` - Include development dependencies
- `uv add <package>` - Add new dependency
- `uv remove <package>` - Remove dependency
- `uv run <command>` - Run command in project environment
- `uv lock` - Update lock file

**Services (Docker Compose):**
- `docker-compose up -d` - Start PostgreSQL & Redis in background
- `docker-compose down` - Stop and remove containers
- `docker-compose logs` - View service logs
- `docker-compose --profile admin up -d` - Include pgAdmin
- `docker-compose exec postgres psql -U htstatus -d htplanner` - Connect to database


## Configuration

HTStatus supports multiple environment configurations with comprehensive templates and validation. Choose the approach that works best for your deployment scenario.

### Quick Setup (Development)

For development, use the development-specific environment template:

```bash
# Copy development template
cp environments/.env.development.example .env

# Edit with your CHPP API credentials
nano .env  # or your preferred editor
```

### Environment-Specific Setup

HTStatus provides environment templates for different deployment scenarios:

#### Development Environment
```bash
# Use development template with detailed comments
cp environments/.env.development.example .env

# Start with development Docker configuration
docker-compose -f docker-compose.yml -f configs/docker-compose.development.yml up -d

# Run development server
make dev
```

#### Staging Environment
```bash
# Use staging template with security enhancements
cp environments/.env.staging.example .env

# Configure staging-specific values (see template comments)
nano .env

# Start with staging Docker configuration
docker-compose -f docker-compose.yml -f configs/docker-compose.staging.yml up -d
```

#### Production Environment
```bash
# Use production template (requires all security settings)
cp environments/.env.production.example .env

# IMPORTANT: Replace ALL placeholder values with secure production values
# See template file for detailed security requirements
nano .env

# Production should use managed services, not Docker Compose
# See configs/docker-compose.production.yml for reference only
```

### Configuration Validation

HTStatus automatically validates configuration based on the environment:

- **Development**: Warnings for missing CHPP credentials, allows development defaults
- **Staging**: Requires secure SECRET_KEY, validates critical settings  
- **Production**: Strict validation of all security settings, requires SSL, validates secret strength

### Environment Variables Reference

**Required for all environments:**
- `FLASK_ENV` - Environment type: `development`, `staging`, `production`
- `SECRET_KEY` - Flask secret key (must be secure for staging/production)
- `DATABASE_URL` - PostgreSQL connection string

**CHPP API Configuration:**
- `CONSUMER_KEY` - Your Hattrick CHPP consumer key ([Get here](https://chpp.hattrick.org/))
- `CONSUMER_SECRETS` - Your Hattrick CHPP consumer secret
- `CALLBACK_URL` - OAuth callback URL for your environment

**Database Configuration (managed by Docker Compose in development):**
- `POSTGRES_DB` - Database name
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_HOST` - Database host
- `POSTGRES_PORT` - Database port

**Redis Configuration:**
- `REDIS_URL` - Redis connection URL
- `REDIS_HOST` - Redis host
- `REDIS_PORT` - Redis port  
- `REDIS_PASSWORD` - Redis password

**Security Settings (staging/production):**
- `SESSION_COOKIE_SECURE` - Enable secure cookies (HTTPS required)
- `SESSION_COOKIE_HTTPONLY` - Prevent JavaScript access to session cookies
- `SESSION_COOKIE_SAMESITE` - CSRF protection (`Lax` or `Strict`)
- `PERMANENT_SESSION_LIFETIME` - Session timeout in seconds

### Legacy config.py (Still Supported)

You can still use a `config.py` file, but environment variables take priority. The configuration system now provides enhanced environment support:

```python
# config.py structure
from config import get_config, Config, DevelopmentConfig, StagingConfig, ProductionConfig

# Auto-detect configuration based on FLASK_ENV
ConfigClass = get_config()

# Or explicitly specify
ConfigClass = get_config('production')
```

**Available Configuration Classes:**
- `DevelopmentConfig`: Development with helpful defaults and warnings
- `StagingConfig`: Staging with enhanced security and validation
- `TestConfig`: Testing with isolated databases and mocked services
- `ProductionConfig`: Production with strict validation and security requirements

```python
import os

class Config(object):
  APP_NAME                 = 'your-app-name'
  SECRET_KEY               = 'you-will-never-guess'
  CONSUMER_KEY             = 'you-will-never-guess'
  CONSUMER_SECRETS         = 'you-will-never-guess'
  CALLBACK_URL             = 'url-to-your-callback'
  CHPP_URL                 = 'https://chpp.hattrick.org/chppxml.ashx'
  SQLALCHEMY_DATABASE_URI  = 'postgresql:///<dbname>'
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  DEBUG_LEVEL              = 3 # 0=none, 1=info, 2=debug, 3=full
```

## Database

### SQLAlchemy (with UV + Docker Compose)

*Start services first:*
```bash
docker-compose up -d
./docker/wait-for-postgres.sh
```

*Create/Upgrade:*
```bash
uv run python manage.py db migrate
uv run python manage.py db upgrade
```

*On problems:*
```bash
uv run python manage.py db stamp head
```

### SQLAlchemy (Legacy)

*Create*
```
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```
*Upgrade*
```
python manage.py db migrate
python manage.py db upgrade
```
```
*On problems*
```
python manage.py db stamp head
```

### Postgres

*Create*
```
CREATE DATABASE htplanner;
```

*Check*
```
$ psql
# \c htplanner
# \dt
# \d results
```

## Requirements

### Modern Setup (UV + Docker Compose)
- **Docker & Docker Compose** - For PostgreSQL and Redis services
- **UV package manager** - For Python dependency management
- **Python 3.9+** - Automatically managed by UV
- **Hattrick CHPP API credentials** - Required for data access

Dependencies are automatically handled by `uv sync`.
Services are automatically managed by `docker-compose up -d`.

### Legacy Setup (Deprecated)
- Postgres
- Python 3+
- Flask
- flask_script
- psycopg2-binary
- python-dateutil

```
pip3 install flask-script
pip3 install psycopg2-binary
pip3 install python-dateutil
```

### Manage requirements (Legacy)
```
pipreqs . --force
pip install -r requirements.txt
```

## Start

### With UV + Docker Compose (Recommended)
```bash
# Start services
docker-compose up -d

# Wait for database
./docker/wait-for-postgres.sh

# Ensure dependencies are installed
uv sync

# Run development server
uv run python run.py
# or
./run.sh

# Stop services when done
docker-compose down
```

### Legacy
```
nohup ./run.sh 5000 &
```
