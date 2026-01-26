#!/usr/bin/env python3
"""
Debug Player Skills from CHPP API

This script fetches player data from the CHPP API and shows exactly what
skill values are returned, helping diagnose the "skills showing as 0" issue.

Usage:
    uv run python scripts/debug_player_skills.py <player_id>

Example:
    uv run python scripts/debug_player_skills.py 480742036
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pychpp import CHPP

from config import Config


def debug_player_skills(player_id: int):
    """Fetch and display player skill data from CHPP API."""

    print(f"\n🔍 Debugging Player Skills for ID: {player_id}")
    print("=" * 70)

    # Load config
    cfg = Config()
    consumer_key = cfg.CONSUMER_KEY
    consumer_secret = cfg.CONSUMER_SECRETS

    # Get OAuth credentials from environment
    # These should be set from a logged-in session
    access_key = os.environ.get("CHPP_ACCESS_KEY")
    access_secret = os.environ.get("CHPP_ACCESS_SECRET")

    if not access_key or not access_secret:
        print("❌ ERROR: CHPP OAuth credentials not found in environment")
        print("\nTo use this script, you need to export your OAuth tokens:")
        print("  1. Login to HTStatus web interface")
        print("  2. Get your access tokens from the Flask session")
        print("  3. Export them:")
        print("     export CHPP_ACCESS_KEY='your_access_key'")
        print("     export CHPP_ACCESS_SECRET='your_access_secret'")
        sys.exit(1)

    print(f"✓ Consumer key: {consumer_key[:15]}...")
    print(f"✓ Access key: {access_key[:15]}...")

    try:
        # Initialize CHPP client
        chpp = CHPP(consumer_key, consumer_secret, access_key, access_secret)
        print("\n✓ CHPP client initialized")

        # Fetch player details
        print(f"\n📥 Fetching player {player_id}...")
        player = chpp.player(id_=player_id)

        print("\n" + "=" * 70)
        print("PLAYER DETAILS")
        print("=" * 70)
        print(f"Name: {player.first_name} {player.last_name}")
        print(f"ID: {player.id}")
        print(f"Age: {player.age}")
        print(f"TSI: {player.tsi}")
        print(f"Form: {player.form}")
        print(f"Loyalty: {player.loyalty}")
        print(f"Experience: {player.experience}")

        print("\n" + "=" * 70)
        print("SKILLS OBJECT")
        print("=" * 70)
        print(f"Skills object type: {type(player.skills)}")
        print(f"Skills object repr: {player.skills}")

        print("\n" + "=" * 70)
        print("INDIVIDUAL SKILL VALUES")
        print("=" * 70)
        print(
            f"Stamina:     {player.skills.stamina} (type: {type(player.skills.stamina)})"
        )
        print(
            f"Keeper:      {player.skills.keeper} (type: {type(player.skills.keeper)})"
        )
        print(
            f"Defender:    {player.skills.defender} (type: {type(player.skills.defender)})"
        )
        print(
            f"Playmaker:   {player.skills.playmaker} (type: {type(player.skills.playmaker)})"
        )
        print(
            f"Winger:      {player.skills.winger} (type: {type(player.skills.winger)})"
        )
        print(
            f"Passing:     {player.skills.passing} (type: {type(player.skills.passing)})"
        )
        print(
            f"Scorer:      {player.skills.scorer} (type: {type(player.skills.scorer)})"
        )
        print(
            f"Set Pieces:  {player.skills.set_pieces} (type: {type(player.skills.set_pieces)})"
        )

        # Check if all skills are None
        skills_none = all(
            [
                player.skills.keeper is None,
                player.skills.defender is None,
                player.skills.playmaker is None,
                player.skills.winger is None,
                player.skills.passing is None,
                player.skills.scorer is None,
                player.skills.set_pieces is None,
            ]
        )

        print("\n" + "=" * 70)
        print("ANALYSIS")
        print("=" * 70)
        if skills_none:
            print("❌ ALL SKILLS ARE None!")
            print("\nThis indicates one of:")
            print("  1. CHPP API is not returning skill data in the XML")
            print("  2. pychpp 0.5.10 is not parsing the skill fields correctly")
            print("  3. Player skills are hidden due to privacy settings")
            print("\n💡 NEXT STEPS:")
            print("  - Check the raw XML response from CHPP API")
            print("  - Verify pychpp version and field mappings")
            print("  - Try with a different player")
        else:
            print("✅ Some or all skills have values")
            skill_values = {
                "keeper": player.skills.keeper,
                "defender": player.skills.defender,
                "playmaker": player.skills.playmaker,
                "winger": player.skills.winger,
                "passing": player.skills.passing,
                "scorer": player.skills.scorer,
                "set_pieces": player.skills.set_pieces,
            }

            none_skills = [k for k, v in skill_values.items() if v is None]
            valued_skills = [
                f"{k}={v}" for k, v in skill_values.items() if v is not None
            ]

            if none_skills:
                print(f"\nSkills with None: {', '.join(none_skills)}")
            if valued_skills:
                print(f"\nSkills with values: {', '.join(valued_skills)}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        print(f"\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/debug_player_skills.py <player_id>")
        print("\nExample:")
        print("  uv run python scripts/debug_player_skills.py 480742036")
        print("\nNote: You must have CHPP_ACCESS_KEY and CHPP_ACCESS_SECRET")
        print("      environment variables set from your logged-in session.")
        sys.exit(1)

    try:
        player_id = int(sys.argv[1])
        debug_player_skills(player_id)
    except ValueError:
        print(f"❌ ERROR: Invalid player ID '{sys.argv[1]}' - must be a number")
        sys.exit(1)
