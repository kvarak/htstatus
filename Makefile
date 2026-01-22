# HT Status Development Makefile
# Integrates UV (Python dependency management) and Docker Compose (services)

.PHONY: help setup dev services stop install update shell lint format fileformat fileformat-fix typecheck typesync security test test-coverage test-integration clean reset changelog db-migrate db-upgrade check-uv

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
	@echo "  make setup       # Initialize development environment"
	@echo "  make dev         # Start development server"
	@echo ""
	@echo "Development Workflow:"
	@echo "  make test-fast   # Quick validation during development"
	@echo "  make test        # Comprehensive testing before commits"
	@echo "  make test-all    # Full quality gates for deployment"
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

fileformat: ## Check file formatting (newline EOF, no trailing whitespace)
	@echo "📝 Checking file formatting standards..."
	@echo "   → Checking for newline at end of file..."
	@git ls-files | grep -E '\.(py|js|ts|tsx|html|css|scss|json|md|txt|yml|yaml|sh|sql|toml|cfg|ini|env)$$|^(Dockerfile|Makefile)' | \
	while read -r file; do \
		if test "$$(tail -c1 "$$file" | wc -l)" -eq 0; then \
			echo "❌ Missing newline at EOF: $$file"; \
			exit 1; \
		fi; \
	done
	@echo "   → Checking for trailing whitespace..."
	@git ls-files | grep -E '\.(py|js|ts|tsx|html|css|scss|json|md|txt|yml|yaml|sh|sql|toml|cfg|ini|env)$$|^(Dockerfile|Makefile)' | \
	while read -r file; do \
		if grep -q '[[:space:]]$$' "$$file"; then \
			echo "❌ Trailing whitespace found in: $$file"; \
			exit 1; \
		fi; \
	done
	@echo "✅ File formatting checks passed"

fileformat-fix: ## Auto-fix file formatting issues (newline EOF, trailing whitespace)
	@echo "🔧 Auto-fixing file formatting issues..."
	@echo "   → Adding newlines at end of files..."
	@git ls-files | grep -E '\.(py|js|ts|tsx|html|css|scss|json|md|txt|yml|yaml|sh|sql|toml|cfg|ini|env)$$|^(Dockerfile|Makefile)' | \
	while read -r file; do \
		if test "$$(tail -c1 "$$file" | wc -l)" -eq 0; then \
			echo "Adding newline to: $$file"; \
			echo "" >> "$$file"; \
		fi; \
	done
	@echo "   → Removing trailing whitespace..."
	@git ls-files | grep -E '\.(py|js|ts|tsx|html|css|scss|json|md|txt|yml|yaml|sh|sql|toml|cfg|ini|env)$$|^(Dockerfile|Makefile)' | \
	while read -r file; do \
		if grep -q '[[:space:]]$$' "$$file"; then \
			echo "Cleaned: $$file"; \
			sed -i '' 's/[[:space:]]*$$//' "$$file"; \
		fi; \
	done
	@echo "✅ File formatting auto-fix completed"

typecheck: check-uv ## Run mypy type checking
	@echo "🔬 Running type checking..."
	@$(UV) run mypy . --ignore-missing-imports

typesync: check-uv ## Validate SQLAlchemy models match TypeScript interfaces
	@echo "🔗 Validating type synchronization..."
	@$(UV) run python scripts/validate_types.py

security: check-uv ## Run bandit and safety security checks
	@echo "🔒 Running security checks..."
	@echo ""
	@echo "📋 Bandit Code Security Analysis:"
	@$(UV) run bandit -r app/ -c .bandit -f json 2>/dev/null > /tmp/bandit-results.json || $(UV) run bandit -r app/ -c .bandit > /tmp/bandit-results.txt || true
	@if [ -f /tmp/bandit-results.json ]; then \
		bandit_issues=$$(jq -r '.metrics._totals."SEVERITY.MEDIUM" + .metrics._totals."SEVERITY.HIGH"' /tmp/bandit-results.json 2>/dev/null || echo "0"); \
		if [ "$$bandit_issues" = "0" ]; then \
			echo "✅ No code security issues found"; \
		else \
			echo "⚠️  $$bandit_issues code security issue(s) found (run 'make security' for details)"; \
		fi; \
	fi
	@echo ""
	@echo "📋 Safety CVE Vulnerability Analysis:"
	@$(UV) run safety scan --output json --disable-optional-telemetry 2>/dev/null | tee /tmp/safety-results.json | jq -r 'if .scan_results.vulnerabilities | length == 0 then "✅ No CVE vulnerabilities in dependencies" else "⚠️  " + (.scan_results.vulnerabilities | length | tostring) + " CVE vulnerability/vulnerabilities found in dependencies" end' 2>/dev/null || $(UV) run safety scan

# Testing Infrastructure
test: services ## 🧪 Run comprehensive test suite (uses isolated groups to prevent fixture contamination)
	@echo "🧪 Running comprehensive test suite (isolated groups)..."
	@echo "   Note: Tests run in separate groups to prevent cross-module fixture contamination"
	@echo "   See TEST-012 in .project/backlog.md for technical details"
	@echo ""
	@$(MAKE) test-isolated

