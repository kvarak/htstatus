# HT Status Development Makefile
# Integrates UV (Python dependency management) and Docker Compose (services)

.PHONY: help setup dev services stop install update shell lint format fileformat fileformat-fix typecheck security test test-coverage test-integration clean reset changelog release-detect release-notes release-tag release-docs db-migrate db-upgrade db-apply check-uv

# Variables
PYTHON := uv run python
PIP := uv pip
UV := uv
DOCKER_COMPOSE := docker-compose

# Common service startup function (consolidation)
define start_services
	@echo "🐳 Starting Docker Compose services..."
	@$(DOCKER_COMPOSE) up -d postgres redis 2>&1 | tee -a /tmp/docker-services.log
	@echo "✅ Services started (PostgreSQL, Redis)"
endef

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

# Development Environment Commands
setup: check-uv ## Initialize development environment (UV sync, Docker setup)
	@echo "🚀 Setting up HT Status development environment..."
	@$(UV) sync --dev
	@$(DOCKER_COMPOSE) pull
	@echo "✅ Development environment ready!"
	@echo "   Next: 'make dev' to start development server"


dev: check-uv services changelog ## Start development server (equivalent to run.sh)
	@echo "🌐 Starting HT Status development server..."
	@$(PYTHON) run.py

stop: ## Stop dev server and Docker Compose services
	@echo "🛑 Stopping HT Status development services..."
	@$(DOCKER_COMPOSE) stop 2>&1 | tee -a /tmp/docker-stop.log || docker compose stop 2>&1 | tee -a /tmp/docker-stop.log || true
	@pkill -f "uv run python.*run.py" 2>&1 | tee -a /tmp/flask-stop.log || true
	@pkill -f "flask run" 2>&1 | tee -a /tmp/flask-stop.log || true
	@echo "✅ Services stopped (Flask, Docker Compose)"

services: ## Start Docker Compose services only
	$(call start_services)

services-dev: ## Start services with development configuration
	@echo "🐳 Starting Docker Compose services (development)..."
	@$(DOCKER_COMPOSE) -f docker-compose.yml -f configs/docker-compose.development.yml up -d 2>&1 | tee -a /tmp/docker-dev.log
	@echo "✅ Services started (PostgreSQL, Redis, pgAdmin)"

services-staging: ## Start services with staging configuration
	@echo "🐳 Starting Docker Compose services (staging)..."
	@$(DOCKER_COMPOSE) -f docker-compose.yml -f configs/docker-compose.staging.yml up -d 2>&1 | tee -a /tmp/docker-staging.log
	@echo "✅ Services started (PostgreSQL, Redis) with staging configuration"

services-stop: ## Stop all Docker Compose services
	@echo "🛑 Stopping Docker Compose services..."
	@$(DOCKER_COMPOSE) down 2>&1 | tee -a /tmp/docker-down.log || docker compose down 2>&1 | tee -a /tmp/docker-down.log || true
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
	@$(PYTHON) -c "import IPython; IPython.start_ipython()" 2>&1 | tee /tmp/ipython-start.log || $(PYTHON)

# Code Quality Commands
lint: check-uv ## Run ruff linting
	@echo "🔍 Running ruff linting..."
	@mkdir -p out/tests && rm -f out/tests/$@.json
	@$(UV) run ruff check . 2>&1 | tee /tmp/ruff-output.txt; \
	if [ $${PIPESTATUS[0]} -eq 0 ]; then \
		echo "All checks passed!"; \
		scripts/qi-json.sh out/tests/lint.json "Code Quality" "make lint" PASSED 0 0 "0 errors" "excellent code quality"; \
	else \
		error_count=$$(grep -c "error" /tmp/ruff-output.txt || echo "0"); \
		app_errors=$$(grep -E '^(app/|models\.py|config\.py)' /tmp/ruff-output.txt | wc -l | tr -d ' '); \
		if [ "$$app_errors" = "0" ] 2>/dev/null; then \
			scripts/qi-json.sh out/tests/lint.json "Code Quality" "make lint" ISSUES $$error_count 0 "$$error_count errors" "dev scripts only"; \
		else \
			scripts/qi-json.sh out/tests/lint.json "Code Quality" "make lint" ISSUES 0 $$error_count "$$error_count errors" "$$app_errors in production code"; \
		fi; \
		exit 1; \
	fi

