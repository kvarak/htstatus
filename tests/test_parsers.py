"""Tests for app/chpp/parsers.py"""

import xml.etree.ElementTree as ET

from app.chpp.models import CHPPMatch, CHPPPlayer, CHPPTeam, CHPPUser
from app.chpp.parsers import (
    parse_matches,
    parse_player,
    parse_players,
    parse_team,
    parse_user,
    safe_find_bool,
    safe_find_int,
    safe_find_text,
)


def test_module_imports():
    """Test that CHPP parsers module imports without errors."""
    import app.chpp.parsers
    assert app.chpp.parsers is not None


class TestSafeFindText:
    """Test safe_find_text utility function."""

    def test_finds_existing_element(self):
        """Test finding an element that exists with text."""
        xml = "<root><item>test_value</item></root>"
        root = ET.fromstring(xml)
        result = safe_find_text(root, "item")
        assert result == "test_value"

    def test_returns_default_for_missing_element(self):
        """Test default value when element doesn't exist."""
        xml = "<root></root>"
        root = ET.fromstring(xml)
        result = safe_find_text(root, "missing", "default")
        assert result == "default"

    def test_returns_none_default_when_not_specified(self):
        """Test None default when no default specified."""
        xml = "<root></root>"
        root = ET.fromstring(xml)
        result = safe_find_text(root, "missing")
        assert result is None

    def test_returns_default_for_empty_text(self):
        """Test default value when element exists but is empty."""
        xml = "<root><item></item></root>"
        root = ET.fromstring(xml)
        result = safe_find_text(root, "item", "default")
        assert result == "default"


class TestSafeFindInt:
    """Test safe_find_int utility function."""

    def test_parses_valid_integer(self):
        """Test parsing valid integer from XML."""
        xml = "<root><count>42</count></root>"
        root = ET.fromstring(xml)
        result = safe_find_int(root, "count")
        assert result == 42

    def test_returns_default_for_missing_element(self):
        """Test default value when element doesn't exist."""
        xml = "<root></root>"
        root = ET.fromstring(xml)
        result = safe_find_int(root, "missing", 99)
        assert result == 99

    def test_returns_zero_default_when_not_specified(self):
        """Test zero default when no default specified."""
        xml = "<root></root>"
        root = ET.fromstring(xml)
        result = safe_find_int(root, "missing")
        assert result == 0

    def test_returns_default_for_invalid_integer(self):
        """Test default value when text cannot be parsed as integer."""
        xml = "<root><count>not_a_number</count></root>"
        root = ET.fromstring(xml)
        result = safe_find_int(root, "count", 99)
        assert result == 99

    def test_handles_negative_integers(self):
        """Test parsing negative integers."""
        xml = "<root><value>-123</value></root>"
        root = ET.fromstring(xml)
        result = safe_find_int(root, "value")
        assert result == -123


class TestSafeFindBool:
    """Test safe_find_bool utility function."""

    def test_parses_true_string(self):
        """Test parsing 'True' string."""
        xml = "<root><flag>True</flag></root>"
        root = ET.fromstring(xml)
        result = safe_find_bool(root, "flag")
        assert result is True

    def test_parses_false_string(self):
        """Test parsing 'False' string."""
        xml = "<root><flag>False</flag></root>"
        root = ET.fromstring(xml)
        result = safe_find_bool(root, "flag")
        assert result is False

    def test_parses_one_as_true(self):
        """Test parsing '1' as True."""
        xml = "<root><flag>1</flag></root>"
        root = ET.fromstring(xml)
        result = safe_find_bool(root, "flag")
        assert result is True

    def test_parses_zero_as_false(self):
        """Test parsing '0' as False."""
        xml = "<root><flag>0</flag></root>"
        root = ET.fromstring(xml)
        result = safe_find_bool(root, "flag")
        assert result is False

    def test_parses_yes_as_true(self):
        """Test parsing 'yes' as True."""
        xml = "<root><flag>yes</flag></root>"
        root = ET.fromstring(xml)
        result = safe_find_bool(root, "flag")
        assert result is True

    def test_returns_default_for_missing_element(self):
        """Test default value when element doesn't exist."""
        xml = "<root></root>"
        root = ET.fromstring(xml)
        result = safe_find_bool(root, "missing", True)
        assert result is True

    def test_returns_false_default_when_not_specified(self):
        """Test False default when no default specified."""
        xml = "<root></root>"
        root = ET.fromstring(xml)
        result = safe_find_bool(root, "missing")
        assert result is False

    def test_case_insensitive_parsing(self):
        """Test case insensitive boolean parsing."""
        xml = "<root><flag>TRUE</flag></root>"
        root = ET.fromstring(xml)
        result = safe_find_bool(root, "flag")
        assert result is True


