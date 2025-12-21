# HT Status

## Local Development with UV

This project uses [UV](https://docs.astral.sh/uv/) for fast Python dependency management and virtual environment handling.

### Quick Start

1. **Install Dependencies**:
   ```bash
   # Install UV (if not already installed)
   brew install uv

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

   # Install Python dependencies (creates .venv automatically)
   uv sync --extra dev
   ```

3. **Start Services & Application**:
   ```bash
   # Start PostgreSQL and Redis services
   docker-compose up -d

   # Wait for database to be ready
   ./docker/wait-for-postgres.sh

   # Run database migrations
   uv run python manage.py db upgrade

   # Start Flask development server
   uv run python run.py
   # or
   ./run.sh
   ```

4. **Access Application**:
   - **Flask App**: http://localhost:5000
   - **React Dev Server**: `npm run dev` (http://localhost:8080)
   - **pgAdmin** (optional): `docker-compose --profile admin up -d` (http://localhost:5050)

- `uv sync` - Install/update dependencies
- `uv sync --extra dev` - Include development dependencies
- `uv add <package>` - Add new dependency
- `uv remove <package>` - Remove dependency
- `uv run <command>` - Run command in project environment
- `uv lock` - Update lock file

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

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

**Required Configuration:**
- `CONSUMER_KEY` - Your Hattrick CHPP consumer key
- `CONSUMER_SECRETS` - Your Hattrick CHPP consumer secret
- `CALLBACK_URL` - OAuth callback URL (usually http://localhost:5000/login)
- `SECRET_KEY` - Flask secret key (change from default)

**Database Configuration (automatic with Docker Compose):**
- `DATABASE_URL` - PostgreSQL connection string
- `POSTGRES_*` - Individual database connection parameters

### Legacy config.py (Still Supported)

You can still use a `config.py` file, but environment variables take priority:

```
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
