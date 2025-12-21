# HT Status Development Makefile
# Integrates UV (Python dependency management) and Docker Compose (services)

.PHONY: help setup dev services stop install update shell lint format typecheck security test test-coverage test-integration clean reset changelog db-migrate db-upgrade

# Variables
PYTHON := uv run python
PIP := uv pip
UV := uv
DOCKER_COMPOSE := docker-compose

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
setup: ## Initialize development environment (UV sync, Docker setup)
	@echo "🚀 Setting up HT Status development environment..."
	@$(UV) sync --dev
	@$(DOCKER_COMPOSE) pull
	@echo "✅ Development environment ready!"
	@echo "   Next: 'make dev' to start development server"

dev: services ## Start development server (equivalent to run.sh)
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

# Python Development Commands
install: ## Install dependencies using UV
	@echo "📦 Installing dependencies..."
	@$(UV) sync

update: ## Update dependencies and sync environment
	@echo "🔄 Updating dependencies..."
	@$(UV) sync --upgrade
	@$(UV) lock --upgrade

shell: ## Open Python shell in UV environment
	@echo "🐍 Opening Python shell..."
	@$(PYTHON) -c "import IPython; IPython.start_ipython()" 2>/dev/null || $(PYTHON)

# Code Quality Commands
lint: ## Run ruff linting
	@echo "🔍 Running ruff linting..."
	@$(UV) run ruff check . --fix

format: ## Run black and ruff formatting
	@echo "🎨 Formatting code..."
	@$(UV) run black .
	@$(UV) run ruff check . --fix --select I
	@$(UV) run ruff format .

typecheck: ## Run mypy type checking
	@echo "🔬 Running type checking..."
	@$(UV) run mypy . --ignore-missing-imports

security: ## Run bandit and safety security checks
	@echo "🔒 Running security checks..."
	@$(UV) run bandit -r app/ -f json 2>/dev/null || $(UV) run bandit -r app/
	@$(UV) run safety check

# Testing Infrastructure
test: services ## Run comprehensive test suite
	@echo "🧪 Running comprehensive test suite..."
	@$(UV) run pytest tests/ -v --tb=short --cov=app --cov=tests --cov-report=term-missing --cov-fail-under=0
	@echo "✅ Test suite completed"

test-unit: services ## Run unit tests only (fast)
	@echo "🔬 Running unit tests..."
	@$(UV) run pytest tests/ -v --tb=short -m "not integration"

test-integration: services ## Run integration tests with Docker services
	@echo "🔗 Running integration tests..."
	@$(UV) run pytest tests/ -v --tb=short -m "integration"

test-coverage: services ## Run tests with detailed coverage reporting
	@echo "📊 Running tests with coverage analysis..."
	@$(UV) run pytest tests/ --cov=app --cov=tests --cov-report=html --cov-report=term-missing --cov-fail-under=60
	@echo "📋 Coverage report generated in htmlcov/"

test-watch: services ## Run tests in watch mode (reruns on file changes)
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

changelog: ## Generate changelog (from changelog.sh)
	@echo "📝 Generating changelog..."
	@bash changelog.sh

# Database Commands
db-migrate: ## Run database migrations
	@echo "🗄️  Creating database migration..."
	@$(PYTHON) manage.py db migrate

db-upgrade: services ## Apply database upgrades
	@echo "🗄️  Applying database upgrades..."
	@$(PYTHON) manage.py db upgrade

# Legacy Support (deprecated but functional)
.PHONY: legacy-run legacy-changelog
legacy-run: ## [DEPRECATED] Use 'make dev' instead
	@echo "⚠️  WARNING: This command is deprecated. Use 'make dev' instead."
	@bash run.sh

legacy-changelog: ## [DEPRECATED] Use 'make changelog' instead
	@echo "⚠️  WARNING: This command is deprecated. Use 'make changelog' instead."
	@bash changelog.sh