class TestParseUser:
    """Test parse_user function."""

    def test_parses_basic_user_data(self):
        """Test parsing basic user information."""
        xml = """
        <root>
            <Manager>
                <UserId>12345</UserId>
                <Loginname>testuser</Loginname>
            </Manager>
            <Teams>
                <Team><TeamId>67890</TeamId></Team>
                <Team><TeamId>11111</TeamId></Team>
            </Teams>
        </root>
        """
        root = ET.fromstring(xml)
        user = parse_user(root)

        assert isinstance(user, CHPPUser)
        assert user.ht_id == 12345
        assert user.username == "testuser"
        assert user._teams_ht_id == [67890, 11111]
        assert user.youth_team_id is None

    def test_parses_user_with_youth_team(self):
        """Test parsing user with youth team ID."""
        xml = """
        <root>
            <Manager>
                <UserId>12345</UserId>
                <Loginname>testuser</Loginname>
            </Manager>
            <YouthTeam>
                <YouthTeamId>99999</YouthTeamId>
            </YouthTeam>
            <Teams>
                <Team><TeamId>67890</TeamId></Team>
            </Teams>
        </root>
        """
        root = ET.fromstring(xml)
        user = parse_user(root)

        assert user.youth_team_id == 99999

    def test_handles_missing_optional_fields(self):
        """Test parsing user with missing optional fields."""
        xml = """
        <root>
            <Manager>
                <UserId>12345</UserId>
            </Manager>
        </root>
        """
        root = ET.fromstring(xml)
        user = parse_user(root)

        assert user.ht_id == 12345
        assert user.username == ""  # Default empty string
        assert user._teams_ht_id == []  # No teams
        assert user.youth_team_id is None

    def test_handles_empty_team_nodes(self):
        """Test handling team nodes with empty text."""
        xml = """
        <root>
            <Manager>
                <UserId>12345</UserId>
                <Loginname>testuser</Loginname>
            </Manager>
            <Teams>
                <Team><TeamId>67890</TeamId></Team>
                <Team><TeamId></TeamId></Team>
                <Team><TeamId>11111</TeamId></Team>
            </Teams>
        </root>
        """
        root = ET.fromstring(xml)
        user = parse_user(root)

        # Should skip the empty team ID
        assert user._teams_ht_id == [67890, 11111]


