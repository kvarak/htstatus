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
- **Route Architecture**: Dual registration system with functional routes in routes.py and blueprint organization in routes_bp.py
- **Security**:
  - .env for secrets, never committed; database migrations tested on copies of production structure
  - Subprocess usage policy: Limited to development tooling only (git version detection)
  - Static commands with no user input vectors; documented with security rationale
  - Bandit configuration (.bandit) skips B404/B607/B603 for documented dev utilities

### Route Ownership Strategy

**Problem Resolved**: BUG-001 identified conflicts between blueprint stub routes and functional routes causing application pages to return empty templates instead of processed data.

**Route Registration System**:
- **Functional Routes** (routes.py): Contains actual business logic for data processing and rendering
- **Blueprint Routes** (routes_bp.py): Organizational structure for route grouping and future migration

**Ownership Rules**:
1. **Functional routes have precedence**: When both exist, functional route implementations should be preserved
2. **Remove conflicting stubs**: Blueprint routes that only return empty templates should be removed
3. **Blueprint routes should be minimal**: Only include routes that provide unique functionality or proper bluepr framework organization

**Resolved Route Conflicts**:
- ✅ `/login` - Functional route preserved (OAuth implementation)
- ✅ `/logout` - Blueprint route preserved (simple session clearing)
- ✅ `/update` - Removed blueprint stub, functional route restored
- ✅ `/player` - Removed blueprint stub, functional route restored
- ✅ `/team` - Removed blueprint stub, functional route restored
- ✅ `/matches` - Removed blueprint stub, functional route restored
- ✅ `/training` - Removed blueprint stub, functional route restored
- ✅ `/settings` - Removed blueprint stub, functional route restored
- ✅ `/debug` - Removed blueprint stub, functional route (admin) restored

**Future Blueprint Migration**: When migrating routes to blueprints, move the functional implementation rather than creating stubs that override working code.

## File Structure
- `/app/routes.py`: Main Flask app logic
- `/models.py`: SQLAlchemy models
- `/src/`: React frontend
- `/app/templates/`: Jinja2 templates
- `/scripts/`: Development utilities and debugging tools
- `/environments/`: Environment configuration templates
- `/configs/`: Docker Compose configurations and build tools
- `/docker/`, `docker-compose.yml`: Container orchestration
- `/Makefile`: Standardized dev commands
- `/tests/`: Test suite

## File Organization Standards

### Version Control Strategy

**Tracked Files** (in git):
- Source code: `*.py`, `*.ts`, `*.tsx`, `*.js`
- Configuration templates: `*.example`, `*.template`
- Documentation: `*.md`
- Project structure: `Makefile`, `pyproject.toml`, `package.json`
- Docker configurations: `docker-compose.yml`, `Dockerfile`

**Ignored Files** (not in git):
- Environment-specific: `.env`, `config.py`, credentials
- Auto-generated: `__pycache__/`, `*.pyc`, `migrations/`
- Development artifacts: `.coverage`, `htmlcov/`, `*.log`
- System files: `.DS_Store` (macOS), `*.swp` (vim)
- Dependencies: `.venv/`, `node_modules/`, `env/`
- Data directories: `data/` (test data), build outputs

**Rationale**: Keep repository clean and secure by excluding:
1. Credentials and secrets (security)
2. Environment-specific configuration (portability)
3. Generated files that can be recreated (efficiency)
4. Large dependency directories (performance)

### Cleanup Commands

```bash
# Remove temporary files and caches
make clean

# Complete environment reset
make reset

# Manual cleanup patterns
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete
find . -name ".DS_Store" -delete
```

See `.gitignore` for complete exclusion patterns.

## Development Scripts

HTStatus includes debugging utilities in the `scripts/` directory, created during troubleshooting and preserved for future development use.

### Script Execution Policy

**Environment Consistency**: All Python scripts in this project should be executed using UV:

```bash
# Correct - uses UV-managed environment
uv run python scripts/[script_name].py

# Incorrect - uses system Python (may have different dependencies)
python scripts/[script_name].py
python3 scripts/[script_name].py
```

