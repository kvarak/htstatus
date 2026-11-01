# HattrickPlanner development commands (`make help`). Production runs the Docker
# image built by CI; see DEPLOYMENT.md.

.PHONY: help install update requirements-txt serve stop services docker-up docker-check \
	lint lint-templates fileformat security-bandit check-chpp test-python test-single test-all format \
	clean changelog release-tag db-migrate db-upgrade db-copy-production check-uv check-venv

UV := uv
PYTHON := uv run python

help: ## Show the main commands (the Makefile has a few more)
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

check-uv:
	@command -v uv >/dev/null 2>&1 || { echo "❌ uv is not installed: https://docs.astral.sh/uv/getting-started/installation/ (macOS: brew install uv)"; exit 1; }

check-venv: check-uv
	@if [ -d .venv ] && ! .venv/bin/python --version >/dev/null 2>&1; then \
		echo "❌ .venv is broken (Python upgraded?). Fix: rm -rf .venv && make install"; exit 1; \
	fi

# Setup
install: check-uv ## Install dependencies (incl. dev tools)
	@$(UV) sync --extra dev

# Upgrade dependencies and refresh requirements.txt
update: check-uv
	@$(UV) sync --upgrade --extra dev
	@$(UV) lock --upgrade
	@$(MAKE) --no-print-directory requirements-txt

# Regenerate requirements.txt (the Docker image and Dependabot use it) after changing dependencies
requirements-txt: check-uv
	@$(UV) pip compile pyproject.toml -o requirements.txt --quiet
	@echo "✅ requirements.txt updated"

# Running
serve: check-venv services changelog ## Start the development server
	@$(PYTHON) run.py

# Start the dev PostgreSQL
services:
	@docker compose up -d --wait --remove-orphans postgres

stop: ## Stop the dev server and Docker Compose services
	@docker compose stop || true
	@pkill -f "uv run python.*run.py" || true
	@echo "✅ Stopped"

# Docker image (same as production). The image has no .git, so the version
# and the /changes data are prepared here (CI does the same).
docker-up: ## Build and run the production image on http://localhost:5010 (WEB_PORT to change)
	@bash scripts/changelog.sh >/dev/null
	@docker compose --profile web build --build-arg APP_VERSION=$$(git describe --tags) web
	@docker compose --profile web up -d --wait postgres web
	@echo "✅ Running at http://localhost:$${WEB_PORT:-5010} (logs: docker compose logs -f web; make stop)"

docker-check: ## Lint and tests inside the Docker test image
	@docker compose up -d --wait postgres
	@docker compose --profile test run --rm --build test

# Quality gates (test-all runs them all)
# ruff + black check (as CI)
lint: check-uv
	@$(UV) run ruff check .
	@$(UV) run black --check --quiet .

# djlint template check
lint-templates: check-uv
	@$(UV) run djlint app/templates/ --check

FORMAT_FILES = git ls-files | grep -E '\.(py|js|ts|tsx|html|css|scss|json|md|txt|yml|yaml|sh|sql|toml|cfg|ini|env)$$|^(Dockerfile|Makefile)'

# Check newline at EOF and no trailing whitespace
fileformat:
	@failed=0; \
	for file in $$($(FORMAT_FILES)); do \
		[ -f "$$file" ] || continue; \
		if test "$$(tail -c1 "$$file" | wc -l)" -eq 0; then echo "❌ Missing newline at EOF: $$file"; failed=1; fi; \
		if grep -q '[[:space:]]$$' "$$file"; then echo "❌ Trailing whitespace: $$file"; failed=1; fi; \
	done; \
	[ "$$failed" -eq 0 ] && echo "✅ File formatting checks passed"; \
	exit $$failed

# bandit security check (medium+ severity fails)
security-bandit: check-uv
	@$(UV) run bandit -r app/ -c .bandit -ll -q

# CHPP API usage policy (only login/OAuth/update may call CHPP)
check-chpp:
	@./scripts/check-chpp-usage.sh

# Python tests with coverage
test-python: check-uv services
	@$(UV) run pytest tests/ $${PYTEST_VERBOSE-"-v"} --tb=short --cov-report=term-missing --cov-report=html

test-single: check-uv services ## One test file: make test-single FILE=tests/test_x.py
	@test -n "$(FILE)" || { echo "❌ Usage: make test-single FILE=tests/test_something.py"; exit 1; }
	@$(UV) run pytest $(FILE) $${PYTEST_VERBOSE-"-v"} --tb=short --cov-fail-under=0

format: check-uv ## Auto-fix formatting: files, ruff/black, templates
	@for file in $$($(FORMAT_FILES)); do \
		[ -f "$$file" ] || continue; \
		if test "$$(tail -c1 "$$file" | wc -l)" -eq 0; then echo "" >> "$$file"; echo "Added newline: $$file"; fi; \
		if grep -q '[[:space:]]$$' "$$file"; then sed -i '' 's/[[:space:]]*$$//' "$$file"; echo "Cleaned: $$file"; fi; \
	done
	@$(UV) run ruff check --fix --quiet .
	@$(UV) run black --quiet .
	@$(UV) run djlint app/templates/ --reformat --quiet >/dev/null || true
	@echo "✅ Formatted"

GATES = test-python fileformat lint lint-templates security-bandit check-chpp

test-all: services format ## Format, then run all quality gates and summarise
	@failed=""; \
	for gate in $(GATES); do \
		if PYTEST_VERBOSE="-q" $(MAKE) --no-print-directory $$gate > /tmp/htstatus-gate-$$gate.log 2>&1; then \
			echo "✅ $$gate"; \
		else \
			echo "❌ $$gate (see /tmp/htstatus-gate-$$gate.log)"; failed="$$failed $$gate"; \
		fi; \
	done; \
	if [ -n "$$failed" ]; then echo "Failed gates:$$failed"; exit 1; fi; \
	echo "🎉 All quality gates passed"

# Remove caches and coverage output
clean:
	@find . -path ./.venv -prune -o \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".ruff_cache" \) -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -path ./.venv -prune -o \( -name "*.pyc" -o -name ".DS_Store" \) -type f -exec rm -f {} + 2>/dev/null || true
	@rm -rf .coverage htmlcov/

# Releases (see DEPLOYMENT.md "Releasing")
# Build the /changes page data from git and the release notes
changelog:
	@bash scripts/changelog.sh

release-tag: ## Tag a release: make release-tag VERSION=3.25 MESSAGE="..."
	@test -n "$(VERSION)" && test -n "$(MESSAGE)" || { echo "❌ Usage: make release-tag VERSION=X.Y MESSAGE=\"description\""; exit 1; }
	@git tag $(VERSION) -m "Release $(VERSION) - $(MESSAGE)"
	@echo "✅ Tag $(VERSION) created"

# Database (local dev; production migrates on container start)
db-migrate: check-uv ## New migration: make db-migrate MESSAGE="description"
	@test -n "$(MESSAGE)" || { echo "❌ Usage: make db-migrate MESSAGE=\"description\""; exit 1; }
	@$(UV) run alembic -c migrations/alembic.ini revision --autogenerate -m "$(MESSAGE)"

db-upgrade: check-uv services ## Apply migrations to the dev database
	@$(PYTHON) scripts/database/apply_migrations.py

db-copy-production: services ## Replace the dev database with a copy of production (PROD_SERVER/PROD_APP_DIR in .env)
	@./scripts/database/copy_production_db.sh