class TestParseTeam:
    """Test parse_team function."""

    def test_parses_basic_team_data(self):
        """Test parsing basic team information."""
        xml = """
        <root>
            <Team>
                <TeamID>12345</TeamID>
                <TeamName>Test Team</TeamName>
                <ShortTeamName>TT</ShortTeamName>
                <RegionId>123</RegionId>
                <FoundedDate>2020-01-01</FoundedDate>
                <LogoURL>http://example.com/logo.png</LogoURL>
            </Team>
            <League>
                <LeagueName>Test League</LeagueName>
                <LeagueLevel>3</LeagueLevel>
            </League>
            <Arena>
                <ArenaName>Test Arena</ArenaName>
                <ArenaId>456</ArenaId>
            </Arena>
        </root>
        """
        root = ET.fromstring(xml)
        team = parse_team(root)

        assert isinstance(team, CHPPTeam)
        assert team.team_id == 12345
        assert team.name == "Test Team"
        assert team.short_team_name == "TT"
        assert team.league_name == "Test League"
        assert team.league_level == 3
        assert team.region_id == 123
        assert team.founded_date == "2020-01-01"
        assert team.arena_name == "Test Arena"
        assert team.arena_id == 456
        assert team.logo_url == "http://example.com/logo.png"

    def test_parses_fan_data(self):
        """Test parsing fan club and supporters information."""
        xml = """
        <root>
            <Team>
                <TeamID>12345</TeamID>
                <TeamName>Test Team</TeamName>
                <ShortTeamName>TT</ShortTeamName>
            </Team>
            <FanClub>
                <FanClubSize>1500</FanClubSize>
            </FanClub>
            <Fans>
                <FansMood>delirious</FansMood>
                <FansMatchAttitude>playitcool</FansMatchAttitude>
            </Fans>
        </root>
        """
        root = ET.fromstring(xml)
        team = parse_team(root)

        assert team.fanclub_size == 1500
        assert team.fans_mood == "delirious"
        assert team.fans_match_attitude == "playitcool"

    def test_handles_missing_optional_fields(self):
        """Test parsing team with missing optional fields."""
        xml = """
        <root>
            <Team>
                <TeamID>12345</TeamID>
                <TeamName>Test Team</TeamName>
                <ShortTeamName>TT</ShortTeamName>
            </Team>
        </root>
        """
        root = ET.fromstring(xml)
        team = parse_team(root)

        assert team.team_id == 12345
        assert team.name == "Test Team"
        assert team.short_team_name == "TT"
        # All optional fields should be None or default values
        assert team.league_name is None
        assert team.league_level is None
        assert team.region_id is None
        assert team.arena_id is None
        assert team.fanclub_size is None


class TestParsePlayer:
    """Test parse_player function."""

    def test_parses_basic_player_data(self):
        """Test parsing basic player information."""
        xml = """
        <root>
            <Player>
                <PlayerID>12345</PlayerID>
                <FirstName>John</FirstName>
                <LastName>Doe</LastName>
                <NickName>JD</NickName>
                <Age>25</Age>
                <AgeDays>100</AgeDays>
                <TSI>1500</TSI>
                <PlayerNumber>9</PlayerNumber>
                <PlayerForm>7</PlayerForm>
                <Experience>6</Experience>
                <Loyalty>5</Loyalty>
                <PlayerSkills>
                    <StaminaSkill>8</StaminaSkill>
                    <KeeperSkill>1</KeeperSkill>
                    <DefenderSkill>7</DefenderSkill>
                    <PlaymakerSkill>9</PlaymakerSkill>
                    <WingerSkill>6</WingerSkill>
                    <PassingSkill>8</PassingSkill>
                    <ScorerSkill>10</ScorerSkill>
                    <SetPiecesSkill>5</SetPiecesSkill>
                </PlayerSkills>
            </Player>
        </root>
        """
        root = ET.fromstring(xml)
        player = parse_player(root)

        assert isinstance(player, CHPPPlayer)
        assert player.player_id == 12345
        assert player.first_name == "John"
        assert player.last_name == "Doe"
        assert player.nick_name == "JD"
        assert player.age == 25
        assert player.age_days == 100
        assert player.tsi == 1500
        assert player.player_number == 9
        assert player.form == 7
        assert player.experience == 6
        assert player.loyalty == 5
        # Test skills
        assert player.stamina == 8
        assert player.keeper == 1
        assert player.defender == 7
        assert player.playmaker == 9
        assert player.winger == 6
        assert player.passing == 8
        assert player.scorer == 10
        assert player.set_pieces == 5

    def test_handles_missing_skills_container(self):
        """Test parsing player without PlayerSkills container."""
        xml = """
        <root>
            <Player>
                <PlayerID>12345</PlayerID>
                <FirstName>John</FirstName>
                <LastName>Doe</LastName>
            </Player>
        </root>
        """
        root = ET.fromstring(xml)
        player = parse_player(root)

        assert player.player_id == 12345
        assert player.first_name == "John"
        assert player.last_name == "Doe"
        # Skills should default to 0 when missing
        assert player.stamina == 0
        assert player.scorer == 0


