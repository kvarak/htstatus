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
   cp environments/.env.development.example .env
   # Edit .env with your Hattrick CHPP credentials

   # Copy configuration template and customize if needed
   cp environments/config.py.example config.py
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
- `make test-fast` - Quick validation during development
- `make test` - Comprehensive testing before commits (**required** by project standards)

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
- `make test-fast` - ⚡ Quick core tests for development (32 tests, ~1 second)
- `make test` - 🧪 Comprehensive test suite (**required** by project standards)
- `make test-config` - 🔧 Configuration tests specifically (helps debug config issues)
- `make test-all` - ✅ Full quality gates (lint + security + config + tests)
- `make test-coverage` - 📊 Detailed HTML coverage reporting
- `make test-integration` - 🔗 Integration tests with Docker services
- `make test-watch` - 👀 Auto-rerun tests on file changes

**Database:**
- `make db-migrate` - Create new database migration
- `make db-upgrade` - Apply database migrations

**Utilities:**
- `make clean` - Remove temporary files and caches
- `make reset` - Clean and rebuild environment
- `make changelog` - Generate changelog

For detailed change history, see [CHANGELOG.md](CHANGELOG.md).

## Documentation

- **[README.md](README.md)** - This file: Project overview and local development setup
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide and operations procedures
- **[TECHNICAL.md](TECHNICAL.md)** - Technical architecture and implementation details
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and release notes

### Legacy Commands (Deprecated but Functional)

The following scripts are still available but deprecated in favor of Make commands:
- `./run.sh` → Use `make dev`
- `scripts/changelog.sh` → Use `make changelog`

**Status**: All scripts in `scripts/` directory are maintained but Makefile commands are preferred for consistency.

### Deployment Scripts

HTStatus includes automated deployment scripts for production deployments:

**`push.sh`** - Primary deployment automation script
- **Usage**: `./push.sh [major]`
- **Purpose**: Generates deployment commands and executes remote deployment using environment variables
- **Configuration**: Uses deployment variables from `.env` file (DEPLOY_SERVER, DEPLOY_REPO_PATH, etc.)
- **Process**: Loads .env → Creates `command.sh` → transfers to server → executes → cleanup
- **Major Flag**: `./push.sh major` regenerates SECRET_KEY for major releases

**Environment Variables** (configured in `.env`):
- `DEPLOY_SERVER`: Target deployment server (default: glader.local)
- `DEPLOY_REPO_PATH`: Remote repository path (default: ~/repos/htstatus)
- `DEPLOY_PYTHON_ENV`: Remote Python environment activation script
- `DEPLOY_GIT_BRANCH`: Git branch to deploy (default: origin/master)

**`command.sh`** - Auto-generated deployment script
- **Status**: AUTO-GENERATED (do not edit manually)
- **Purpose**: Contains deployment commands executed on target server
- **Generated by**: `push.sh` creates this file dynamically using environment variables
- **Lifecycle**: Created → transferred → executed → removed automatically

**Production Deployment Process**:
1. Configure deployment variables in `.env` file
2. Run `./push.sh` to initiate deployment
3. Script loads environment variables and generates `command.sh` with deployment commands
4. Transfers and executes commands on configured deployment server
5. Performs git pull, dependency updates, and database migrations
6. Cleans up temporary files automatically

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

HTStatus supports flexible configuration through environment variables and config templates. The system provides automatic validation and environment-specific defaults for robust deployment across development, staging, and production environments.

### Quick Setup (Recommended)

For new developers, use the comprehensive config template with guided setup:

```bash
# Copy the config template with detailed documentation
cp config.py.template config.py

# Edit with your settings following the inline documentation
nano config.py  # or your preferred editor
```

The config template includes complete documentation for all settings, validation methods, and environment-specific examples.

### Environment-Based Configuration

HTStatus uses a priority-based configuration system:
1. **Environment Variables** (highest priority)
2. **config.py file** (medium priority)
3. **Default values** (lowest priority)

This allows flexible deployment where environment variables can override file-based configuration.

#### Development Setup

```bash
# Option 1: Use config template (recommended for beginners)
cp config.py.template config.py
# Edit config.py with your CHPP credentials

# Option 2: Use environment variables
cp environments/.env.development.example .env
# Edit .env with your CHPP credentials

# Start development server
make dev
```

#### Production Deployment

```bash
# Environment variables override config.py for production deployments
export FLASK_ENV=production
export SECRET_KEY=$(openssl rand -hex 32)
export CONSUMER_KEY="your-chpp-key"
export CONSUMER_SECRETS="your-chpp-secret"
export DATABASE_URL="postgresql://user:pass@host:port/db"

# Validate configuration before starting
uv run python -c "from config import get_config; get_config().validate()"
```

### Configuration Classes

HTStatus provides environment-specific configuration classes with automatic detection:

**DevelopmentConfig**
- Helpful debugging defaults
- Relaxed validation with warnings
- Automatic setup guidance
- Local database integration

**StagingConfig**
- Enhanced security requirements
- Comprehensive validation
- Performance optimizations
- SSL cookie enforcement

**ProductionConfig**
- Strict security validation
- Required secret strength checks
- HTTPS-only enforcement
- Comprehensive audit logging

**TestConfig**
- Isolated test databases
- Mocked external services
- Parallel execution support
- Coverage reporting integration

### Core Configuration Variables

**Application Settings:**
```bash
FLASK_ENV=development|staging|production  # Environment mode
SECRET_KEY=your-secret-key                 # Flask secret (auto-generated if missing)
DEBUG_LEVEL=0-3                           # Debug verbosity (0=none, 3=full)
```

**Hattrick CHPP API:**
```bash
CONSUMER_KEY=your-chpp-key                 # Get at https://chpp.hattrick.org/
CONSUMER_SECRETS=your-chpp-secret         # CHPP consumer secret
CALLBACK_URL=http://localhost:5000/auth    # OAuth callback URL
```

**Database Configuration:**
```bash
DATABASE_URL=postgresql://user:pass@host:port/db  # Complete connection string
# OR individual components (lower priority)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=htplanner
POSTGRES_USER=htstatus
POSTGRES_PASSWORD=secure_password
```

**Security Settings (Production):**
```bash
SESSION_COOKIE_SECURE=true               # HTTPS-only cookies
SESSION_COOKIE_HTTPONLY=true             # Prevent XSS access
SESSION_COOKIE_SAMESITE=Lax              # CSRF protection
PERMANENT_SESSION_LIFETIME=7200          # Session timeout (seconds)
```

### Configuration Validation

HTStatus includes comprehensive configuration validation:

**Development Mode:**
- Warns about missing CHPP credentials
- Provides setup guidance for first-time users
- Validates database connectivity
- Suggests security improvements

**Production Mode:**
- Enforces secure SECRET_KEY requirements
- Validates SSL/TLS configuration
- Requires strong password policies
- Performs security audit checks

**Validation Example:**
```bash
# Test your configuration
uv run python -c "
from config import get_config
config = get_config()
print(f'Environment: {config.FLASK_ENV}')
config.validate()
print('✅ Configuration valid!')
"
```

### Migration from Legacy config.py

If you have an existing config.py file, you can modernize it:

```bash
# Backup existing config
cp config.py config.py.backup

# Copy new template
cp config.py.template config.py

# Migrate your settings following the template structure
# Environment variables will override any file settings
```

The new configuration system maintains full backward compatibility while providing enhanced features.

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
uv run python manage.py db init
uv run python manage.py db migrate
uv run python manage.py db upgrade
```
*Upgrade*
```
uv run python manage.py db migrate
uv run python manage.py db upgrade
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
