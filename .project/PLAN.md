
## Plan

## Project Requirements
**⚠️ All work must comply with these requirements:**
- DB always needs to be backwards compatible
- Always test with `make test`
- Always keep ARCHITECTURE.md up to date
- Always keep PLAN.md up to date, adding new items and checking/updating done items
- Always keep project requirements up to date in this PLAN.md file
- Always keep README.md up to date, adding/modifying external information
- Local development must use UV for Python dependency management
- Docker Compose must provide complete local development environment (PostgreSQL, services)

---

## Current Status
- **COMPLETED**: Task 1 - Architecture documentation
- **NEXT**: Task 2 - Local Development Modernization (UV + Docker Compose + Makefile)
- **PRIORITY**: Developer experience with UV for Python + Docker Compose for services

---

## Task 1 - Architecture Documentation
**Status: ✅ COMPLETED**
- [x] Create a ARCHITECTURE.md with the current structure

## Task 2 - Local Development Modernization
**Status: 🔄 NEXT - IN PROGRESS**

**Implementation Plan:**
1. **UV Migration (2A)**: ✅ COMPLETED - Created pyproject.toml, migrated dependencies, added dev tools
2. **Docker Compose Setup (2B)**: ✅ COMPLETED - Created docker-compose.yml with PostgreSQL + Redis, environment variables
3. **Makefile Integration (2C)**: 🔄 NEXT - Consolidate shell scripts, add UV/Docker Compose commands, testing infrastructure

**Key Requirements to Fulfill:**
- ✅ UV for Python dependency management
- ✅ Docker Compose for complete development environment (PostgreSQL, Redis, services)
- ⏳ `make test` command availability
- ⏳ Backward compatible database changes
- ✅ Keep documentation updated (ARCHITECTURE.md, PLAN.md, README.md)

**Current State Analysis:**
- ✅ Uses UV for fast Python dependency management (replaces pip/requirements.txt)
- ✅ Development dependencies configured (pytest, ruff, black, mypy, etc.)
- ✅ Virtual environment (.venv) created automatically by UV
- ✅ Documentation updated with UV + Docker Compose workflow
- ✅ Docker Compose provides PostgreSQL + Redis services
- ✅ Environment variable configuration with backwards compatibility
- ❌ Shell scripts for basic operations (run.sh, changelog.sh) → Need Makefile
- ❌ No standardized make commands → Need `make test`, `make dev`, etc.
- ✅ GitHub Actions CI exists (basic flake8 linting)
- ✅ Dual frontend architecture documented

**Next Steps:**
- [x] Replace pip/requirements.txt with UV for faster Python dependency management
- [x] Create Docker Compose environment for PostgreSQL and services
- [ ] Add Makefile that leverages UV and Docker Compose for streamlined commands

### Task 2.1 - Testing Foundation
**Status: ⏳ WAITING (requires Task 2 completion)**
- [ ] Create comprehensive test suite (unit, integration, API tests) using UV and Docker

### Task 2.2 - Testing Infrastructure
**Status: ⏳ WAITING (requires Task 2.1)**
- [ ] Add test coverage reporting and CI/CD pipeline setup with UV/Docker integration

### Task 2.3 - VS Code Integration
**Status: ⏳ WAITING (requires Task 2.1)**
- [ ] Setup VS Code Python testing extensions with UV and Docker integration

### Task 2.4 - VS Code Configuration
**Status: ⏳ WAITING (requires Task 2.3)**
- [ ] Configure tests to run on file save using UV environment

### Task 2.5 - Git Integration
**Status: ⏳ WAITING (requires Task 2.1)**
- [ ] Add pre-commit hooks for automated testing using UV

### Task 2.6 - Git Integration Extended
**Status: ⏳ WAITING (requires Task 2.5)**
- [ ] Setup commit-msg hooks for test validation

### Task 2.7 - Code Quality Tools
**Status: ⏳ WAITING (requires Task 2 completion)**
- [ ] Setup linting tools (ruff, black, isort) with UV and VS Code integration

### Task 2.8 - API Documentation
**Status: ⏳ WAITING (requires Task 2.1)**
- [ ] Document and test existing Flask API endpoints

---

## Task 3 - Code Cleanup
**Status: ⏳ BLOCKED (requires ALL Task 2 completion - AFTER TESTS)**

### Task 3.1 - Constants Extraction
**Status: ⏳ BLOCKED (requires Task 2 completion)**
- [ ] Extract hardcoded constants (HTmatchtype, HTmatchrole) to separate config files

### Task 3.2 - Code Refactoring
**Status: ⏳ BLOCKED (requires Task 2 completion)**
- [ ] Refactor routes.py (1976 lines) - split into smaller modules by functionality

### Task 3.3 - Type Safety
**Status: ⏳ BLOCKED (requires Task 2 completion)**
- [ ] Add type hints to Python functions for better maintainability

### Task 3.4 - Configuration Management
**Status: ⏳ BLOCKED (requires Task 2 completion)**
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