class TestParsePlayers:
    """Test parse_players function."""

    def test_parses_multiple_players(self):
        """Test parsing multiple players from players endpoint."""
        xml = """
        <root>
            <PlayerList>
                <Player>
                    <PlayerID>12345</PlayerID>
                    <FirstName>John</FirstName>
                    <LastName>Doe</LastName>
                    <Age>25</Age>
                    <PlayerSkills>
                        <StaminaSkill>8</StaminaSkill>
                        <ScorerSkill>10</ScorerSkill>
                    </PlayerSkills>
                </Player>
                <Player>
                    <PlayerID>67890</PlayerID>
                    <FirstName>Jane</FirstName>
                    <LastName>Smith</LastName>
                    <Age>23</Age>
                    <PlayerSkills>
                        <KeeperSkill>9</KeeperSkill>
                        <DefenderSkill>7</DefenderSkill>
                    </PlayerSkills>
                </Player>
            </PlayerList>
        </root>
        """
        root = ET.fromstring(xml)
        players = parse_players(root)

        assert len(players) == 2
        assert all(isinstance(p, CHPPPlayer) for p in players)

        # First player
        assert players[0].player_id == 12345
        assert players[0].first_name == "John"
        assert players[0].stamina == 8
        assert players[0].scorer == 10

        # Second player
        assert players[1].player_id == 67890
        assert players[1].first_name == "Jane"
        assert players[1].keeper == 9
        assert players[1].defender == 7

    def test_handles_empty_player_list(self):
        """Test parsing empty player list."""
        xml = """
        <root>
            <PlayerList>
            </PlayerList>
        </root>
        """
        root = ET.fromstring(xml)
        players = parse_players(root)

        assert players == []

    def test_handles_missing_player_list(self):
        """Test parsing when PlayerList is missing."""
        xml = "<root></root>"
        root = ET.fromstring(xml)
        players = parse_players(root)

        assert players == []


class TestParseMatches:
    """Test parse_matches function."""

    def test_parses_basic_match_data(self):
        """Test parsing basic match information."""
        xml = """
        <root>
            <Team>
                <MatchList>
                    <Match>
                        <MatchID>12345</MatchID>
                        <MatchDate>2024-01-15 15:00:00</MatchDate>
                        <MatchType>1</MatchType>
                        <HomeTeamID>100</HomeTeamID>
                        <HomeTeamName>Home Team</HomeTeamName>
                        <AwayTeamID>200</AwayTeamID>
                        <AwayTeamName>Away Team</AwayTeamName>
                        <HomeGoals>2</HomeGoals>
                        <AwayGoals>1</AwayGoals>
                    </Match>
                </MatchList>
            </Team>
        </root>
        """
        root = ET.fromstring(xml)
        matches = parse_matches(root)

        assert len(matches) == 1
        match = matches[0]
        assert isinstance(match, CHPPMatch)
        assert match.ht_id == 12345
        assert match.datetime == "2024-01-15 15:00:00"
        assert match.matchtype == 1
        assert match.home_team_id == 100
        assert match.home_team_name == "Home Team"
        assert match.away_team_id == 200
        assert match.away_team_name == "Away Team"
        assert match.home_goals == 2
        assert match.away_goals == 1

    def test_parses_multiple_matches(self):
        """Test parsing multiple matches."""
        xml = """
        <root>
            <Team>
                <MatchList>
                    <Match>
                        <MatchID>11111</MatchID>
                        <MatchDate>2024-01-15 15:00:00</MatchDate>
                        <MatchType>1</MatchType>
                    </Match>
                    <Match>
                        <MatchID>22222</MatchID>
                        <MatchDate>2024-01-22 15:00:00</MatchDate>
                        <MatchType>2</MatchType>
                    </Match>
                </MatchList>
            </Team>
        </root>
        """
        root = ET.fromstring(xml)
        matches = parse_matches(root)

        assert len(matches) == 2
        assert matches[0].ht_id == 11111
        assert matches[1].ht_id == 22222

    def test_handles_empty_match_list(self):
        """Test parsing empty match list."""
        xml = """
        <root>
            <Team>
                <MatchList>
                </MatchList>
            </Team>
        </root>
        """
        root = ET.fromstring(xml)
        matches = parse_matches(root)

        assert matches == []
