#!/usr/bin/env python3
"""
Debug CHPP OAuth Issues

Compares HTTP requests between pychpp and custom CHPP for the player() endpoint
to identify OAuth signature differences.

Usage:
    uv run python scripts/debug_chpp_oauth.py

Note: This requires valid OAuth tokens from a logged-in session.
"""

import logging
import os
import sys

# Configure logging to see debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import Config  # noqa: E402


def main():
    """Debug OAuth requests."""
    print("\n" + "="*70)
    print("CHPP OAuth Debug - Player Endpoint Comparison")
    print("="*70)

    cfg = Config()

    # Get OAuth tokens from environment
    access_key = os.environ.get("CHPP_ACCESS_KEY")
    access_secret = os.environ.get("CHPP_ACCESS_SECRET")

    if not access_key or not access_secret:
        print("\n❌ OAuth tokens not found in environment")
        print("\nTo set them, export from your HTStatus session:")
        print("  export CHPP_ACCESS_KEY='your_key'")
        print("  export CHPP_ACCESS_SECRET='your_secret'")
        sys.exit(1)

    print("\n✓ Found OAuth tokens")
    print(f"  Access Key: {access_key[:20]}...")
    print(f"  Access Secret: {access_secret[:20]}...")

    # Test player ID (replace with a real one)
    player_id = 480742036
    print(f"\n📌 Testing with Player ID: {player_id}")

    print("\n" + "="*70)
    print("Testing pychpp")
    print("="*70)

    try:
        from pychpp import CHPP as PychppCHPP

        pychpp_client = PychppCHPP(
            cfg.CONSUMER_KEY,
            cfg.CONSUMER_SECRETS,
            access_key,
            access_secret,
        )

        print("\n📥 Calling pychpp.player()...")
        player = pychpp_client.player(id_=player_id)
        print(f"✅ SUCCESS: Got player {player.first_name} {player.last_name}")
        print(f"   Skills: Keeper={player.keeper}, Defender={player.defender}")

    except Exception as e:
        print(f"❌ FAILED: {e}")

    print("\n" + "="*70)
    print("Testing Custom CHPP")
    print("="*70)

    try:
        # Import custom CHPP with debug logging
        from app.chpp import CHPP as CustomCHPP

        custom_client = CustomCHPP(
            cfg.CONSUMER_KEY,
            cfg.CONSUMER_SECRETS,
            access_key,
            access_secret,
        )

        print("\n📥 Calling custom CHPP.player()...")
        player = custom_client.player(id_=player_id)
        print(f"✅ SUCCESS: Got player {player.first_name} {player.last_name}")
        print(f"   Skills: Keeper={player.keeper}, Defender={player.defender}")

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70)
    print("Investigation Points")
    print("="*70)
    print("""
If custom CHPP failed with 401:
1. Check if OAuth1Session signature generation is identical
2. Verify playerId parameter name is correct (case-sensitive)
3. Compare HTTP headers between pychpp and custom CHPP
4. Check if there's any parameter encoding difference
5. Verify access token scope includes player endpoint
    """)


if __name__ == "__main__":
    main()