lint-fix: check-uv ## Auto-fix linting issues using ruff
	@echo "🔧 Auto-fixing linting issues..."
	@$(UV) run ruff check . --fix
	@echo "✅ Linting auto-fix completed"

fileformat: ## Check file formatting (newline EOF, no trailing whitespace)
	@mkdir -p out/tests && rm -f out/tests/$@.json
	@echo "📝 Checking file formatting standards..."
	@echo "   → Checking for newline at end of file..."
	@failed=false; \
	failed_count=0; \
	for file in $$(git ls-files | grep -E '\.(py|js|ts|tsx|html|css|scss|json|md|txt|yml|yaml|sh|sql|toml|cfg|ini|env)$$|^(Dockerfile|Makefile)'); do \
		if [ -f "$$file" ] && test "$$(tail -c1 "$$file" | wc -l)" -eq 0; then \
			echo "❌ Missing newline at EOF: $$file"; \
			failed=true; \
			failed_count=$$((failed_count + 1)); \
		fi; \
	done; \
	if [ "$$failed" = "true" ]; then \
		scripts/qi-json.sh out/tests/$@.json "File Format" "make fileformat" FAILED 0 $$failed_count "$$failed_count files" "missing newline at end of file"; \
		exit 1; \
	fi
	@echo "   → Checking for trailing whitespace..."
	@failed=false; \
	failed_count=0; \
	for file in $$(git ls-files | grep -E '\.(py|js|ts|tsx|html|css|scss|json|md|txt|yml|yaml|sh|sql|toml|cfg|ini|env)$$|^(Dockerfile|Makefile)'); do \
		if [ -f "$$file" ] && grep -q '[[:space:]]$$' "$$file"; then \
			echo "❌ Trailing whitespace found in: $$file"; \
			failed=true; \
			failed_count=$$((failed_count + 1)); \
		fi; \
	done; \
	if [ "$$failed" = "true" ]; then \
		scripts/qi-json.sh out/tests/$@.json "File Format" "make fileformat" FAILED 0 $$failed_count "$$failed_count files" "files have trailing whitespace"; \
		exit 1; \
	fi
	@total_files=$$(git ls-files | grep -E '\.(py|js|ts|tsx|html|css|scss|json|md|txt|yml|yaml|sh|sql|toml|cfg|ini|env)$$|^(Dockerfile|Makefile)' | while read f; do [ -f "$$f" ] && echo "$$f"; done | wc -l | tr -d ' '); \
	echo "✅ File formatting checks passed"; \
	scripts/qi-json.sh out/tests/$@.json "File Format" "make fileformat" PASSED 0 0 "$$total_files files" "consistent formatting"

fileformat-fix: ## Auto-fix file formatting issues (newline EOF, trailing whitespace)
	@echo "🔧 Auto-fixing file formatting issues..."
	@echo "   → Adding newlines at end of files..."
	@git ls-files | grep -E '\.(py|js|ts|tsx|html|css|scss|json|md|txt|yml|yaml|sh|sql|toml|cfg|ini|env)$$|^(Dockerfile|Makefile)' | \
	while read -r file; do \
		if [ -f "$$file" ] && test "$$(tail -c1 "$$file" | wc -l)" -eq 0; then \
			echo "Adding newline to: $$file"; \
			echo "" >> "$$file"; \
		fi; \
	done
	@echo "   → Removing trailing whitespace..."
	@git ls-files | grep -E '\.(py|js|ts|tsx|html|css|scss|json|md|txt|yml|yaml|sh|sql|toml|cfg|ini|env)$$|^(Dockerfile|Makefile)' | \
	while read -r file; do \
		if [ -f "$$file" ] && grep -q '[[:space:]]$$' "$$file"; then \
			echo "Cleaned: $$file"; \
			sed -i '' 's/[[:space:]]*$$//' "$$file"; \
		fi; \
	done
	@echo "✅ File formatting auto-fix completed"

