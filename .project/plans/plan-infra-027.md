# Plan: INFRA-027 Feature Flag Configuration Documentation

## Executive Summary

Create comprehensive documentation for the `USE_CUSTOM_CHPP` feature flag to enable safe deployment and management of the custom CHPP client in production. This is a 30-minute documentation task supporting the P3 Stability milestone.

## Analysis

### Current State
- **Feature Flag**: `USE_CUSTOM_CHPP` environment variable implemented and working (INFRA-025 complete)
- **Default Behavior**: Uses pychpp 0.5.10 (production stable)
- **Custom CHPP**: Code complete (INFRA-026), OAuth blocking production validation
- **Documentation Gap**: No `.env` examples or deployment guides for the feature flag

### Problem Statement
Operators and developers deploying HTStatus lack clear documentation on:
1. How to enable/disable the custom CHPP client
2. Where to configure the feature flag (.env, Docker, CI/CD)
3. When to use custom vs pychpp (decision criteria)
4. How to roll back if issues occur (instant, no restart needed)
5. What behavior changes when toggling the flag

### Impact
- Production deployment teams need clear instructions
- New developers need onboarding on CHPP configuration
- Docker/staging environments need examples
- Troubleshooting guides for feature flag issues

### Strategic Value (P3 Alignment)
- **Stability Focus**: Enables safe production experimentation with custom CHPP
- **Maintainability**: Clear documentation reduces support burden
- **Simplification**: Single place to reference instead of scattered comments
- **Process**: Establishes pattern for future feature flags

## Solution

### Deliverables

**1. Environment Configuration Examples** (10 min)
- Update `.env.example` with `USE_CUSTOM_CHPP` entry
- Add inline comments explaining the flag and options
- Include docker-compose environment variable examples
- Add CI/CD pipeline variable examples (if GitHub Actions configured)

**2. Feature Flag Deployment Guide** (15 min)
- Create section in DEPLOYMENT.md or new FEATURE_FLAGS.md
- Cover:
  - How to enable/disable the flag
  - Environment-specific recommendations (dev, staging, production)
  - Decision criteria for when to use custom CHPP
  - Rollback procedures (instant toggle, no restart needed)
  - Troubleshooting common issues
  - Monitoring/logging what flag is active

**3. Code Comments Update** (5 min)
- Reference new documentation in relevant code locations
- Add links from factory.py `_display_startup_status()` function
- Update TECHNICAL.md to reference deployment guide

## Implementation Steps

### Step 1: Update .env.example
```bash
# Location: .env.example (create if missing, or update existing)
# Add CHPP client configuration section with:
# - USE_CUSTOM_CHPP=false (default, safe production setting)
# - Comment explaining custom vs pychpp
# - Link to DEPLOYMENT.md or FEATURE_FLAGS.md
```

### Step 2: Create/Update Deployment Guide
Choose one approach:
- **Option A**: Add section to existing DEPLOYMENT.md
- **Option B**: Create new FEATURE_FLAGS.md for comprehensive flag management

Content:
1. **Feature Flag Overview**
   - Name: `USE_CUSTOM_CHPP`
   - Type: Boolean environment variable
   - Default: `false` (pychpp 0.5.10)
   - Scope: Application-wide (affects all CHPP API calls)

2. **Configuration Methods**
   - Local development: Add to `.env` file
   - Docker: Set in docker-compose.yml environment section
   - Kubernetes: Set in deployment manifests
   - CI/CD: Set in GitHub Actions secrets/variables

3. **Use Cases**
   - **Production**: Keep default (false) until custom CHPP fully validated
   - **Staging**: Can test custom CHPP with `true`
   - **Development**: Can toggle for testing both paths
   - **Testing**: Keep default in automated tests (mocked API)

4. **Rollback Procedures**
   - Change environment variable: `USE_CUSTOM_CHPP=false`
   - No application restart required
   - Next request will use pychpp
   - Instant rollback with zero downtime

5. **Monitoring/Logging**
   - Startup status displayed: "✅ Using Custom CHPP Client" or "✅ Using pychpp Client"
   - Check logs when troubleshooting API issues
   - Verify correct client is active before production deployments

### Step 3: Update Related Documentation
- Link from factory.py `_display_startup_status()` function documentation
- Update TECHNICAL.md section on CHPP integration
- Add reference in README.md deployment section

### Step 4: Code Comments
- Add comment in `app/chpp_utils.py` linking to deployment guide
- Update `app/factory.py` startup function with reference

## Testing

### Documentation Validation
- [ ] All examples are accurate (tested locally if code examples)
- [ ] Links to deployment guide work and are clear
- [ ] A new team member can follow guide to enable custom CHPP
- [ ] Rollback procedure is explicitly documented
- [ ] All configuration methods covered (local, Docker, CI/CD)

### Quality Checks
- [ ] No broken links in documentation
- [ ] Code examples match actual implementation
- [ ] Linting passes on any new markdown files
- [ ] Documentation uses consistent terminology

## Acceptance Criteria

- ✅ `.env.example` includes `USE_CUSTOM_CHPP` configuration with explanatory comments
- ✅ Deployment guide created (either DEPLOYMENT.md section or separate FEATURE_FLAGS.md)
- ✅ Guide covers all configuration methods (local, Docker, CI/CD)
- ✅ Rollback procedures documented (instant toggle, no restart)
- ✅ Decision criteria for custom vs pychpp client clear
- ✅ References added to factory.py and TECHNICAL.md
- ✅ Documentation is clear enough for new developers/operators

## Dependencies & Blockers

**No blockers** - Pure documentation task

**Related**:
- INFRA-025: Feature flag implementation (completed)
- INFRA-026: Custom CHPP code implementation (blocked on BUG-013)
- BUG-013: OAuth debugging (separate track, not blocking this task)

## Effort Estimation

- Environment configuration: 10 min
- Deployment guide creation: 15 min
- Code comments and links: 5 min
- **Total: 30 minutes**

## Discovery Notes

### Potential Future Tasks
1. **INFRA-028**: Deployment automation (GitHub Actions secrets configuration)
2. **DOC-031**: CHPP Client Migration Runbook (when ready to switch to custom in production)
3. **MONITORING-001**: Feature flag usage metrics/alerting (advanced monitoring)

### Related Simplifications
- Feature flag pattern can be reused for other optional features
- Could consolidate into feature_flags.py module if more flags added later
- Consider env config validation on startup (INFRA-029)

## References

- **Implementation**: app/chpp_utils.py, app/factory.py, app/blueprints/*.py
- **Related**: DEPLOYMENT.md (existing), TECHNICAL.md, .env.example
- **Project**: See .project/backlog.md for related tasks
