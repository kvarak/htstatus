# HT Status Development Makefile
# Integrates UV (Python dependency management) and Docker Compose (services)

.PHONY: help setup dev services stop install update shell lint format typecheck security test test-coverage test-integration clean reset changelog db-migrate db-upgrade check-uv

# Variables
PYTHON := uv run python
PIP := uv pip
UV := uv
DOCKER_COMPOSE := docker-compose

# Check if UV is available, provide helpful error message if not
check-uv:
	@command -v uv >/dev/null 2>&1 || { \
		echo "❌ ERROR: UV is not installed"; \
		echo ""; \
		echo "UV is required for this project. Install it using one of these methods:"; \
		echo ""; \
		echo "📦 Using package managers:"; \
		echo "  # macOS:"; \
		echo "  brew install uv"; \
		echo ""; \
		echo "  # Linux (Ubuntu/Debian):"; \
		echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		echo ""; \
		echo "  # Linux (Arch):"; \
		echo "  pacman -S uv"; \
		echo ""; \
		echo "  # Or using pip (cross-platform):"; \
		echo "  pip install uv"; \
		echo ""; \
		echo "🔄 After installation, restart your terminal and try again."; \
		echo "📖 For more info: https://docs.astral.sh/uv/getting-started/installation/"; \
		exit 1; \
	}

# Default target
help: ## Show this help message
	@echo "HT Status Development Commands"
	@echo "=============================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick Start:"
	@echo "  make setup    # Initialize development environment"
	@echo "  make dev      # Start development server"
	@echo ""

# Development Environment Commands
setup: check-uv ## Initialize development environment (UV sync, Docker setup)
	@echo "🚀 Setting up HT Status development environment..."
	@$(UV) sync --dev
	@$(DOCKER_COMPOSE) pull
	@echo "✅ Development environment ready!"
	@echo "   Next: 'make dev' to start development server"

dev: check-uv services ## Start development server (equivalent to run.sh)
	@echo "🌐 Starting HT Status development server..."
	@$(PYTHON) run.py

stop: ## Stop dev server and Docker Compose services
	@echo "🛑 Stopping HT Status development services..."
	@$(DOCKER_COMPOSE) stop >/dev/null 2>&1 || docker compose stop >/dev/null 2>&1 || true
	@pkill -f "python.*run.py" >/dev/null 2>&1 || true
	@pkill -f "flask run" >/dev/null 2>&1 || true
	@echo "✅ Services stopped (Flask, Docker Compose)"

services: ## Start Docker Compose services only
	@echo "🐳 Starting Docker Compose services..."
	@$(DOCKER_COMPOSE) up -d postgres redis
	@echo "✅ Services started (PostgreSQL, Redis)"

services-dev: ## Start services with development configuration
	@echo "🐳 Starting Docker Compose services (development)..."
	@$(DOCKER_COMPOSE) -f docker-compose.yml -f configs/docker-compose.development.yml up -d
	@echo "✅ Services started (PostgreSQL, Redis, pgAdmin)"

services-staging: ## Start services with staging configuration
	@echo "🐳 Starting Docker Compose services (staging)..."
	@$(DOCKER_COMPOSE) -f docker-compose.yml -f configs/docker-compose.staging.yml up -d
	@echo "✅ Services started (PostgreSQL, Redis) with staging configuration"

services-stop: ## Stop all Docker Compose services
	@echo "🛑 Stopping Docker Compose services..."
	@$(DOCKER_COMPOSE) down >/dev/null 2>&1 || docker compose down >/dev/null 2>&1 || true
	@echo "✅ Services stopped"

config-validate: check-uv ## Validate configuration for current environment
	@echo "🔍 Validating configuration..."
	@$(PYTHON) -c "from config import get_config; cfg = get_config(); cfg.validate_config(); print('✅ Configuration is valid')"

config-help: ## Show configuration setup help
	@echo "⚙️  HTStatus Configuration Help"
	@echo "=============================="
	@echo ""
	@echo "Environment Templates:"
	@echo "  Development: cp environments/.env.development.example .env"
	@echo "  Staging:     cp environments/.env.staging.example .env"
	@echo "  Production:  cp environments/.env.production.example .env"
	@echo ""
	@echo "Environment Detection:"
	@echo "  Set FLASK_ENV=development|staging|production"
	@echo ""
	@echo "Validation:"
	@echo "  make config-validate  # Check current configuration"
	@echo ""
	@echo "Templates provide:"
	@echo "  - Environment-specific defaults"
	@echo "  - Security guidelines"
	@echo "  - Required vs optional settings"
	@echo "  - Deployment instructions"

