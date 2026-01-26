#!/usr/bin/env python3
"""
CHPP XML Sample Capture Script

Captures real XML responses from CHPP API for testing custom client.
This script must be run after logging in to the application to have valid session tokens.

Usage:
    1. Start the application: make dev
    2. Login through web interface
    3. In Python console or script, call this with session tokens:
       capture_xml_samples(consumer_key, consumer_secret, access_key, access_secret, team_id)

Or run interactively:
    uv run python -c "from scripts.capture_chpp_xml import capture_interactive; capture_interactive()"
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def capture_xml_samples(consumer_key, consumer_secret, access_key, access_secret, team_id=None):
    """
    Capture XML samples from CHPP API.

    Args:
        consumer_key: Application consumer key
        consumer_secret: Application consumer secret
        access_key: User access key (from session)
        access_secret: User access secret (from session)
        team_id: Optional team ID for team-specific requests
    """
    try:
        from pychpp import CHPP

        print("🔍 Capturing CHPP XML Samples...")
        print("=" * 50)

        # Initialize CHPP client
        chpp = CHPP(consumer_key, consumer_secret, access_key, access_secret)
        print("✓ CHPP client initialized")

        # Create output directory
        output_dir = Path(__file__).parent.parent / "app" / "chpp" / "test_data"
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Output directory: {output_dir}")

        # 1. Capture managercompendium (user + teams)
        print("\n📥 Fetching managercompendium...")
        try:
            root = chpp.request(file="managercompendium", version="1.6")
            xml_str = ET.tostring(root, encoding='unicode', method='xml')

            # Pretty print
            from xml.dom import minidom
            dom = minidom.parseString(xml_str)
            pretty_xml = dom.toprettyxml(indent="  ")

            output_file = output_dir / "managercompendium.xml"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)

            print(f"✓ Saved: {output_file}")

            # Extract team ID if not provided
            if not team_id:
                team_nodes = root.findall(".//Team/TeamId")
                if team_nodes:
                    team_id = int(team_nodes[0].text)
                    print(f"✓ Detected team ID: {team_id}")

            # Check YouthTeamId presence
            youth_team = root.find(".//Manager/YouthTeamId")
            if youth_team is not None and youth_team.text:
                print(f"ℹ️  User has YouthTeamId: {youth_team.text}")
            else:
                print("ℹ️  User has NO YouthTeamId (testing our fix)")

        except Exception as e:
            print(f"❌ Error fetching managercompendium: {e}")
            import traceback
            print(traceback.format_exc())

        # 2. Capture teamdetails
        if team_id:
            print(f"\n📥 Fetching teamdetails for team {team_id}...")
            try:
                # Get team object (this triggers teamdetails endpoint)
                team = chpp.team(ht_id=team_id)

                # Access the underlying XML by making raw request
                # pychpp caches this, so we need to request directly
                root = chpp.request(file="teamdetails", version="3.5", teamID=team_id)
                xml_str = ET.tostring(root, encoding='unicode', method='xml')

                from xml.dom import minidom
                dom = minidom.parseString(xml_str)
                pretty_xml = dom.toprettyxml(indent="  ")

                output_file = output_dir / "teamdetails.xml"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(pretty_xml)

                print(f"✓ Saved: {output_file}")
                print(f"ℹ️  Team name: {team.name if hasattr(team, 'name') else 'N/A'}")

            except Exception as e:
                print(f"❌ Error fetching teamdetails: {e}")
                import traceback
                print(traceback.format_exc())

        # 3. Capture players
        if team_id:
            print(f"\n📥 Fetching players for team {team_id}...")
            try:
                # Request players endpoint
                root = chpp.request(file="players", version="2.5", teamID=team_id)
                xml_str = ET.tostring(root, encoding='unicode', method='xml')

                from xml.dom import minidom
                dom = minidom.parseString(xml_str)
                pretty_xml = dom.toprettyxml(indent="  ")

                output_file = output_dir / "players.xml"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(pretty_xml)

                print(f"✓ Saved: {output_file}")

                # Count players
                player_nodes = root.findall(".//Player")
                print(f"ℹ️  Found {len(player_nodes)} players")

            except Exception as e:
                print(f"❌ Error fetching players: {e}")
                import traceback
                print(traceback.format_exc())

        # 4. Note about match endpoint (TBD)
        print("\n📋 Match endpoint TBD:")
        print("   Need to identify which match endpoint is used by matches.py")
        print("   Candidates: matches_archive, match_details, match_lineup")

        print("\n" + "=" * 50)
        print("✅ XML capture complete!")
        print(f"📁 Samples saved to: {output_dir}")
        print("\nNext steps:")
        print("1. Review captured XML files")
        print("2. Identify match endpoint from matches.py")
        print("3. Proceed with REFACTOR-016 (Design phase)")

        return True

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def capture_interactive():
    """
    Interactive mode - prompts for credentials.
    WARNING: Only use for local testing, never commit credentials!
    """
    print("CHPP XML Sample Capture - Interactive Mode")
    print("=" * 50)
    print("⚠️  WARNING: Never commit credentials to git!")
    print()

    try:
        from config import Config
        cfg = Config()

        print("Using credentials from config.py...")
        consumer_key = cfg.CONSUMER_KEY
        consumer_secret = cfg.CONSUMER_SECRETS

        print("\nYou need OAuth access tokens from an active session.")
        print("To get these:")
        print("1. Run 'make dev'")
        print("2. Login through web interface")
        print("3. Check Flask session or logs for access_key and access_secret")
        print()

        access_key = input("Enter access_key (from session): ").strip()
        access_secret = input("Enter access_secret (from session): ").strip()
        team_id_input = input("Enter team ID (optional, press Enter to auto-detect): ").strip()

        team_id = int(team_id_input) if team_id_input else None

        if not access_key or not access_secret:
            print("❌ Access tokens required!")
            return False

        return capture_xml_samples(
            consumer_key, consumer_secret,
            access_key, access_secret,
            team_id
        )

    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    print("To capture XML samples:")
    print("1. Ensure you're logged into the application")
    print("2. Get access_key and access_secret from Flask session")
    print("3. Call capture_xml_samples() with your credentials")
    print()
    print("For interactive mode (prompts for tokens):")
    print("  uv run python scripts/capture_chpp_xml.py")
    print()

    # Only run interactive if called directly
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        capture_interactive()
    else:
        print("Run with --interactive flag to enter interactive mode")
        print("Or import and call capture_xml_samples() directly")
