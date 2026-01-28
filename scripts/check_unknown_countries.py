#!/usr/bin/env python3
"""
HTStatus Unknown Countries Checker

Check for unmapped country IDs in player data for a specific team.
Usage: uv run python scripts/check_unknown_countries.py [team_id]

This script identifies country IDs that are not mapped in our COUNTRIES dictionary,
helping to complete the country mapping for proper flag and color display.
"""

import argparse
import sys
from collections import Counter

# Setup path for app imports
sys.path.append('.')

from app.factory import create_app
from app.hattrick_countries import COUNTRIES
from app.model_registry import get_players_model


def check_unknown_countries(team_id=None):
    """Check for unknown countries in the specified team or all teams."""
    app = create_app()

    with app.app_context():
        Players = get_players_model()

        # Get players for specific team or all players
        if team_id:
            players = Players.query.filter_by(current_team_id=team_id).all()
            print(f"🏆 Team {team_id} Players Analysis:")
        else:
            players = Players.query.all()
            print("🌍 Global Players Analysis:")

        print(f"Total players: {len(players)}")
        print()

        # Collect all country IDs
        country_ids = [player.native_country_id for player in players if player.native_country_id is not None]
        country_counter = Counter(country_ids)

        # Find unknown countries
        unknown_countries = [cid for cid in country_ids if cid not in COUNTRIES]

        if unknown_countries:
            print("🚨 Unknown Countries Found:")
            unique_unknown = set(unknown_countries)
            for country_id in sorted(unique_unknown):
                count = country_counter[country_id]
                print(f"  Country ID {country_id}: {count} players - NEEDS MAPPING")

            print("\n📝 Countries to Add to COUNTRIES Dictionary:")
            print("Copy these entries to app/hattrick_countries.py:")
            print()
            for country_id in sorted(unique_unknown):
                print(f"    {country_id}: {{")
                print(f"        'name': 'UNKNOWN_COUNTRY_{country_id}',")
                print("        'flag': '❓',")
                print("        'color': '#CCCCCC'")
                print("    },")
        else:
            print("✅ All countries are properly mapped!")

        print("\nℹ️  Summary:")
        mapped_count = len([cid for cid in country_ids if cid in COUNTRIES])
        print(f"  Mapped countries: {mapped_count}")
        print(f"  Unknown countries: {len(unknown_countries)}")
        print(f"  Total country entries: {len(country_ids)}")
        print(f"  Unique countries: {len(set(country_ids))}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check for unknown countries in player data")
    parser.add_argument("team_id", type=int, nargs="?", help="Team ID to check (optional, checks all teams if omitted)")

    args = parser.parse_args()
    check_unknown_countries(args.team_id)
