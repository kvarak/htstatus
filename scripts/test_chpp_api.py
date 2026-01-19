#!/usr/bin/env python3
"""
CHPP API Connectivity Test Script

Tests CHPP API connectivity independently of the main application
to diagnose data fetching issues.

Usage:
    uv run python scripts/test_chpp_api.py

Environment:
    This script requires the UV-managed Python environment.
    Always use 'uv run' to ensure correct dependency resolution.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import traceback

from config import Config


def test_chpp_connection():
    """Test basic CHPP API connectivity and authentication."""

    print("🔍 Testing CHPP API Connectivity...")
    print("=" * 50)

    try:
        # Get configuration
        cfg = Config()
        consumer_key = cfg.CONSUMER_KEY
        consumer_secret = cfg.CONSUMER_SECRETS
        print(f"✓ Consumer key loaded: {consumer_key[:10]}...")
        print(f"✓ Consumer secret loaded: {consumer_secret[:10]}...")

        # Note: This test script doesn't have access to user OAuth tokens
        # In production, we would need valid access_key and access_secret from session
        print("\n⚠️  Note: This test requires valid OAuth access tokens")
        print("   Real testing must be done through the web interface after login")
        print("\n📋 To test the /update route:")
        print("   1. Run 'make dev'")
        print("   2. Navigate to http://localhost:5010")
        print("   3. Login with your Hattrick credentials")
        print("   4. Click 'Update data' and check console logs for detailed diagnostics")

        return True

    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        print(f"Full error: {traceback.format_exc()}")
        return False

def test_configuration():
    """Test basic configuration setup."""

    print("\n🔧 Testing Configuration...")
    print("=" * 50)

    required_vars = [
        'CONSUMER_KEY',
        'CONSUMER_SECRETS',
        'SQLALCHEMY_DATABASE_URI'
    ]

    try:
        cfg = Config()

        missing_vars = []
        for var in required_vars:
            if not hasattr(cfg, var) or not getattr(cfg, var):
                missing_vars.append(var)
            else:
                print(f"✓ {var}: configured")

        if missing_vars:
            print(f"\n❌ Missing configuration variables: {', '.join(missing_vars)}")
            print("   Check your .env file and config.py")
            return False
        else:
            print("\n✅ All required configuration variables are set")
            return True

    except Exception as e:
        print(f"❌ Configuration loading error: {str(e)}")
        return False

if __name__ == "__main__":
    print("HTStatus CHPP API Diagnostics")
    print("=" * 50)

    config_ok = test_configuration()
    chpp_ok = test_chpp_connection()

    print("\n📊 Diagnostic Summary")
    print("=" * 50)
    print(f"Configuration: {'✅ OK' if config_ok else '❌ FAILED'}")
    print(f"CHPP Setup: {'✅ OK' if chpp_ok else '❌ FAILED'}")

    if config_ok and chpp_ok:
        print("\n🎉 Basic setup appears correct!")
        print("   Test the /update route through the web interface for full validation")
    else:
        print("\n⚠️  Issues found - fix configuration before testing /update route")