typecheck: check-uv ## Run mypy type checking
	@echo "🔬 Running type checking..."
	@mkdir -p out/tests && rm -f out/tests/$@.json
	@$(UV) run mypy app/ models.py config.py --ignore-missing-imports --exclude="migrations|tests" 2>&1 | tee /tmp/typecheck-output.txt; \
	error_count=$$(grep -c "error:" /tmp/typecheck-output.txt || echo "0"); \
	if [ "$$error_count" -eq 0 ]; then \
		echo "✅ Type checking passed"; \
		scripts/qi-json.sh out/tests/$@.json "Type Checking" "make typecheck" PASSED 0 0 "type-safe code" "mypy validation successful"; \
	else \
		echo "❌ Type checking found $$error_count errors"; \
		scripts/qi-json.sh out/tests/$@.json "Type Checking" "make typecheck" FAILED 0 $$error_count "$$error_count type errors" "run 'mypy app/' to see details"; \
		exit 1; \
	fi


security-bandit: check-uv ## Run bandit code security analysis
	@mkdir -p out/tests
	@echo "🔒 Running bandit code security analysis..."
	@$(UV) run bandit -r app/ -c .bandit -f json 2>&1 | tee /tmp/bandit-results.json || $(UV) run bandit -r app/ -c .bandit 2>&1 | tee /tmp/bandit-results.txt || true
	@bandit_status="CLEAN"; \
	if [ -f /tmp/bandit-results.json ]; then \
		bandit_issues=$$(jq -r '.metrics._totals."SEVERITY.MEDIUM" + .metrics._totals."SEVERITY.HIGH"' /tmp/bandit-results.json 2>/dev/null || echo "0"); \
		if [ "$$bandit_issues" = "0" ]; then \
			echo "✅ No code security issues found"; \
			bandit_status="CLEAN"; \
		else \
			echo "⚠️  $$bandit_issues code security issue(s) found (run 'make security-bandit' for details)"; \
			bandit_status="$$bandit_issues ISSUE(S)"; \
		fi; \
	fi; \
	scripts/qi-json.sh out/tests/security-bandit.json "Bandit Code Analysis" "make security-bandit" PASSED 0 0 "bandit analysis complete" "code security validation" bandit="$$bandit_status"

security-deps: check-uv ## Run safety dependency vulnerability analysis
	@mkdir -p out/tests
	@echo "🔒 Running dependency vulnerability analysis..."
	@if $(UV) run safety scan --short-report 2>&1 | tee /tmp/safety-results.txt; then \
		safety_exit_code=0; \
	else \
		safety_exit_code=$$?; \
	fi; \
	total_cves=$$(grep -o "[0-9]* vulnerabilities found" /tmp/safety-results.txt | tail -1 | grep -o "[0-9]*" || echo "0"); \
	ignored_cves=$$(grep -o "[0-9]* ignored due to policy" /tmp/safety-results.txt | head -1 | grep -o "[0-9]*" || echo "0"); \
	active_cves=$$(( total_cves - ignored_cves )); \
	cve_status="NONE"; \
	deps_result="PASSED"; \
	if [ "$$total_cves" = "0" ]; then \
		echo "✅ No CVE vulnerabilities in dependencies"; \
		cve_status="NONE"; \
	elif [ "$$active_cves" = "0" ] && [ "$$total_cves" != "0" ]; then \
		echo "⚠️  $$total_cves CVE vulnerability(s) found but all ignored by policy"; \
		cve_status="$$total_cves IGNORED"; \
		deps_result="ISSUES"; \
	elif [ "$$ignored_cves" != "0" ]; then \
		echo "❌ $$active_cves active CVE vulnerability(s) found ($$ignored_cves ignored)"; \
		cve_status="$$active_cves ACTIVE, $$ignored_cves IGNORED"; \
		deps_result="FAILED"; \
	else \
		echo "❌ $$total_cves CVE vulnerability(s) found"; \
		cve_status="$$total_cves FOUND"; \
		deps_result="FAILED"; \
	fi; \
	scripts/qi-json.sh out/tests/security-deps.json "Dependency Analysis" "make security-deps" $$deps_result $$ignored_cves $$active_cves "dependency analysis complete" "CVE vulnerability validation" cve="$$cve_status"

test-single: check-uv services ## 🧪 Run a single test file (usage: make test-single FILE=tests/test_database.py)
	@test -n "$(FILE)" || { echo "❌ Usage: make test-single FILE=tests/test_something.py"; exit 1; }
	@echo "🧪 Running single test file: $(FILE)..."
	@mkdir -p out/tests && rm -f out/tests/test-single.json
	@$(UV) run pytest $(FILE) $${PYTEST_VERBOSE-"-v"} --tb=short --cov-fail-under=0 --json-report --json-report-file=out/tests/test-single.json
	@echo "✅ Single test file completed: $(FILE)"

