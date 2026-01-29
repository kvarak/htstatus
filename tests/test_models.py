"""Tests for both models.py (root level) and app/chpp/models.py"""

from datetime import datetime
from unittest.mock import patch

from models import Group, Match, MatchPlay, Players, PlayerSetting, User


def test_root_models_imports():
    """Test that root models module imports without errors."""
    import models
    assert models is not None


def test_chpp_models_imports():
    """Test that CHPP models module imports without errors."""
    import app.chpp.models
    assert app.chpp.models is not None


class TestUserModel:
    """Test User model functionality."""

    def test_user_creation(self):
        """Test User model initialization with all required fields."""
        with patch('time.strftime', return_value="2024-01-01 12:00:00"):
            user = User(
                ht_id=12345,
                ht_user="test_ht_user",
                username="testuser",
                password="testpass",
                access_key="access_key",
                access_secret="access_secret"
            )

            assert user.ht_id == 12345
            assert user.ht_user == "test_ht_user"
            assert user.username == "testuser"
            assert user.password == "testpass"
            assert user.access_key == "access_key"
            assert user.access_secret == "access_secret"
            assert user.c_login == 1
            assert user.c_team == 0
            assert user.c_player == 0
            assert user.role == ""

    def test_user_role_management(self):
        """Test User role getter and setter methods."""
        user = User(12345, "test", "user", "pass", "key", "secret")

        # Test default role
        assert user.getRole() == ""

        # Test setting role
        user.setRole("admin")
        assert user.getRole() == "admin"

    def test_user_activity_tracking(self):
        """Test User activity tracking methods."""
        user = User(12345, "test", "user", "pass", "key", "secret")

        initial_login = user.c_login
        initial_player = user.c_player
        initial_matches = user.c_matches
        initial_team = user.c_team
        initial_training = user.c_training
        initial_update = user.c_update

        # Test each activity tracking method
        user.login()
        assert user.c_login == initial_login + 1

        user.player()
        assert user.c_player == initial_player + 1

        user.matches()
        assert user.c_matches == initial_matches + 1

        user.team()
        assert user.c_team == initial_team + 1

        user.training()
        assert user.c_training == initial_training + 1

        user.updatedata()
        assert user.c_update == initial_update + 1

    def test_user_columns_management(self):
        """Test User column preferences functionality."""
        user = User(12345, "test", "user", "pass", "key", "secret")

        # Test default columns (empty list)
        assert user.getColumns() == []

        # Test setting columns
        test_columns = ["name", "age", "form"]
        user.updateColumns(test_columns)
        assert user.getColumns() == test_columns

        # Test updating columns
        new_columns = ["name", "stamina", "keeper"]
        user.updateColumns(new_columns)
        assert user.getColumns() == new_columns

    def test_user_columns_error_handling(self):
        """Test User columns error handling with corrupted data."""
        user = User(12345, "test", "user", "pass", "key", "secret")

        # Simulate corrupted pickle data
        user.player_columns = b"corrupted_data"

        # Should return empty list on error
        assert user.getColumns() == []

    def test_user_claim_user(self):
        """Test User claimUser method updates credentials."""
        user = User(12345, "test", "user", "pass", "key", "secret")
        original_login_count = user.c_login

        user.claimUser("newuser", "newpass", "newkey", "newsecret")

        assert user.username == "newuser"
        assert user.password == "newpass"
        assert user.access_key == "newkey"
        assert user.access_secret == "newsecret"
        assert user.c_login == original_login_count + 1

    def test_user_repr(self):
        """Test User string representation."""
        user = User(12345, "test", "testuser", "pass", "key", "secret")
        assert str(user) == "<id testuser>"


class TestGroupModel:
    """Test Group model functionality."""

    def test_group_creation(self):
        """Test Group model initialization."""
        group = Group(
            user_id=12345,
            name="Goalkeepers",
            order=1,
            textcolor="#000000",
            bgcolor="#FFD700"
        )

        assert group.user_id == 12345
        assert group.name == "Goalkeepers"
        assert group.order == 1
        assert group.textcolor == "#000000"
        assert group.bgcolor == "#FFD700"

    def test_group_repr(self):
        """Test Group string representation."""
        group = Group(12345, "Test Group", 5, "#000", "#FFF")
        assert str(group) == "<Test Group 5>"


