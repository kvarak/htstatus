
## Plan

## Project Requirements
**⚠️ All work must comply with these requirements:**

### Core Quality Standards
- **Database Integrity**: DB schema changes must be backwards compatible - all migrations must be additive only (no column drops, no breaking changes to existing data)
- **Testing Gate**: ALWAYS verify changes with `make test` before completion - all tests must pass
- **Code Quality Gate**: ALWAYS run `make lint` and address critical issues before completion

### Documentation Standards (Enforced)
- **ARCHITECTURE.md**: Update within same PR/task when structural changes are made (new components, workflow changes, dependency updates)
- **PLAN.md**: Mark completed items ✅ and update status when tasks finish - keep dependency chain current
- **README.md Cross-Platform**: ALL installation commands, setup steps, and external dependencies MUST provide explicit alternatives for both Linux and macOS (FORBIDDEN: platform-specific commands like 'brew install' without alternatives)

### Development Environment Standards
- **Python Dependency Management**: Must use UV for all Python dependencies - no direct pip usage in documentation or scripts
- **Service Orchestration**: Docker Compose must provide complete local development environment (PostgreSQL, Redis, all required services)
- **Container Platform Compatibility**: Must work with Docker, Podman, Colima - use standard compose syntax, test with alternatives when possible

### Security & Maintenance Standards
- **Secrets Management**: Never commit API keys, passwords, or sensitive config - use environment variables with .env.example templates
- **Dependency Security**: Run `make security` for dependency vulnerability scanning on major updates
- **Migration Safety**: Database migrations must be tested on copy of production data structure before deployment


---

## Current Status
- **COMPLETED**: Task 1 - Architecture documentation
- **COMPLETED**: Task 2 - Local Development Modernization (UV + Docker Compose + Makefile) ✅
- **COMPLETED**: Task 2.7 - Code Quality Tools (integrated in Makefile) ✅
- **NEXT**: Task 2.0.1 - Code Quality & Security Remediation (CRITICAL - quality gate failures)
- **BLOCKED**: Task 2.1 - Testing Foundation (blocked by quality issues)
- **BLOCKED**: All Task 3+ (blocked by quality baseline requirement)
- **PRIORITY**: Fix 3 security vulnerabilities and 14 linting violations before proceeding

**Key Achievement**: Modern development stack successfully established with UV + Docker + Make integration.
**Critical Issue**: Enhanced project requirements revealed quality gate failures that must be resolved before testing foundation can be built.
**Next Focus**: Address security vulnerabilities (CWE-78 subprocess issues) and code quality violations to establish proper development standards.

---

## Task 1 - Architecture Documentation
**Status: ✅ COMPLETED**
- [x] Create a ARCHITECTURE.md with the current structure

## Task 2 - Local Development Modernization
**Status: ✅ COMPLETED**

**Implementation Plan:**
1. **UV Migration (2A)**: ✅ COMPLETED - Created pyproject.toml, migrated dependencies, added dev tools
2. **Docker Compose Setup (2B)**: ✅ COMPLETED - Created docker-compose.yml with PostgreSQL + Redis, environment variables
3. **Makefile Integration (2C)**: ✅ COMPLETED - Added comprehensive Makefile with all required commands

**Key Requirements Fulfilled:**
- ✅ UV for Python dependency management
- ✅ Docker Compose for complete development environment (PostgreSQL, Redis, services)
- ✅ `make test` command availability (**CRITICAL REQUIREMENT SATISFIED**)
- ✅ Backward compatible database changes
- ✅ Documentation updated (ARCHITECTURE.md, PLAN.md, README.md)

**Final State:**
- ✅ Uses UV for fast Python dependency management (replaces pip/requirements.txt)
- ✅ Development dependencies configured (pytest, ruff, black, mypy, etc.)
- ✅ Virtual environment (.venv) created automatically by UV
- ✅ Documentation updated with UV + Docker Compose + Makefile workflow
- ✅ Docker Compose provides PostgreSQL + Redis services
- ✅ Environment variable configuration with backwards compatibility
- ✅ **Makefile with standardized development commands** - Replaces scattered shell scripts
- ✅ **`make test`, `make dev`, `make setup` commands available**
- ✅ GitHub Actions CI exists (basic flake8 linting)
- ✅ Dual frontend architecture documented
- ✅ Legacy scripts (run.sh, changelog.sh) still functional but deprecated

**Task 2 Summary:** Successfully modernized the local development workflow with UV for Python dependency management, Docker Compose for service orchestration, and a comprehensive Makefile providing standardized development commands. All critical requirements including `make test` are now available.

### Task 2.0.1 - Code Quality & Security Remediation
**Status: 🔄 NEXT - CRITICAL (blocks Task 2.1)**
**Priority: HIGH - Must complete before testing foundation**

**Quality Gate Violations Identified:**
- [ ] **Fix Security Issues (CRITICAL)**: Address 3 security violations in app/routes.py
  - [ ] CWE-78: Subprocess usage security review (line 27: git describe subprocess call)
  - [ ] B607: Review partial executable paths in subprocess calls
  - [ ] B603: Validate subprocess input sanitization
- [ ] **Resolve Linting Violations**: Address 14 code quality issues identified by ruff
  - [ ] E402: Fix module-level import placement (app/__init__.py:16)
  - [ ] SIM115: Convert file operations to context managers (3 violations in routes.py)
  - [ ] SIM108: Convert if-else blocks to ternary operators (8 violations)
  - [ ] SIM102: Combine nested if statements (2 violations)
- [ ] **Enhance Quality Enforcement**: Update development workflow for automatic quality gates
  - [ ] Create `make test-all` command that enforces lint + security + test gates
  - [ ] Update documentation with quality requirements compliance
  - [ ] Ensure CI/CD pipeline includes quality gate enforcement