test-fast: check-uv services ## ⚡ Run critical tests only (quick development validation)
	@echo "⚡ Running fast test subset for development..."
	@$(UV) run pytest tests/test_basic.py tests/test_app_factory.py tests/test_auth.py tests/test_database.py -v --tb=short
	@echo "✅ Fast tests completed - run 'make test' for comprehensive validation"

test-config: check-uv ## 🔧 Run configuration tests specifically
	@echo "🔧 Running configuration tests..."
	@echo "   Note: These tests may fail if you have real CHPP credentials in .env"
	@echo "   See INFRA-018 in backlog.md for resolution details"
	@$(UV) run pytest tests/test_config.py -v --tb=short --cov=config --cov-report=term-missing
	@echo "✅ Configuration tests completed"

test-integration: check-uv services ## 🔗 Run integration tests with Docker services
	@echo "🔗 Running integration tests..."
	@$(UV) run pytest tests/integration/ -v --tb=short --cov=app --cov=models --cov=config --cov-report=term-missing
	@echo "✅ Integration tests completed"

test-coverage: check-uv services ## 📊 Run tests with detailed HTML coverage reporting
	@echo "📊 Running tests with detailed coverage analysis..."
	@$(UV) run pytest tests/ --cov=app --cov=models --cov=config --cov-report=html --cov-report=term-missing --cov-fail-under=90
	@echo "📋 Detailed coverage report generated in htmlcov/"

test-watch: check-uv services ## 👀 Run tests in watch mode (reruns on file changes)
	@echo "👀 Running tests in watch mode..."
	@$(UV) run pytest-watch tests/ -- -v --tb=short

test-core: check-uv services ## 🎯 Run core tests (basic, factory, auth, config)
	@echo "🎯 Running core tests (no database writes)..."
	@$(UV) run pytest tests/test_basic.py tests/test_app_factory.py tests/test_auth.py tests/test_config.py -v --tb=short --cov-fail-under=0
	@echo "✅ Core tests completed"

test-db: check-uv services ## 🗄️  Run database and business logic tests
	@echo "🗄️  Running database and business logic tests..."
	@$(UV) run pytest tests/test_database.py tests/test_business_logic.py tests/test_chpp_integration.py -v --tb=short --cov-fail-under=0
	@echo "✅ Database tests completed"

test-routes: check-uv services ## 🛣️  Run blueprint and route tests
	@echo "🛣️  Running blueprint and route tests..."
	@$(UV) run pytest tests/test_blueprint_*.py tests/test_minimal_routes.py tests/test_routes.py tests/test_strategic_routes.py tests/test_blueprint_routes_focused.py -v --tb=short --cov-fail-under=0
	@echo "✅ Route tests completed"

test-isolated: check-uv services ## 🔬 Run all tests in isolated groups (prevents cross-contamination)
	@echo "🔬 Running all tests in isolated groups to prevent fixture contamination..."
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "Group 1: Core Tests (basic, factory, auth, config)"
	@echo "═══════════════════════════════════════════════════════════════"
	@$(MAKE) test-core
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "Group 2: Database & Business Logic Tests"
	@echo "═══════════════════════════════════════════════════════════════"
	@$(MAKE) test-db
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "Group 3: Blueprint & Route Tests"
	@echo "═══════════════════════════════════════════════════════════════"
	@$(MAKE) test-routes
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "✅ All isolated test groups completed successfully"
	@echo "═══════════════════════════════════════════════════════════════"

test-all: ## ✅ Run all quality gates (fileformat + lint + security + typesync + config + comprehensive tests)
	@echo "🚀 Running complete quality gate validation..."
	@echo ""
	@echo "📋 Step 1/6: File Format Standards"
	@echo "=================================="
	@make fileformat 2>&1 | tee /tmp/fileformat-results.txt || true
	@echo ""
	@echo "📋 Step 2/6: Code Quality (Linting)"
	@echo "=================================="
	@make lint 2>&1 | tee /tmp/lint-results.txt || true
	@echo ""
	@echo "📋 Step 3/6: Security Analysis"
	@echo "============================="
	@make security 2>&1 | tee /tmp/security-results.txt || true
	@echo ""
	@echo "📋 Step 4/6: Type Synchronization"
	@echo "=============================="
	@make typesync 2>&1 | tee /tmp/typesync-results.txt || true
	@echo ""
	@echo "📋 Step 5/6: Configuration Validation"
	@echo "===================================="
	@make test-config 2>&1 | tee /tmp/config-results.txt || true
	@echo ""
	@echo "📋 Step 6/6: Application Coverage Analysis (Isolated Groups)"
	@echo "========================================="
	@make test-isolated 2>&1 | tee /tmp/test-results.txt
	@echo ""
	@scripts/quality-intelligence.sh

# Utility Commands
clean: ## Clean up temporary files, caches
	@echo "🧹 Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".DS_Store" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .coverage htmlcov/ *.log
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