EXCEPTIONS = __init__.py test_factories.py constants.py error_handlers.py

test-python: check-uv services ## 🧪 Run all Python tests with coverage
	@echo "🧪 Running all Python tests with coverage..."
	@mkdir -p out/tests && rm -f out/tests/$@.json out/tests/$@-cov.json
	@$(UV) run pytest tests/ $${PYTEST_VERBOSE-"-v"} --tb=short --cov=app --cov=models --cov=config --cov-report=term-missing --cov-report=html --cov-report=json:out/tests/$@-cov.json --cov-fail-under=40 --json-report --json-report-file=out/tests/$@.json

coverage-report: check-uv ## 📊 Generate detailed coverage analysis and testing priorities
	@echo "📊 Generating coverage analysis for test prioritization..."
	@mkdir -p out/tests && rm -f out/tests/$@.json
	@$(PYTHON) scripts/coverage_report.py --json > /tmp/coverage-analysis.json
	@coverage_pct=$$(jq -r '.total_coverage' /tmp/coverage-analysis.json); \
	gap_pct=$$(jq -r '.gap_to_target' /tmp/coverage-analysis.json); \
	priority_files=$$(jq -r '.priority_files | length' /tmp/coverage-analysis.json); \
	if [ "$$gap_pct" != "null" ] && [ $$(echo "$$gap_pct > 0" | bc -l) -eq 1 ]; then \
		printf "⚠️  Coverage: %.1f%% (%.1f%% below 50%% target)\n" "$$coverage_pct" "$$gap_pct"; \
		scripts/qi-json.sh out/tests/$@.json "Test Coverage Analysis" "make coverage-report" ISSUES 0 $$priority_files "$$priority_files priority files" "$$(printf "%.1f%% coverage, %.1f%% gap to target" "$$coverage_pct" "$$gap_pct")"; \
	else \
		printf "✅ Coverage: %.1f%% (target met)\n" "$$coverage_pct"; \
		scripts/qi-json.sh out/tests/$@.json "Test Coverage Analysis" "make coverage-report" PASSED 0 0 "coverage target met" "$$(printf "%.1f%% coverage exceeds 50%% target" "$$coverage_pct")"; \
	fi
	@$(PYTHON) scripts/coverage_report.py

coverage-json: check-uv ## 📊 Generate coverage analysis in JSON format
	@$(PYTHON) scripts/coverage_report.py --json

test-coverage-files: check-uv ## Check if all Python files have corresponding test files
	@echo "🔍 Checking for untested Python files..."
	@mkdir -p out/tests && rm -f out/tests/$@.json
	@missing_tests=""; \
	missing_count=0; \
	total_files=0; \
	excluded_count=0; \
	for pyfile in $$(find app/ -name "*.py" -type f | grep -v __pycache__ | sort) models.py config.py; do \
		if [ -f "$$pyfile" ]; then \
			basename=$$(basename $$pyfile .py); \
			filename=$$(basename $$pyfile); \
			skip_file=false; \
			for exception in $(EXCEPTIONS); do \
				if [ "$$filename" = "$$exception" ]; then \
					echo "⏭️  Skipping $$pyfile (exception: $$exception)"; \
					skip_file=true; \
					excluded_count=$$((excluded_count + 1)); \
					break; \
				fi; \
			done; \
			if [ "$$skip_file" = "false" ]; then \
				total_files=$$((total_files + 1)); \
				if [ "$$pyfile" = "models.py" ] || [ "$$pyfile" = "config.py" ]; then \
					testfile="tests/test_$$basename.py"; \
				else \
					testfile="tests/test_$$basename.py"; \
				fi; \
				if [ ! -f "$$testfile" ]; then \
					echo "❌ Missing test file: $$testfile (for $$pyfile)"; \
					missing_tests="$$missing_tests $$pyfile"; \
					missing_count=$$((missing_count + 1)); \
				fi; \
			fi; \
		fi; \
	done; \
	echo "📊 Excluded $$excluded_count files, checked $$total_files files"; \
	if [ "$$missing_count" -eq 0 ]; then \
		echo "✅ All $$total_files Python files have corresponding test files"; \
		scripts/qi-json.sh out/tests/$@.json "Test Coverage (files)" "make test-coverage-files" PASSED 0 0 "$$total_files files tested" "complete test file coverage ($$excluded_count excluded)"; \
	else \
		echo "❌ $$missing_count of $$total_files Python files missing test files:$$missing_tests"; \
		scripts/qi-json.sh out/tests/$@.json "Test Coverage (files)" "make test-coverage-files" FAILED 0 $$missing_count "$$missing_count missing tests" "$$missing_count files need test files ($$excluded_count excluded)"; \
		exit 1; \
	fi

