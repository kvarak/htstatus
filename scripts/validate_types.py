#!/usr/bin/env python3
"""
Type Sync Validation Script

Validates that TypeScript interfaces in src/types/index.ts match
SQLAlchemy models in models.py to prevent type drift.
"""

import re
import sys
from pathlib import Path
from typing import Any

# Type mapping between SQLAlchemy and TypeScript
TYPE_MAPPING = {
    # SQLAlchemy -> TypeScript
    'Integer': 'number',
    'String': 'string',
    'String()': 'string',
    'Boolean': 'boolean',
    'DateTime': 'Date',
    'Float': 'number',
    'PickleType': 'any',  # player_columns is serialized data
}

def extract_model_fields(models_path: Path) -> dict[str, dict[str, Any]]:
    """Extract field definitions from SQLAlchemy models."""
    models = {}

    with open(models_path) as f:
        content = f.read()

    # Find class definitions
    class_pattern = r'class\s+(\w+)\(db\.Model\):(.*?)(?=class\s+\w+\(db\.Model\)|$)'
    matches = re.findall(class_pattern, content, re.DOTALL)

    for class_name, class_content in matches:
        # Skip abstract classes and focus on main models
        if class_name in ['MatchPlay', 'Match', 'User', 'Players', 'Group', 'PlayerSetting']:
            fields = {}

            # Extract db.Column definitions
            column_pattern = r'(\w+)\s*=\s*db\.Column\(([^)]+)\)'
            column_matches = re.findall(column_pattern, class_content)

            for field_name, column_def in column_matches:
                # Extract column type
                type_match = re.match(r'db\.(\w+)(?:\([^)]*\))?', column_def.strip())
                if type_match:
                    sql_type = type_match.group(1)

                    # Check for nullable/optional
                    is_nullable = 'nullable=False' not in column_def
                    is_primary_key = 'primary_key=True' in column_def

                    fields[field_name] = {
                        'type': sql_type,
                        'nullable': is_nullable and not is_primary_key,
                        'primary_key': is_primary_key
                    }

            # Map class name to TypeScript interface name
            ts_name = class_name
            if class_name == 'Players':
                ts_name = 'Player'
            elif class_name == 'Group':
                ts_name = 'PlayerGroup'

            models[ts_name] = fields

    return models

def extract_typescript_interfaces(types_path: Path) -> dict[str, dict[str, Any]]:
    """Extract interface definitions from TypeScript file."""
    interfaces = {}

    with open(types_path) as f:
        content = f.read()

    # Find interface definitions
    interface_pattern = r'export interface\s+(\w+)\s*\{([^}]+)\}'
    matches = re.findall(interface_pattern, content, re.DOTALL)

    for interface_name, interface_content in matches:
        # Skip UI-only interfaces
        if interface_name in ['User', 'Player', 'Match', 'MatchPlay', 'PlayerGroup', 'PlayerSetting']:
            fields = {}

            # Extract field definitions
            field_pattern = r'(\w+)(\?)?\s*:\s*([^;]+);'
            field_matches = re.findall(field_pattern, interface_content)

            for field_name, optional_marker, field_type in field_matches:
                is_optional = bool(optional_marker)
                field_type = field_type.strip()

                fields[field_name] = {
                    'type': field_type,
                    'optional': is_optional
                }

            interfaces[interface_name] = fields

    return interfaces

def validate_type_sync(models: dict[str, dict[str, Any]],
                      interfaces: dict[str, dict[str, Any]]) -> list[str]:
    """Validate that TypeScript interfaces match SQLAlchemy models."""
    errors = []

    for model_name in models:
        if model_name not in interfaces:
            errors.append(f"❌ Missing TypeScript interface: {model_name}")
            continue

        model_fields = models[model_name]
        interface_fields = interfaces[model_name]

        # Check each model field has corresponding interface field
        for field_name, field_info in model_fields.items():
            if field_name not in interface_fields:
                errors.append(f"❌ {model_name}.{field_name}: Missing in TypeScript interface")
                continue

            # Check type compatibility
            sql_type = field_info['type']
            ts_field = interface_fields[field_name]
            ts_type = ts_field['type']

            # Map SQLAlchemy type to expected TypeScript type
            expected_ts_type = TYPE_MAPPING.get(sql_type, sql_type)

            if ts_type != expected_ts_type:
                errors.append(f"❌ {model_name}.{field_name}: Type mismatch - SQLAlchemy '{sql_type}' -> expected '{expected_ts_type}', got '{ts_type}'")

            # Check nullable/optional consistency
            is_nullable = field_info.get('nullable', False)
            is_optional = ts_field.get('optional', False)

            if is_nullable != is_optional:
                nullable_str = "nullable" if is_nullable else "required"
                optional_str = "optional" if is_optional else "required"
                errors.append(f"⚠️  {model_name}.{field_name}: Nullability mismatch - SQLAlchemy {nullable_str}, TypeScript {optional_str}")

        # Check for extra TypeScript fields
        for field_name in interface_fields:
            if field_name not in model_fields:
                errors.append(f"⚠️  {model_name}.{field_name}: Extra field in TypeScript interface (not in model)")

    # Check for extra interfaces
    for interface_name in interfaces:
        if interface_name not in models:
            errors.append(f"ℹ️  Extra TypeScript interface: {interface_name} (no corresponding model)")

    return errors

def main():
    """Main validation function."""
    project_root = Path(__file__).parent.parent
    models_path = project_root / "models.py"
    types_path = project_root / "src" / "types" / "index.ts"

    if not models_path.exists():
        print(f"❌ Models file not found: {models_path}")
        sys.exit(1)

    if not types_path.exists():
        print(f"❌ Types file not found: {types_path}")
        sys.exit(1)

    print("🔍 Validating type sync between SQLAlchemy models and TypeScript interfaces...")

    # Extract type definitions
    models = extract_model_fields(models_path)
    interfaces = extract_typescript_interfaces(types_path)

    print(f"📊 Found {len(models)} models and {len(interfaces)} interfaces")

    # Validate synchronization
    errors = validate_type_sync(models, interfaces)

    if not errors:
        print("✅ Type sync validation passed - no mismatches found!")
        return 0
    else:
        print(f"\n❌ Found {len(errors)} type sync issues:")
        for error in errors:
            print(f"   {error}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
