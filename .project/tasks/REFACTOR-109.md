# REFACTOR-109: Remove Test Stub Waste and TODO Overhead

**Status**: 🎯 Ready to Execute | **Effort**: 2-3 hours | **Priority**: P3 | **Impact**: Cognitive load reduction
**Dependencies**: None | **Strategic Value**: Clean test suite without false signals

## Problem Statement
Multiple test files contain only TODO comments without actual implementations, creating maintenance overhead and false coverage signals:
- test_hattrick_countries.py: 5 TODO items, no actual tests
- test_client.py: 6 TODO items, no implementation
- Various test stubs that provide no validation value

This creates cognitive load when navigating tests and suggests coverage that doesn't exist.

## Implementation

### Phase 1: TODO Audit and Removal (1 hour)
- Identify all test files with only TODO comments
- Remove test files that contain no actual test implementation
- Document removed test areas in .project/backlog.md for future consideration
- Update test discovery patterns if needed

### Phase 2: Test Coverage Reality Check (1 hour)
- Run coverage analysis to identify actual vs suggested test coverage
- Remove stub test classes that provide no validation
- Consolidate remaining TODO items into single tracking location
- Update test suite documentation to reflect actual coverage

### Phase 3: Clean Test Structure (1 hour)
- Ensure remaining test files have meaningful implementations
- Remove empty test classes and placeholder methods
- Apply consistent naming patterns to remaining tests
- Verify all remaining tests contribute to actual validation

## Acceptance Criteria
- [ ] No test files containing only TODO comments remain
- [ ] Test coverage reports reflect actual validation, not stubs
- [ ] Remaining TODO items consolidated in single tracking location
- [ ] All test files contain meaningful implementations
- [ ] Test suite provides clear signal vs noise ratio
- [ ] No broken test discovery after cleanup

## Strategic Value
Eliminates false signals in test coverage and reduces cognitive overhead when working with the test suite.