**Why UV is Required**:
- Ensures consistent dependency versions across environments
- Prevents "works on my machine" issues
- Matches production environment configuration
- Automatically resolves project dependencies

**Makefile Integration**: All Makefile targets automatically use UV (via `$(PYTHON)` variable), so commands like `make db-upgrade` are already UV-aware.

### Database Utilities (`scripts/database/`)

**`apply_migrations.py`**: Safe database migration utility
- Creates Flask app with proper context handling
- Bypasses route loading for migration-only operations
- Use when standard `make db-upgrade` encounters issues

**`test_db_connection.py`**: PostgreSQL connection diagnostics
- Tests direct database connectivity bypassing SQLAlchemy
- Provides detailed error diagnostics for troubleshooting
- Helpful for diagnosing authentication, networking, or service issues

Usage:
```bash
# Test database connectivity
uv run python scripts/database/test_db_connection.py

# Apply migrations safely
uv run python scripts/database/apply_migrations.py
```

### Migration Utilities (`scripts/migration/`)

**`temp_migrate.py`**: Quick migration execution
- Simplified script for emergency migration scenarios
- Minimal setup with basic error handling
- Use `scripts/database/apply_migrations.py` for safer operations

Common Troubleshooting Scenarios:
- **macOS PostgreSQL conflicts**: Use connection tester to identify port conflicts
- **Authentication failures**: Migration utility creates proper Flask context
- **Service startup issues**: Scripts can run independently of main application

*These utilities were created during INFRA-011 (authentication system restoration) and are maintained as permanent development tools.*

## Development Standards
- See `.project/plan.md` for requirements and standards
- See `.project/architecture.md` for system design
- See `.project/prompts.json` for AI/DevAgent workflows

## Debugging Guide

### Quick Debugging Reference

**Environment Issues:**
- `make config-validate` - Check configuration validity
- `make setup` - Reinitialize development environment
- `make services` - Start Docker services only
- `uv sync --dev` - Resolve UV dependency issues

**Testing Issues:**
- `make test` - Run comprehensive test suite
- `make test-unit` - Fast unit tests only
- `pytest tests/ -v --tb=short` - Verbose test output with traceback

**Application Issues:**
- Check Docker logs: `docker-compose logs postgres redis`
- Validate environment: `uv run python -c "from config import get_config; get_config().validate_config()"`
- Database connection: `make db-upgrade` then test connectivity

### Environment Debugging

#### UV Package Management Issues

**Problem: UV command not found**
```bash
# Symptoms: "command not found: uv"
# Solution: Install UV
# macOS:
brew install uv

# Linux (Ubuntu/Debian):
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Arch Linux:
pacman -S uv

# Verify installation:
uv --version
```

**Problem: UV sync failures or dependency conflicts**
```bash
# Symptoms: "Failed to resolve dependencies" or version conflicts
# Solution: Clean and reinstall
rm -rf .venv/
uv sync --dev

# If conflicts persist, check for system Python issues:
uv python install 3.11  # Install specific Python version
uv sync --python 3.11   # Use specific version
```

**Problem: Virtual environment activation issues**
```bash
# Symptoms: Commands not found, wrong Python version
# Solution: Use UV run prefix or activate manually
uv run python --version  # Preferred approach
# OR
source .venv/bin/activate  # Manual activation
```

#### Docker Compose Service Issues

**Problem: Services won't start**
```bash
# Check service status:
docker-compose ps

# View service logs:
docker-compose logs postgres
docker-compose logs redis

# Common fixes:
docker-compose down && docker-compose up -d  # Restart services
docker system prune -f  # Clean up resources if low on space
```

**Problem: PostgreSQL connection refused**
```bash
# Symptoms: "connection refused" or "could not connect to server"
# Check PostgreSQL status:
docker-compose logs postgres

# Verify port availability:
netstat -tulpn | grep 5432  # Linux
lsof -ti:5432               # macOS

# Solution: Stop conflicting services or change port in docker-compose.yml
sudo systemctl stop postgresql  # If system PostgreSQL is running
```

**Problem: Port conflicts**
```bash
# Symptoms: "port already in use" during service startup
# Find process using port:
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :5000  # Flask

# Kill conflicting process:
kill -9 <PID>

# Or modify docker-compose.yml ports section
```