class TestPlayerSettingModel:
    """Test PlayerSetting model functionality."""

    def test_player_setting_creation(self):
        """Test PlayerSetting model initialization."""
        setting = PlayerSetting(
            player_id=123456,
            user_id=12345,
            group_id=1
        )

        assert setting.player_id == 123456
        assert setting.user_id == 12345
        assert setting.group_id == 1

    def test_player_setting_repr(self):
        """Test PlayerSetting string representation."""
        setting = PlayerSetting(123456, 12345, 1)
        assert str(setting) == "<123456 1>"


class TestMatchModel:
    """Test Match model functionality."""

    def test_match_creation(self):
        """Test Match model initialization with required data."""
        match_data = {
            "ht_id": 987654,
            "home_team_id": 12345,
            "home_team_name": "Home Team FC",
            "away_team_id": 54321,
            "away_team_name": "Away United",
            "datetime": datetime(2024, 1, 15, 15, 0),
            "matchtype": 1,
            "context_id": 0,
            "rule_id": 0,
            "cup_level": 0,
            "cup_level_index": 0,
            "home_goals": 2,
            "away_goals": 1
        }

        match = Match(match_data)

        assert match.ht_id == 987654
        assert match.home_team_id == 12345
        assert match.home_team_name == "Home Team FC"
        assert match.away_team_id == 54321
        assert match.away_team_name == "Away United"
        assert match.home_goals == 2
        assert match.away_goals == 1
        assert match.matchtype == 1

    def test_match_repr(self):
        """Test Match string representation."""
        match_data = {
            "ht_id": 111222,
            "home_team_id": 12345,
            "home_team_name": "Test FC",
            "away_team_id": 54321,
            "away_team_name": "Sample United",
            "datetime": datetime(2024, 3, 15, 15, 0),
            "matchtype": 1, "context_id": 0, "rule_id": 0,
            "cup_level": 0, "cup_level_index": 0,
            "home_goals": 3, "away_goals": 0
        }

        match = Match(match_data)
        assert str(match) == "Test FC - Sample United: 111222"


class TestMatchPlayModel:
    """Test MatchPlay model functionality."""

    def test_matchplay_creation(self):
        """Test MatchPlay model initialization."""
        matchplay_data = {
            "match_id": 987654,
            "player_id": 123456,
            "datetime": datetime(2024, 3, 15, 15, 0),
            "first_name": "John",
            "nick_name": "Johnny",
            "last_name": "Doe",
            "role_id": 100,
            "rating_stars": 7.5,
            "rating_stars_eom": 7.0,
            "behaviour": 1
        }

        matchplay = MatchPlay(matchplay_data)

        assert matchplay.match_id == 987654
        assert matchplay.player_id == 123456
        assert matchplay.first_name == "John"
        assert matchplay.nick_name == "Johnny"
        assert matchplay.last_name == "Doe"
        assert matchplay.rating_stars == 7.5
        assert matchplay.rating_stars_eom == 7.0
        assert matchplay.role_id == 100

    def test_matchplay_repr(self):
        """Test MatchPlay string representation."""
        matchplay_data = {
            "match_id": 987655, "player_id": 123457,
            "datetime": datetime(2024, 3, 15, 15, 0),
            "first_name": "Jane", "nick_name": "Janie",
            "last_name": "Smith", "role_id": 101,
            "rating_stars": 8.0, "rating_stars_eom": 7.5,
            "behaviour": 1
        }

        matchplay = MatchPlay(matchplay_data)
        assert "Jane Smith" in str(matchplay)
        assert "8.0/7.5" in str(matchplay)


