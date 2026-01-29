#!/usr/bin/env python3
"""Test script to check current groups for user 182085"""

import importlib.util
import sys
from pathlib import Path

import psycopg2

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import config

spec = importlib.util.spec_from_file_location("config", project_root / "config.py")
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)

# Get database URL
config_obj = config_module.Config()
url = config_obj.SQLALCHEMY_DATABASE_URI

# Parse URL
url = url.replace('postgresql://', '')
credentials, host_part = url.split('@', 1)
user, password = credentials.split(':', 1)
host_port, database = host_part.rsplit('/', 1)
host, port = host_port.rsplit(':', 1)

# Connect and query
conn = psycopg2.connect(
    host=host,
    port=int(port),
    database=database,
    user=user,
    password=password
)

cur = conn.cursor()

# Check groups for user 182085
cur.execute('SELECT COUNT(*) FROM playergroup WHERE user_id = %s', (182085,))
count = cur.fetchone()[0]
print(f'Groups for user 182085: {count}')

if count > 0:
    cur.execute('SELECT name, "order", bgcolor, textcolor FROM playergroup WHERE user_id = %s ORDER BY "order"', (182085,))
    groups = cur.fetchall()
    print('Groups:')
    for name, order, bgcolor, textcolor in groups:
        print(f'  - {name} (order {order}, bg: {bgcolor}, text: {textcolor})')
else:
    print('No groups found!')

# Test the create_default_groups function
print("\nTesting create_default_groups function:")
try:
    sys.path.insert(0, str(project_root / "app"))
    from utils import create_default_groups

    # Check if function exists and can be imported
    print("✅ create_default_groups function imported successfully")

    # Try creating groups for user 182085
    print("Creating default groups...")
    result = create_default_groups(182085)

    if result:
        print(f"✅ Created {len(result)} groups")
        for group in result:
            print(f"  - {group.name} (order {group.order})")
    else:
        print("❌ Function returned None or empty")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

conn.close()
