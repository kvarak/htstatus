#!/usr/bin/env python3
"""
Test if POST method fixes the player() endpoint 401 error.

This test verifies that the player() endpoint now works with POST instead of GET.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import Config


def test_post_method():
    """Test if player() endpoint works with POST."""
    print("\n" + "="*70)
    print("Testing player() endpoint with POST method")
    print("="*70)

    cfg = Config()

    # Get OAuth tokens from environment
    access_key = os.environ.get("CHPP_ACCESS_KEY")
    access_secret = os.environ.get("CHPP_ACCESS_SECRET")

    if not access_key or not access_secret:
        print("\n❌ OAuth tokens not found in environment")
        print("\nTo test the fix, set:")
        print("  export CHPP_ACCESS_KEY='your_key'")
        print("  export CHPP_ACCESS_SECRET='your_secret'")
        return False

    print("\n✓ Found OAuth tokens")

    # Test with custom CHPP
    try:
        from app.chpp import CHPP as CustomCHPP

        custom_client = CustomCHPP(
            cfg.CONSUMER_KEY,
            cfg.CONSUMER_SECRETS,
            access_key,
            access_secret,
        )

        # Try player endpoint
        player_id = 462840653  # Example player ID
        print(f"\n📥 Calling player({player_id}) with POST method...")
        player = custom_client.player(id_=player_id)

        print(f"✅ SUCCESS! Got player: {player.first_name} {player.last_name}")
        print(f"   Keeper: {player.keeper}, Winger: {player.winger}")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


if __name__ == "__main__":
    success = test_post_method()
    sys.exit(0 if success else 1)