**Rationale:** The enhanced project requirements revealed that Task 2C was completed with failing quality gates (`make lint` and `make security` both exit with errors). These must be resolved to establish proper development standards before building testing infrastructure.

### Task 2.1 - Testing Foundation
**Status: ⏳ BLOCKED (requires Task 2.0.1 completion for quality baseline)**
- [ ] Create comprehensive test suite (unit, integration, API tests) using UV and Docker
- [ ] Implement proper Flask application factory pattern for testability
- [ ] Add test database configuration and fixtures
- [ ] Create test utilities for CHPP API mocking

### Task 2.2 - Testing Infrastructure
**Status: ⏳ BLOCKED (requires Task 2.0.1 → 2.1 completion)**
- [ ] Add test coverage reporting and CI/CD pipeline setup with UV/Docker integration

### Task 2.3 - VS Code Integration
**Status: ⏳ BLOCKED (requires Task 2.0.1 → 2.1 completion)**
- [ ] Setup VS Code Python testing extensions with UV and Docker integration

### Task 2.4 - VS Code Configuration
**Status: ⏳ BLOCKED (requires Task 2.3)**
- [ ] Configure tests to run on file save using UV environment

### Task 2.5 - Git Integration
**Status: ⏳ BLOCKED (requires Task 2.0.1 → 2.1 completion)**
- [ ] Add pre-commit hooks for automated testing using UV

### Task 2.6 - Git Integration Extended
**Status: ⏳ BLOCKED (requires Task 2.5)**
- [ ] Setup commit-msg hooks for test validation

### Task 2.7 - Code Quality Tools
**Status: ✅ COMPLETED (implemented in Makefile)**
- [x] Setup linting tools (ruff, black, isort) with UV and VS Code integration
- [x] Integrated make lint, make format, make typecheck, make security commands
- [x] Added comprehensive code quality pipeline in development workflow

### Task 2.8 - API Documentation
**Status: ⏳ BLOCKED (requires Task 2.0.1 → 2.1 completion)**
- [ ] Document and test existing Flask API endpoints

---

## Task 3 - Code Cleanup
**Status: ⏳ BLOCKED (requires Task 2.0.1 → 2.1 completion - quality baseline required before major refactoring)**

### Task 3.1 - Constants Extraction
**Status: ⏳ BLOCKED (requires Task 2.0.1 → 2.1 completion)**
- [ ] Extract hardcoded constants (HTmatchtype, HTmatchrole) to separate config files

### Task 3.2 - Code Refactoring
**Status: ⏳ BLOCKED (requires Task 2.0.1 → 2.1 completion)**
- [ ] Refactor routes.py (1976 lines) - split into smaller modules by functionality

### Task 3.3 - Type Safety
**Status: ⏳ BLOCKED (requires Task 2.0.1 → 2.1 completion)**
- [ ] Add type hints to Python functions for better maintainability

### Task 3.4 - Configuration Management
**Status: ⏳ BLOCKED (requires Task 2.0.1 → 2.1 completion)**
- [ ] Add proper configuration management (environment variables, secrets)

---

## Task 4 - Performance Optimization
**Status: ⏳ BLOCKED (requires Task 3 completion)**

### Task 4.1 - Caching Layer
**Status: ⏳ BLOCKED (requires Task 3 completion)**
- [ ] Add caching layer for CHPP API responses

### Task 4.2 - Async Processing
**Status: ⏳ BLOCKED (requires Task 3 completion)**
- [ ] Implement async Python for better concurrency with CHPP calls

### Task 4.3 - Performance Monitoring
**Status: ⏳ BLOCKED (requires Task 3 completion)**
- [ ] Add performance monitoring to measure optimization impact

### Task 4.4 - Database Preparation
**Status: ⏳ BLOCKED (requires Task 3 completion)**
- [ ] Create database backup/migration strategy

### Task 4.5 - Database Indexes
**Status: ⏳ BLOCKED (requires Task 3 completion)**
- [ ] Add database indexes for performance (ht_id fields, data_date)

### Task 4.6 - Query Optimization
**Status: ⏳ BLOCKED (requires Task 3 completion)**
- [ ] Optimize player_diff queries for large datasets

---

## Task 5 - Python Modernization
**Status: ⏳ BLOCKED (requires Task 4 completion)**

### Task 5.1 - Flask Modernization
**Status: ⏳ BLOCKED (requires Task 4 completion)**
- [ ] Migrate to modern Flask patterns (blueprints, application factory)

### Task 5.2 - API Layer
**Status: ⏳ BLOCKED (requires Task 4 completion)**
- [ ] Add API layer for React frontend (Flask-RESTful or FastAPI integration)

### Task 5.3 - Documentation
**Status: ⏳ BLOCKED (requires Task 4 completion)**
- [ ] Setup Sphinx for Python documentation generation

---

## Task 6 - Deployment & Production
**Status: ⏳ BLOCKED (requires Task 5 completion)**

### Task 6.1 - Production Containerization
**Status: ⏳ BLOCKED (requires Task 5 completion) - Development Docker already in Task 2**
- [ ] Optimize Docker for production deployment (multi-stage builds, security hardening)

### Task 6.2 - CI/CD Pipeline
**Status: ⏳ BLOCKED (requires Task 5 completion) - UV/Docker foundation ready**
- [ ] Implement CI/CD pipeline with automated testing using UV and Docker

### Task 6.3 - Security
**Status: ⏳ BLOCKED (requires Task 5 completion)**
- [ ] Add security scanning for dependencies and code (bandit, safety) integrated with UV

---

## Task 7 - Frontend Completion
**Status: ⏳ BLOCKED (requires Task 6 completion)**
- [ ] Complete React frontend migration from Jinja2 templates