#### Configuration and Environment Variables

**Problem: Configuration validation failures**
```bash
# Check current configuration:
make config-validate

# Common issues and fixes:
# Missing .env file:
cp environments/.env.development.example .env
# Edit .env with your settings

# Invalid configuration values:
python -c "
import os
print('FLASK_ENV:', os.getenv('FLASK_ENV'))
print('DATABASE_URL:', os.getenv('DATABASE_URL'))
# Check for typos and missing values
"
```

**Problem: Database connection string issues**
```bash
# Symptoms: SQLAlchemy connection errors
# Verify DATABASE_URL format:
# postgresql://username:password@localhost:5432/database

# Test connection manually:
python -c "
import psycopg2
from config import get_config
cfg = get_config()
conn = psycopg2.connect(cfg.DATABASE_URL)
print('Database connection successful')
conn.close()
"
```

### Development Workflow Debugging

#### Testing Infrastructure Issues

**Problem: Test hanging or not completing**
```bash
# CASE STUDY: INFRA-005 Resolution
# Symptoms: Tests hang at ~70% completion, never finish
# Root Cause: Database transactions not properly cleaned up

# Solution implemented (reference for similar issues):
# 1. Added db.session.rollback() in test fixtures
# 2. Added db.session.close() in teardown
# 3. Ensured proper transaction isolation

# If experiencing similar hanging:
# Check for unclosed database sessions:
pytest tests/ -v -s --tb=long  # Verbose output to identify hang point

# Force kill hanging tests:
pkill -f pytest
```

**Problem: Specific test failures**
```bash
# Run single test for debugging:
pytest tests/test_specific.py::TestClass::test_method -v -s

# Debug with print statements:
pytest tests/ -v -s --capture=no

# Check test database state:
# Tests should use isolated transactions and fixtures
```

**Problem: Coverage calculation issues**
```bash
# Symptoms: Coverage hanging, incorrect percentages
# Solution: Use optimized coverage configuration
make test  # Uses optimized coverage settings

# Manual coverage debugging:
uv run pytest tests/ --cov=app --cov=models --cov-report=term-missing

# Check coverage configuration in pyproject.toml:
# Should exclude legacy routes and focus on blueprint architecture
```

#### Build System and Makefile Issues

**Problem: Make command failures**
```bash
# Check UV availability first:
make check-uv

# Common Makefile debugging:
make help  # See all available commands

# If specific command fails, run manually:
# Instead of "make test":
uv run pytest tests/ -v --tb=short --cov=app --cov=models

# Check for missing dependencies:
uv sync --dev
```

**Problem: Database migration issues**
```bash
# Check current migration status:
uv run python manage.py db current

# Create migration:
make db-migrate

# Apply migrations:
make db-upgrade

# If migrations fail:
# Check for model definition errors in models.py
# Verify database connectivity
# Review migration scripts in migrations/versions/
```

### Application Runtime Debugging

#### Flask Application Issues

**Problem: Flask app won't start**
```bash
# Check for syntax errors:
python -m py_compile app/__init__.py
python -m py_compile models.py
python -m py_compile config.py

# Verify imports:
python -c "from app.factory import create_app; print('App imports successfully')"

# Check for circular imports:
# Review import statements in app/__init__.py and models.py
```

**Problem: Template rendering errors**
```bash
# Symptoms: TemplateNotFound or template syntax errors
# Check template paths in app/templates/
# Verify Flask app configuration:
python -c "
from app.factory import create_app
app = create_app()
print('Template folder:', app.template_folder)
print('Static folder:', app.static_folder)
"
```

**Problem: Route not found (404 errors)**
```bash
# List all registered routes:
python -c "
from app.factory import create_app
app = create_app()
for rule in app.url_map.iter_rules():
    print(rule.rule, rule.methods)
"

# Check blueprint registration in app/factory.py
# Verify route definitions in app/routes_bp.py
```

#### Database and Model Issues

**Problem: SQLAlchemy model errors**
```bash
# Check model definitions:
python -c "from models import User, Players, Match; print('Models import successfully')"

# Test database schema:
python -c "
from app.factory import create_app
from app import db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database schema created successfully')
"

# Check for composite primary key issues (reference: INFRA-005 fix):
# Ensure autoincrement=True is not used with composite primary keys
# Models with multiple primary key columns should not have autoincrement
```

