"""Tests for app.chpp.parsers module.

Tests XML parsing functions for CHPP API responses.
"""

import xml.etree.ElementTree as ET

from app.chpp.models import CHPPPlayer, CHPPTeam, CHPPUser
from app.chpp.parsers import (
    parse_players,
    parse_team,
    parse_user,
    safe_find_bool,
    safe_find_int,
    safe_find_text,
)


class TestSafeHelperFunctions:
    """Tests for safe XML extraction helper functions."""

    def test_safe_find_text_found(self):
        """Test safe_find_text with existing element."""
        xml = "<root><test>value</test></root>"
        root = ET.fromstring(xml)

        result = safe_find_text(root, ".//test")
        assert result == "value"

    def test_safe_find_text_not_found(self):
        """Test safe_find_text with missing element."""
        xml = "<root><other>value</other></root>"
        root = ET.fromstring(xml)

        result = safe_find_text(root, ".//test", default="missing")
        assert result == "missing"

    def test_safe_find_text_empty_element(self):
        """Test safe_find_text with empty element."""
        xml = "<root><test></test></root>"
        root = ET.fromstring(xml)

        result = safe_find_text(root, ".//test", default="empty")
        assert result == "empty"

    def test_safe_find_int_valid(self):
        """Test safe_find_int with valid integer."""
        xml = "<root><number>123</number></root>"
        root = ET.fromstring(xml)

        result = safe_find_int(root, ".//number")
        assert result == 123

    def test_safe_find_int_invalid(self):
        """Test safe_find_int with invalid integer."""
        xml = "<root><number>not_a_number</number></root>"
        root = ET.fromstring(xml)

        result = safe_find_int(root, ".//number", default=999)
        assert result == 999

    def test_safe_find_int_missing(self):
        """Test safe_find_int with missing element."""
        xml = "<root><other>123</other></root>"
        root = ET.fromstring(xml)

        result = safe_find_int(root, ".//number")
        assert result == 0

    def test_safe_find_bool_true_values(self):
        """Test safe_find_bool with various true values."""
        test_cases = [
            ("<root><flag>True</flag></root>", True),
            ("<root><flag>true</flag></root>", True),
            ("<root><flag>1</flag></root>", True),
            ("<root><flag>yes</flag></root>", True),
        ]

        for xml, expected in test_cases:
            root = ET.fromstring(xml)
            result = safe_find_bool(root, ".//flag")
            assert result == expected

    def test_safe_find_bool_false_values(self):
        """Test safe_find_bool with various false values."""
        test_cases = [
            ("<root><flag>False</flag></root>", False),
            ("<root><flag>false</flag></root>", False),
            ("<root><flag>0</flag></root>", False),
            ("<root><flag>no</flag></root>", False),
        ]

        for xml, expected in test_cases:
            root = ET.fromstring(xml)
            result = safe_find_bool(root, ".//flag")
            assert result == expected

    def test_safe_find_bool_missing(self):
        """Test safe_find_bool with missing element."""
        xml = "<root><other>true</other></root>"
        root = ET.fromstring(xml)

        result = safe_find_bool(root, ".//flag", default=True)
        assert result


class TestParseUser:
    """Tests for parse_user function."""

    def test_parse_user_with_youth_team(self):
        """Test parsing user with YouthTeamId present."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
        <HattrickData>
            <Manager>
                <UserId>123456</UserId>
                <Loginname>testuser</Loginname>
                <Teams>
                    <Team>
                        <TeamId>456789</TeamId>
                        <YouthTeam>
                            <YouthTeamId>789012</YouthTeamId>
                        </YouthTeam>
                    </Team>
                </Teams>
            </Manager>
        </HattrickData>"""

        root = ET.fromstring(xml)
        user = parse_user(root)

        assert isinstance(user, CHPPUser)
        assert user.ht_id == 123456
        assert user.username == "testuser"
        assert 456789 in user._teams_ht_id

    def test_parse_user_without_youth_team(self):
        """Test parsing user without YouthTeamId (YouthTeamId bug fix)."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
        <HattrickData>
            <Manager>
                <UserId>123456</UserId>
                <Loginname>testuser</Loginname>
                <Teams>
                    <Team>
                        <TeamId>456789</TeamId>
                        <!-- No YouthTeam section -->
                    </Team>
                </Teams>
            </Manager>
        </HattrickData>"""

        root = ET.fromstring(xml)
        user = parse_user(root)

        assert isinstance(user, CHPPUser)
        assert user.ht_id == 123456
        assert user.username == "testuser"
        assert 456789 in user._teams_ht_id

    def test_parse_user_multiple_teams(self):
        """Test parsing user with multiple teams."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
        <HattrickData>
            <Manager>
                <UserId>123456</UserId>
                <Loginname>testuser</Loginname>
                <Teams>
                    <Team>
                        <TeamId>456789</TeamId>
                    </Team>
                    <Team>
                        <TeamId>111222</TeamId>
                    </Team>
                </Teams>
            </Manager>
        </HattrickData>"""

        root = ET.fromstring(xml)
        user = parse_user(root)

        assert len(user._teams_ht_id) == 2
        assert 456789 in user._teams_ht_id
        assert 111222 in user._teams_ht_id

    def test_parse_user_missing_fields(self):
        """Test parsing user with missing required fields."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
        <HattrickData>
            <Manager>
                <!-- Missing UserId and LoginName -->
            </Manager>
        </HattrickData>"""

        root = ET.fromstring(xml)
        user = parse_user(root)

        assert user.ht_id == 0  # Default value
        assert user.username == ""  # Default value
        assert len(user._teams_ht_id) == 0