check-chpp: ## Check CHPP API usage policy compliance
	@echo "🔍 Checking CHPP API usage policy..."
	@chmod +x scripts/check-chpp-usage.sh
	@./scripts/check-chpp-usage.sh

GATES = fileformat lint security-bandit security-deps test-coverage-files coverage-report check-chpp

test-all: check-uv services fileformat-fix lint-fix ## 🧪 Run complete quality gate validation
	@echo "🚀 Running complete quality gate validation"
	@mkdir -p out/tests && rm -f out/tests/*.json
	@count=1; \
	echo "🔎 [$$count] Running test-python..."; \
	PYTEST_VERBOSE="" $(MAKE) test-python || true; \
	for gate in $(GATES); do \
		count=$$((count + 1)); \
		echo "🔎 [$$count] Running $$gate..."; \
		PYTEST_VERBOSE="" $(MAKE) $$gate &>/dev/null || true; \
	done; \
	scripts/quality-intelligence.sh --expected-results $${count}

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

# Release Commands
release-detect: ## Detect if changes warrant a version release
	@echo "🔍 Detecting release-worthy changes..."
	@chmod +x scripts/release/detect_version_changes.sh
	@./scripts/release/detect_version_changes.sh

release-notes: ## Generate release notes (usage: make release-notes VERSION=1.2)
	@test -n "$(VERSION)" || { echo "❌ Usage: make release-notes VERSION=1.2"; exit 1; }
	@echo "📝 Generating release notes for version $(VERSION)..."
	@chmod +x scripts/release/update_releases.sh
	@./scripts/release/update_releases.sh $(VERSION)

release-tag: ## Create git tag (usage: make release-tag VERSION=1.2 MESSAGE="Release description")
	@test -n "$(VERSION)" || { echo "❌ Usage: make release-tag VERSION=1.2 MESSAGE=\"description\""; exit 1; }
	@test -n "$(MESSAGE)" || { echo "❌ Usage: make release-tag VERSION=1.2 MESSAGE=\"description\""; exit 1; }
	@echo "🏷️  Creating git tag $(VERSION)..."
	@git tag $(VERSION) -m "Release $(VERSION) - $(MESSAGE)"
	@echo "✅ Tag $(VERSION) created"

release-docs: ## Update all release documentation after tagging
	@echo "📚 Updating release documentation..."
	@$(MAKE) changelog
	@echo "✅ Release documentation updated"

# Database Commands
db-migrate: check-uv ## Create database migration (usage: make db-migrate MESSAGE="description")
	@echo "🗄️  Creating database migration..."
	@if [ -z "$(MESSAGE)" ]; then \
		echo "❌ Error: MESSAGE parameter required"; \
		echo "Usage: make db-migrate MESSAGE=\"description\""; \
		echo "Alternative: uv run alembic -c migrations/alembic.ini revision --autogenerate -m \"description\""; \
		exit 1; \
	fi
	@echo "Using Alembic directly to avoid Flask context issues..."
	@uv run alembic -c migrations/alembic.ini revision --autogenerate -m "$(MESSAGE)"

db-upgrade: check-uv services ## Apply database upgrades
	@echo "🗄️  Applying database upgrades..."
	@./scripts/database/upgrade_local_database.sh --force

db-apply: check-uv ## Apply database migrations using production-safe script
	@echo "🗄️  Applying database migrations (production-safe)..."
	@uv run python scripts/database/apply_migrations.py

# Deployment Commands
deploy-prepare: ## Prepare deployment environment (git, dependencies)
	@echo "🚀 Preparing deployment environment..."
	@echo "Installing system dependencies..."
	@if command -v apt-get >/dev/null 2>&1; then \
		sudo apt-get update -qq && sudo apt-get install -y jq; \
	elif command -v yum >/dev/null 2>&1; then \
		sudo yum install -y jq; \
	elif command -v brew >/dev/null 2>&1; then \
		brew install jq; \
	else \
		echo "⚠️  Could not detect package manager - please install jq manually"; \
	fi
	@echo "Installing uv..."
	@export PATH="$$HOME/.local/bin:$$PATH"; \
	if ! command -v uv >/dev/null 2>&1; then \
		pip3 install --user uv; \
	fi
	@echo "Ensuring ~/.local/bin in PATH..."
	@if ! grep -q 'export PATH="$$HOME/.local/bin:$$PATH"' ~/.bashrc 2>/dev/null; then \
		echo 'export PATH="$$HOME/.local/bin:$$PATH"' >> ~/.bashrc; \
		echo "✓ Added ~/.local/bin to PATH in ~/.bashrc"; \
	fi
	@echo "✅ Environment prepared"

deploy-sync: check-uv ## Sync code and dependencies
	@echo "🔄 Syncing code and dependencies..."
	@git fetch --all
	@git reset --hard $${DEPLOY_GIT_BRANCH:-next/main}
	@echo "Cleaning migration conflicts..."
	@find migrations/versions/ -name "*.py" -not -path "*/__pycache__/*" | while read -r file; do \
		if ! git ls-files --error-unmatch "$$file" >/dev/null 2>&1; then \
			echo "Removing untracked migration file: $$file"; \
			rm -f "$$file"; \
		fi; \
	done
	@export PATH="$$HOME/.local/bin:$$PATH"; \
	rm -rf .venv 2>/dev/null || true; \
	uv sync --python 3.14; \
	uv pip install requests requests-oauthlib
	@echo "✅ Code and dependencies synced"

deploy-docs: ## Update release documentation and changelog
	@echo "📚 Updating documentation..."
	@if $(MAKE) release-detect 2>/dev/null; then \
		echo "Version changes detected - updating release documentation..."; \
		$(MAKE) release-docs || echo "Release update failed, continuing..."; \
	else \
		echo "No version changes detected - generating changelog only..."; \
		$(MAKE) changelog; \
	fi
	@echo "✅ Documentation updated"

deploy-migrate: check-uv ## Apply database migrations safely
	@echo "🗄️  Applying database migrations..."
	@export PATH="$$HOME/.local/bin:$$PATH"; \
	uv run python scripts/database/apply_migrations.py
	@echo "✅ Database migrations completed"

deploy-finalize: ## Finalize deployment (restart service, cleanup)
	@echo "🏁 Finalizing deployment..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@touch app/routes.py
	@sudo systemctl restart htstatus
	@if [ $$? -eq 0 ]; then \
		echo "✅ Service restarted successfully"; \
		sudo systemctl status htstatus --no-pager -l | head -10; \
	else \
		echo "❌ Service restart failed!"; \
		exit 1; \
	fi
	@echo "✅ Finalization completed"

deploy: ## Smart deployment: --run if pushed, --dry-run if not (override with FORCE_DEPLOY=true)
	@echo "🚀 Preparing deployment..."
	@if [ "$${FORCE_DEPLOY}" = "true" ]; then \
		echo "🔓 FORCE_DEPLOY=true - skipping git push check"; \
		chmod +x scripts/deployment/deploy.sh; \
		./scripts/deployment/deploy.sh --run; \
	elif git diff --quiet && git diff --cached --quiet; then \
		if git log --oneline @{u}.. 2>/dev/null | grep -q .; then \
			echo "⚠️  WARNING: Local commits not pushed to remote"; \
			echo "   Use 'git push' first or set FORCE_DEPLOY=true"; \
			echo "   Running dry-run instead..."; \
			chmod +x scripts/deployment/deploy.sh; \
			./scripts/deployment/deploy.sh --run --dry-run; \
		else \
			echo "✅ Working directory clean and up to date with remote"; \
			chmod +x scripts/deployment/deploy.sh; \
			./scripts/deployment/deploy.sh --run; \
		fi; \
	else \
		echo "⚠️  WARNING: Uncommitted changes detected"; \
		echo "   Commit and push changes first or set FORCE_DEPLOY=true"; \
		echo "   Running dry-run instead..."; \
		chmod +x scripts/deployment/deploy.sh; \
		./scripts/deployment/deploy.sh --run --dry-run; \
	fi