### Advanced Debugging Tools

#### Performance Debugging

**Problem: Slow database queries**
```bash
# Enable SQLAlchemy query logging:
# Add to config.py temporarily:
# SQLALCHEMY_ECHO = True

# Check for N+1 query problems:
# Review relationship loading in models.py
# Consider using joinedload() for related data

# Monitor database performance:
docker-compose exec postgres psql -U postgres -d htstatus -c "
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC LIMIT 10;
"
```

**Problem: Memory usage issues**
```bash
# Monitor application memory:
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"

# Check for memory leaks in long-running processes
# Review database connection pooling
# Ensure proper session cleanup
```

#### CHPP API Integration Debugging

**Problem: OAuth authentication failures**
```bash
# Check OAuth credentials in .env:
python -c "
import os
print('CONSUMER_KEY exists:', bool(os.getenv('CHPP_CONSUMER_KEY')))
print('CONSUMER_SECRET exists:', bool(os.getenv('CHPP_CONSUMER_SECRET')))
# Never print actual secrets!
"

# Test CHPP API connectivity:
python -c "
from app.factory import create_app
app = create_app()
# Test basic CHPP connection (implement as needed)
"
```

**Problem: API rate limiting**
```bash
# Implement exponential backoff in API calls
# Check CHPP API documentation for rate limits
# Monitor API response headers for rate limit information
# Consider implementing request caching
```

### Cross-Platform Debugging

#### Linux vs macOS Differences

**Docker Socket Issues (Linux):**
```bash
# If Docker commands require sudo:
sudo usermod -aG docker $USER
newgrp docker

# Test Docker access:
docker run hello-world
```

**Path and Permission Issues:**
```bash
# File permissions:
chmod +x scripts/*.sh  # Make scripts executable

# Path differences:
# Use absolute paths in scripts
# Check environment variable differences between platforms
```

#### Windows Considerations (if applicable)

```bash
# Use WSL2 for Windows development
# Ensure Docker Desktop is configured for WSL2
# Watch for line ending differences (CRLF vs LF)

# Configure Git for consistent line endings:
git config --global core.autocrlf false
```

### Production Environment Debugging

**Problem: Environment-specific failures**
```bash
# Check environment detection:
python -c "
import os
from config import get_config
print('FLASK_ENV:', os.getenv('FLASK_ENV'))
print('Config class:', get_config().__class__.__name__)
"

# Validate production configuration:
# Ensure all required environment variables are set
# Check for development-only code in production
# Verify database connection strings for production
```

**Problem: Deployment issues**
```bash
# Check service health:
curl -f http://localhost:5000/health || echo "Health check failed"

# Monitor application logs:
tail -f /var/log/htstatus/application.log

# Database migration in production:
# Always backup before migrations
# Test migrations on production copy first
# Use blue-green deployment strategy
```

### Troubleshooting Checklist

When encountering issues, follow this systematic approach:

1. **Environment Validation**
   - [ ] `make config-validate` passes
   - [ ] All services running: `docker-compose ps`
   - [ ] UV environment synced: `uv sync --dev`

2. **Basic Connectivity**
   - [ ] Database accessible: `make db-upgrade`
   - [ ] Python imports working: `python -c "from app.factory import create_app"`
   - [ ] Tests passing: `make test`

3. **Application Health**
   - [ ] Flask app starts: `make dev`
   - [ ] Routes accessible: Check key endpoints
   - [ ] No errors in logs: `docker-compose logs`

4. **Development Tools**
   - [ ] Linting passes: `make lint`
   - [ ] Type checking: `make typecheck`
   - [ ] Security checks: `make security`

If issues persist after this checklist, consult the specific debugging sections above or create a detailed issue report including:
- Error messages and stack traces
- Environment details (`uv --version`, `docker --version`)
- Steps to reproduce
- Expected vs actual behavior

---

*Update this file as technical implementation evolves. Ensure all major changes are documented here and referenced in plan.md and architecture.md as needed.*