class TestPlayersModel:
    """Test Players model functionality."""

    def test_players_creation_basic(self):
        """Test Players model initialization with basic required fields."""
        player_data = {
            "ht_id": 123456,
            "first_name": "Test", "nick_name": "Test", "last_name": "Player",
            "number": 1, "category_id": 0, "owner_notes": "",
            "age_years": 25, "age_days": 100, "age": "25.100",
            "next_birthday": datetime(2024, 6, 1),
            "arrival_date": datetime(2024, 1, 1),
            "form": 7, "cards": 0, "injury_level": 0, "statement": "",
            "language": "English", "language_id": 2,
            "agreeability": 3, "aggressiveness": 3, "honesty": 3,
            "experience": 5, "loyalty": 10, "specialty": 0,
            "native_country_id": 1, "native_league_id": 1,
            "native_league_name": "Test League", "tsi": 1000, "salary": 5000,
            "caps": 0, "caps_u20": 0, "career_goals": 10, "career_hattricks": 1,
            "league_goals": 5, "cup_goals": 2, "friendly_goals": 3,
            "current_team_matches": 20, "current_team_goals": 8,
            "national_team_id": 0, "national_team_name": "",
            "is_transfer_listed": False, "team_id": 12345,
            "stamina": 6, "keeper": 3, "defender": 7, "playmaker": 8,
            "winger": 5, "passing": 6, "scorer": 9, "set_pieces": 4,
            "owner": 12345, "mother_club_bonus": False, "leadership": 5
        }

        player = Players(player_data)

        assert player.ht_id == 123456
        assert player.first_name == "Test"
        assert player.last_name == "Player"
        assert player.keeper == 3
        assert player.scorer == 9
        assert player.is_transfer_listed is False

    def test_players_boolean_conversion(self):
        """Test Players model boolean field conversion."""
        player_data = {
            "ht_id": 123457, "first_name": "Bool", "nick_name": "Test",
            "last_name": "Player", "number": 2, "category_id": 0,
            "owner_notes": "", "age_years": 26, "age_days": 30, "age": "26.30",
            "next_birthday": datetime(2024, 9, 1),
            "arrival_date": datetime(2023, 6, 15),
            "form": 7, "cards": 1, "injury_level": 1, "statement": "",
            "language": "German", "language_id": 4,
            "agreeability": 7, "aggressiveness": 6, "honesty": 8,
            "experience": 6, "loyalty": 7, "specialty": 1,
            "native_country_id": 10, "native_league_id": 3,
            "native_league_name": "Germany", "tsi": 3000, "salary": 18000,
            "caps": 5, "caps_u20": 8, "career_goals": 20, "career_hattricks": 1,
            "league_goals": 15, "cup_goals": 3, "friendly_goals": 2,
            "current_team_matches": 40, "current_team_goals": 15,
            "national_team_id": 3010, "national_team_name": "Germany",
            "is_transfer_listed": 1,  # Truthy value
            "team_id": 54321, "stamina": 8, "keeper": 5, "defender": 8,
            "playmaker": 7, "winger": 6, "passing": 7, "scorer": 8,
            "set_pieces": 6, "owner": 12345,
            "mother_club_bonus": 1,  # Truthy value
            "leadership": 6
        }

        player = Players(player_data)

        assert player.is_transfer_listed is True
        assert player.mother_club_bonus is True
        assert isinstance(player.is_transfer_listed, bool)
        assert isinstance(player.mother_club_bonus, bool)

    def test_players_repr(self):
        """Test Players string representation."""
        player_data = {
            "ht_id": 999999, "first_name": "Repr", "nick_name": "Test",
            "last_name": "Player", "number": 99, "category_id": 0,
            "owner_notes": "", "age_years": 20, "age_days": 0, "age": "20.0",
            "next_birthday": datetime(2024, 6, 1),
            "arrival_date": datetime(2024, 1, 1),
            "form": 6, "cards": 0, "injury_level": 0, "statement": "",
            "language": "English", "language_id": 2,
            "agreeability": 5, "aggressiveness": 5, "honesty": 5,
            "experience": 3, "loyalty": 6, "specialty": 0,
            "native_country_id": 1, "native_league_id": 1,
            "native_league_name": "Test League", "tsi": 1000, "salary": 5000,
            "caps": 0, "caps_u20": 0, "career_goals": 0, "career_hattricks": 0,
            "league_goals": 0, "cup_goals": 0, "friendly_goals": 0,
            "current_team_matches": 0, "current_team_goals": 0,
            "national_team_id": 0, "national_team_name": "",
            "is_transfer_listed": False, "team_id": 12345,
            "stamina": 5, "keeper": 5, "defender": 5, "playmaker": 5,
            "winger": 5, "passing": 5, "scorer": 5, "set_pieces": 5,
            "owner": 12345, "mother_club_bonus": False, "leadership": 5
        }

        player = Players(player_data)
        player_str = str(player)
        assert "Repr Player" in player_str
        assert "999999" in player_str