# Python Development Commands
install: check-uv ## Install dependencies using UV
	@echo "📦 Installing dependencies..."
	@$(UV) sync

update: check-uv ## Update dependencies and sync environment
	@echo "🔄 Updating dependencies..."
	@$(UV) sync --upgrade
	@$(UV) lock --upgrade

shell: check-uv ## Open Python shell in UV environment
	@echo "🐍 Opening Python shell..."
	@$(PYTHON) -c "import IPython; IPython.start_ipython()" 2>/dev/null || $(PYTHON)

# Code Quality Commands
lint: check-uv ## Run ruff linting
	@echo "🔍 Running ruff linting..."
	@$(UV) run ruff check . --fix

format: check-uv ## Run black and ruff formatting
	@echo "🎨 Formatting code..."
	@$(UV) run black .
	@$(UV) run ruff check . --fix --select I
	@$(UV) run ruff format .

typecheck: check-uv ## Run mypy type checking
	@echo "🔬 Running type checking..."
	@$(UV) run mypy . --ignore-missing-imports

security: check-uv ## Run bandit and safety security checks
	@echo "🔒 Running security checks..."
	@$(UV) run bandit -r app/ -f json 2>/dev/null || $(UV) run bandit -r app/
	@$(UV) run safety check

# Testing Infrastructure
# Testing Infrastructure with fallback support
test: services ## Run comprehensive test suite
	@echo "🧪 Running comprehensive test suite..."
	@if command -v uv >/dev/null 2>&1; then \
		$(UV) run pytest tests/ -v --tb=short --cov=app --cov=models --cov=config --cov-report=term-missing --cov-fail-under=0; \
	else \
		echo "⚠️  UV not available, falling back to system Python..."; \
		python -m pytest tests/ -v --tb=short --cov=app --cov=models --cov=config --cov-report=term-missing --cov-fail-under=0 2>/dev/null || \
		python3 -m pytest tests/ -v --tb=short --cov=app --cov=models --cov=config --cov-report=term-missing --cov-fail-under=0 2>/dev/null || \
		{ echo "❌ ERROR: Neither UV nor pytest available. Please install UV or pytest."; exit 1; }; \
	fi
	@echo "✅ Test suite completed successfully with config.py coverage included"

test-unit: check-uv services ## Run unit tests only (fast)
	@echo "🔬 Running unit tests..."
	@$(UV) run pytest tests/ -v --tb=short -m "not integration"

test-integration: check-uv services ## Run integration tests with Docker services
	@echo "🔗 Running integration tests..."
	@$(UV) run pytest tests/ -v --tb=short -m "integration"

test-coverage: check-uv services ## Run tests with detailed coverage reporting
	@echo "📊 Running tests with coverage analysis..."
	@$(UV) run pytest tests/ --cov=app --cov=models --cov=config --cov-report=html --cov-report=term-missing --cov-fail-under=80
	@echo "📋 Coverage report generated in htmlcov/"

test-watch: check-uv services ## Run tests in watch mode (reruns on file changes)
	@echo "👀 Running tests in watch mode..."
	@$(UV) run pytest-watch tests/ -- -v --tb=short

test-all: lint security test ## Run all quality gates (lint + security + tests)
	@echo "✅ All quality gates passed!"

# Utility Commands
clean: ## Clean up temporary files, caches
	@echo "🧹 Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .coverage htmlcov/ .ruff_cache/
	@echo "✅ Cleanup complete"

reset: clean ## Reset environment (clean + fresh install)
	@echo "🔄 Resetting environment..."
	@rm -rf .venv/
	@$(UV) sync --dev
	@echo "✅ Environment reset complete"

changelog: ## Generate changelog (from scripts/changelog.sh)
	@echo "📝 Generating changelog..."
	@bash scripts/changelog.sh

# Database Commands
db-migrate: check-uv ## Run database migrations
	@echo "🗄️  Creating database migration..."
	@$(PYTHON) manage.py db migrate

db-upgrade: check-uv services ## Apply database upgrades
	@echo "🗄️  Applying database upgrades..."
	@$(PYTHON) manage.py db upgrade

# Legacy Support (deprecated but functional)
.PHONY: legacy-run legacy-changelog
legacy-run: ## [DEPRECATED] Use 'make dev' instead
	@echo "⚠️  WARNING: This command is deprecated. Use 'make dev' instead."
	@bash run.sh

legacy-changelog: ## [DEPRECATED] Use 'make changelog' instead
	@echo "⚠️  WARNING: This command is deprecated. Use 'make changelog' instead."
	@bash scripts/changelog.sh