class TestParseTeam:
    """Tests for parse_team function."""

    def test_parse_team_basic(self):
        """Test parsing team with basic information."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
        <HattrickData>
            <Team>
                <TeamID>456789</TeamID>
                <TeamName>Test FC</TeamName>
                <ShortTeamName>Test</ShortTeamName>
            </Team>
        </HattrickData>"""

        root = ET.fromstring(xml)
        team = parse_team(root)

        assert isinstance(team, CHPPTeam)
        assert team.team_id == 456789
        assert team.name == "Test FC"
        assert team.short_team_name == "Test"

    def test_parse_team_missing_fields(self):
        """Test parsing team with missing optional fields."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
        <HattrickData>
            <Team>
                <TeamID>456789</TeamID>
                <!-- Missing TeamName and ShortTeamName -->
            </Team>
        </HattrickData>"""

        root = ET.fromstring(xml)
        team = parse_team(root)

        assert team.team_id == 456789
        assert team.name == ""  # Default value
        assert team.short_team_name == ""  # Default value


class TestParsePlayers:
    """Tests for parse_players function."""

    def test_parse_players_single_player(self):
        """Test parsing single player with all skills."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
        <HattrickData>
            <Team>
                <TeamID>456789</TeamID>
                <PlayerList>
                    <Player>
                        <PlayerID>1001</PlayerID>
                        <FirstName>Test</FirstName>
                        <LastName>Player</LastName>
                        <PlayerNumber>1</PlayerNumber>
                        <Keeper>5</Keeper>
                        <Defender>8</Defender>
                        <Playmaker>6</Playmaker>
                        <Winger>4</Winger>
                        <Passing>7</Passing>
                        <Scorer>3</Scorer>
                        <SetPieces>2</SetPieces>
                        <Experience>4</Experience>
                        <PlayerForm>6</PlayerForm>
                        <Stamina>5</Stamina>
                        <Loyalty>8</Loyalty>
                    </Player>
                </PlayerList>
            </Team>
        </HattrickData>"""

        root = ET.fromstring(xml)
        players = parse_players(root)

        assert len(players) == 1
        player = players[0]

        assert isinstance(player, CHPPPlayer)
        assert player.player_id == 1001
        assert player.first_name == "Test"
        assert player.last_name == "Player"
        assert player.player_number == 1
        assert player.keeper == 5
        assert player.defender == 8
        assert player.playmaker == 6
        assert player.winger == 4
        assert player.passing == 7
        assert player.scorer == 3
        assert player.set_pieces == 2
        assert player.experience == 4
        assert player.form == 6
        assert player.stamina == 5
        assert player.loyalty == 8

    def test_parse_players_multiple_players(self):
        """Test parsing multiple players."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
        <HattrickData>
            <Team>
                <TeamID>456789</TeamID>
                <PlayerList>
                    <Player>
                        <PlayerID>1001</PlayerID>
                        <FirstName>Player</FirstName>
                        <LastName>One</LastName>
                        <Keeper>5</Keeper>
                    </Player>
                    <Player>
                        <PlayerID>1002</PlayerID>
                        <FirstName>Player</FirstName>
                        <LastName>Two</LastName>
                        <Keeper>3</Keeper>
                    </Player>
                </PlayerList>
            </Team>
        </HattrickData>"""

        root = ET.fromstring(xml)
        players = parse_players(root)

        assert len(players) == 2
        assert players[0].player_id == 1001
        assert players[0].first_name == "Player"
        assert players[0].last_name == "One"
        assert players[1].player_id == 1002
        assert players[1].first_name == "Player"
        assert players[1].last_name == "Two"

    def test_parse_players_missing_skills(self):
        """Test parsing player with missing skill values."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
        <HattrickData>
            <Team>
                <TeamID>456789</TeamID>
                <PlayerList>
                    <Player>
                        <PlayerID>1001</PlayerID>
                        <FirstName>Incomplete</FirstName>
                        <LastName>Player</LastName>
                        <!-- Missing most skills -->
                        <Keeper>5</Keeper>
                    </Player>
                </PlayerList>
            </Team>
        </HattrickData>"""

        root = ET.fromstring(xml)
        players = parse_players(root)

        player = players[0]
        assert player.keeper == 5
        assert player.defender == 0  # Default value for missing skills
        assert player.playmaker == 0
        assert player.experience == 0

    def test_parse_players_empty_team(self):
        """Test parsing team with no players."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
        <HattrickData>
            <Team>
                <TeamID>456789</TeamID>
                <!-- No players -->
            </Team>
        </HattrickData>"""

        root = ET.fromstring(xml)
        players = parse_players(root)

        assert len(players) == 0
