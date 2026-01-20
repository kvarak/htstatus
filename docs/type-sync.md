# Type Synchronization Documentation

## Overview

The HTStatus project uses a dual architecture with Python (SQLAlchemy) models and TypeScript interfaces. To maintain consistency and prevent type drift between these systems, we use automated type validation.

## Type Sync Validation

### Script: `scripts/validate_types.py`

Validates that TypeScript interfaces in `src/types/index.ts` match SQLAlchemy models in `models.py`.

**Checks performed:**
- Field presence (all model fields have corresponding interface fields)
- Type compatibility (SQLAlchemy types map correctly to TypeScript types)
- Nullability consistency (nullable database fields vs optional TypeScript properties)
- Missing fields detection (fields in interface but not in model)

### Usage

```bash
# Manual validation
make typesync

# As part of quality gates
make test-all
```

### Type Mappings

| SQLAlchemy Type | TypeScript Type |
|----------------|-----------------|
| Integer        | number          |
| String         | string          |
| Boolean        | boolean         |
| DateTime       | Date            |
| Float          | number          |
| PickleType     | any             |

### Common Issues

**Nullability Mismatches:**
- SQLAlchemy fields are nullable by default unless `nullable=False` is specified
- TypeScript fields are required unless marked with `?` (optional)
- Fix: Add `?` to optional TypeScript fields or add `nullable=False` to SQLAlchemy columns

**Type Mismatches:**
- Ensure TypeScript types match the mapped SQLAlchemy types
- Example: `PickleType` should map to `any`, not specific types like `string[]`

**Missing Fields:**
- Add missing fields to TypeScript interfaces
- Or add missing columns to SQLAlchemy models if needed

## Maintenance Procedures

### Adding New Model Fields

1. Add field to SQLAlchemy model in `models.py`
2. Add corresponding field to TypeScript interface in `src/types/index.ts`
3. Run `make typesync` to validate synchronization
4. Update tests and documentation as needed

### Changing Field Types

1. Update type in both SQLAlchemy model and TypeScript interface
2. Ensure type mapping is correct (see table above)
3. Run `make typesync` to validate
4. Create database migration if needed
5. Update related code and tests

### CI Integration

Type sync validation is integrated into the quality gate pipeline:
- **Position**: Step 4/6 in `make test-all`
- **Exit behavior**: Pipeline continues on failure (warning only)
- **Reporting**: Clear summary in quality gate results

## Current Status

As of initial implementation, there are 85 type sync issues, primarily:
- 83 nullability mismatches (SQLAlchemy nullable vs TypeScript required)
- 2 type/field mismatches (User.password missing, User.player_columns type)

These represent existing design decisions and can be addressed incrementally without breaking changes.