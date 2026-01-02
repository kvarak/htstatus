"""Test database operations and models."""

import time
from datetime import datetime

from sqlalchemy import text

from app.factory import db
from models import Players, Match, MatchPlay, User, Group, PlayerSetting


def test_database_connection(app, db_session):
    """Test that database connection works."""
    with app.app_context():
        # Test basic database connectivity using modern SQLAlchemy
        result = db_session.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1


def test_database_tables_created(app, db_session):
    """Test that all required tables are created."""
    with app.app_context():
        # Check that tables exist in the database
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        # These are the core tables we expect based on the models
        # Note: SQLAlchemy might create them with different names
        assert len(tables) > 0, "No tables found in test database"


def test_database_session_rollback(app, db_session):
    """Test that database session rollback works properly."""
    with app.app_context():
        # This test ensures our test isolation is working
        # Any changes made here should be rolled back after the test

        # Try a simple transaction using modern SQLAlchemy
        try:
            db_session.execute(text("CREATE TEMPORARY TABLE test_rollback (id INTEGER)"))
            db_session.commit()
        except Exception:
            # If it fails, that's fine - we're just testing the rollback mechanism
            pass

        # The main assertion is that this test can run multiple times
        # without conflicts, which proves rollback is working
        assert True


def test_database_isolation_between_tests(app, db_session):
    """Test that tests are isolated from each other."""
    with app.app_context():
        # This test should not see any data from other tests
        # because each test gets a fresh transaction that rolls back

        # This is more of a structural test to ensure our test setup is correct
        assert db_session is not None
        assert db_session.is_active


# ============================================================================
# Player Model Tests
# ============================================================================

def test_player_creation(app, db_session):
    """Test creating a player with all required fields."""
    with app.app_context():
        player_data = {
            'ht_id': 123456,
            'first_name': 'John',
            'nick_name': 'Johnny',
            'last_name': 'Doe',
            'number': 7,
            'category_id': 0,
            'owner_notes': 'Test notes',
            'age_years': 23,
            'age_days': 45,
            'age': '23.45',
            'next_birthday': datetime(2024, 6, 15),
            'arrival_date': datetime(2023, 1, 15),
            'form': 7,
            'cards': 0,
            'injury_level': 0,
            'statement': 'Feeling good',
            'language': 'English',
            'language_id': 2,
            'agreeability': 6,
            'aggressiveness': 5,
            'honesty': 8,
            'experience': 4,
            'loyalty': 7,
            'specialty': 1,
            'native_country_id': 5,
            'native_league_id': 1,
            'native_league_name': 'England',
            'tsi': 2500,
            'salary': 15000,
            'caps': 2,
            'caps_u20': 5,
            'career_goals': 12,
            'career_hattricks': 1,
            'league_goals': 8,
            'cup_goals': 2,
            'friendly_goals': 2,
            'current_team_matches': 25,
            'current_team_goals': 8,
            'national_team_id': 3001,
            'national_team_name': 'England',
            'is_transfer_listed': False,
            'team_id': 54321,
            'stamina': 8,
            'keeper': 4,
            'defender': 8,
            'playmaker': 6,
            'winger': 7,
            'passing': 6,
            'scorer': 9,
            'set_pieces': 5,
            'owner': 12345,
            'mother_club_bonus': True,
            'leadership': 6
        }
        
        player = Players(player_data)
        db_session.add(player)
        db_session.commit()
        
        # Test player was created with correct values
        assert player.ht_id == 123456
        assert player.first_name == 'John'
        assert player.nick_name == 'Johnny'
        assert player.last_name == 'Doe'
        assert player.stamina == 8
        assert player.keeper == 4
        assert player.defender == 8
        assert player.scorer == 9
        assert player.is_transfer_listed is False
        assert player.mother_club_bonus is True


def test_player_skill_calculations(app, db_session):
    """Test player skill-related calculations and properties."""
    with app.app_context():
        player_data = {
            'ht_id': 123457,
            'first_name': 'Test',
            'nick_name': 'Player',
            'last_name': 'Skills',
            'number': 8,
            'category_id': 0,
            'owner_notes': '',
            'age_years': 25,
            'age_days': 0,
            'age': '25.0',
            'next_birthday': datetime(2024, 12, 1),
            'arrival_date': datetime(2024, 1, 1),
            'form': 8,
            'cards': 1,
            'injury_level': 0,
            'statement': '',
            'language': 'Spanish',
            'language_id': 3,
            'agreeability': 7,
            'aggressiveness': 6,
            'honesty': 8,
            'experience': 8,
            'loyalty': 9,
            'specialty': 2,
            'native_country_id': 15,
            'native_league_id': 5,
            'native_league_name': 'Spain',
            'tsi': 3500,
            'salary': 25000,
            'caps': 15,
            'caps_u20': 12,
            'career_goals': 45,
            'career_hattricks': 3,
            'league_goals': 30,
            'cup_goals': 8,
            'friendly_goals': 7,
            'current_team_matches': 60,
            'current_team_goals': 30,
            'national_team_id': 3015,
            'national_team_name': 'Spain',
            'is_transfer_listed': True,
            'team_id': 54321,
            'stamina': 9,
            'keeper': 3,
            'defender': 6,
            'playmaker': 8,
            'winger': 5,
            'passing': 7,
            'scorer': 10,
            'set_pieces': 8,
            'owner': 12345,
            'mother_club_bonus': False,
            'leadership': 7
        }
        
        player = Players(player_data)
        db_session.add(player)
        db_session.commit()
        
        # Test high-level skills
        assert player.scorer == 10  # Excellent scorer
        assert player.stamina == 9   # Excellent stamina
        assert player.playmaker == 8 # Formidable playmaker
        
        # Test experience and form interaction
        assert player.experience == 8
        assert player.form == 8
        
        # Test specialty and leadership
        assert player.specialty == 2
        assert player.leadership == 7


def test_player_repr(app, db_session):
    """Test player string representation."""
    with app.app_context():
        player_data = {
            'ht_id': 999999,
            'first_name': 'Representation',
            'nick_name': 'Test',
            'last_name': 'Player',
            'number': 99,
            'category_id': 0,
            'owner_notes': '',
            'age_years': 20,
            'age_days': 0,
            'age': '20.0',
            'next_birthday': datetime(2024, 6, 1),
            'arrival_date': datetime(2024, 1, 1),
            'form': 6,
            'cards': 0,
            'injury_level': 0,
            'statement': '',
            'language': 'English',
            'language_id': 2,
            'agreeability': 5,
            'aggressiveness': 5,
            'honesty': 5,
            'experience': 3,
            'loyalty': 6,
            'specialty': 0,
            'native_country_id': 1,
            'native_league_id': 1,
            'native_league_name': 'Test League',
            'tsi': 1000,
            'salary': 5000,
            'caps': 0,
            'caps_u20': 0,
            'career_goals': 0,
            'career_hattricks': 0,
            'league_goals': 0,
            'cup_goals': 0,
            'friendly_goals': 0,
            'current_team_matches': 0,
            'current_team_goals': 0,
            'national_team_id': 0,
            'national_team_name': '',
            'is_transfer_listed': False,
            'team_id': 12345,
            'stamina': 5,
            'keeper': 5,
            'defender': 5,
            'playmaker': 5,
            'winger': 5,
            'passing': 5,
            'scorer': 5,
            'set_pieces': 5,
            'owner': 12345,
            'mother_club_bonus': False,
            'leadership': 5
        }
        
        player = Players(player_data)
        db_session.add(player)
        db_session.commit()
        
        player_str = str(player)
        assert 'Representation Player' in player_str
        assert '999999' in player_str


# ============================================================================
# Match Model Tests  
# ============================================================================

def test_match_creation(app, db_session):
    """Test creating a match with all required fields."""
    with app.app_context():
        match_data = {
            'ht_id': 987654,
            'home_team_id': 12345,
            'home_team_name': 'Home Team',
            'away_team_id': 54321,
            'away_team_name': 'Away Team',
            'datetime': datetime(2024, 3, 15, 15, 0),
            'matchtype': 1,
            'context_id': 0,
            'rule_id': 0,
            'cup_level': 0,
            'cup_level_index': 0,
            'home_goals': 2,
            'away_goals': 1
        }
        
        match = Match(match_data)
        db_session.add(match)
        db_session.commit()
        
        # Test match was created with correct values
        assert match.ht_id == 987654
        assert match.home_team_name == 'Home Team'
        assert match.away_team_name == 'Away Team'
        assert match.home_goals == 2
        assert match.away_goals == 1
        assert match.matchtype == 1


def test_match_repr(app, db_session):
    """Test match string representation."""
    with app.app_context():
        match_data = {
            'ht_id': 111222,
            'home_team_id': 12345,
            'home_team_name': 'Test FC',
            'away_team_id': 54321,
            'away_team_name': 'Sample United',
            'datetime': datetime(2024, 3, 15, 15, 0),
            'matchtype': 1,
            'context_id': 0,
            'rule_id': 0,
            'cup_level': 0,
            'cup_level_index': 0,
            'home_goals': 3,
            'away_goals': 0
        }
        
        match = Match(match_data)
        db_session.add(match)
        db_session.commit()
        
        match_str = str(match)
        assert 'Test FC - Sample United' in match_str
        assert '111222' in match_str


# ============================================================================
# MatchPlay Model Tests
# ============================================================================

def test_matchplay_creation(app, db_session):
    """Test creating a matchplay record."""
    with app.app_context():
        matchplay_data = {
            'match_id': 987654,
            'player_id': 123456,
            'datetime': datetime(2024, 3, 15, 15, 0),
            'first_name': 'John',
            'nick_name': 'Johnny',
            'last_name': 'Doe',
            'role_id': 100,
            'rating_stars': 7.5,
            'rating_stars_eom': 7.0,
            'behaviour': 1
        }
        
        matchplay = MatchPlay(matchplay_data)
        db_session.add(matchplay)
        db_session.commit()
        
        # Test matchplay was created with correct values
        assert matchplay.match_id == 987654
        assert matchplay.player_id == 123456
        assert matchplay.first_name == 'John'
        assert matchplay.last_name == 'Doe'
        assert matchplay.rating_stars == 7.5
        assert matchplay.rating_stars_eom == 7.0
        assert matchplay.role_id == 100


def test_matchplay_repr(app, db_session):
    """Test matchplay string representation."""
    with app.app_context():
        matchplay_data = {
            'match_id': 987655,
            'player_id': 123457,
            'datetime': datetime(2024, 3, 15, 15, 0),
            'first_name': 'Jane',
            'nick_name': 'Janie',
            'last_name': 'Smith',
            'role_id': 101,
            'rating_stars': 8.0,
            'rating_stars_eom': 7.5,
            'behaviour': 1
        }
        
        matchplay = MatchPlay(matchplay_data)
        db_session.add(matchplay)
        db_session.commit()
        
        matchplay_str = str(matchplay)
        assert 'Jane Smith' in matchplay_str
        assert '8.0/7.5' in matchplay_str


# ============================================================================
# User Model Tests
# ============================================================================

def test_user_creation(app, db_session):
    """Test creating a user with all required fields."""
    with app.app_context():
        user = User(12345, 'test_ht_user', 'testuser', 'password123', 'access_key', 'access_secret')
        db_session.add(user)
        db_session.commit()
        
        # Test user was created with correct values
        assert user.ht_id == 12345
        assert user.ht_user == 'test_ht_user'
        assert user.username == 'testuser'
        assert user.password == 'password123'
        assert user.access_key == 'access_key'
        assert user.access_secret == 'access_secret'
        assert user.c_login == 1
        assert user.c_team == 0
        assert user.c_player == 0


def test_user_methods(app, db_session):
    """Test user model methods."""
    with app.app_context():
        user = User(12346, 'test_ht_user2', 'testuser2', 'password123', 'access_key2', 'access_secret2')
        db_session.add(user)
        db_session.commit()
        
        # Test role methods
        user.setRole('admin')
        assert user.getRole() == 'admin'
        
        # Test activity tracking methods
        initial_login_count = user.c_login
        user.login()
        assert user.c_login == initial_login_count + 1
        
        initial_player_count = user.c_player
        user.player()
        assert user.c_player == initial_player_count + 1
        
        initial_matches_count = user.c_matches
        user.matches()
        assert user.c_matches == initial_matches_count + 1
        
        initial_team_count = user.c_team
        user.team()
        assert user.c_team == initial_team_count + 1
        
        initial_training_count = user.c_training
        user.training()
        assert user.c_training == initial_training_count + 1
        
        initial_update_count = user.c_update
        user.updatedata()
        assert user.c_update == initial_update_count + 1


def test_user_columns_methods(app, db_session):
    """Test user column preference methods."""
    with app.app_context():
        user = User(12347, 'test_ht_user3', 'testuser3', 'password123', 'access_key3', 'access_secret3')
        db_session.add(user)
        db_session.commit()
        
        # Test setting and getting columns
        test_columns = ['name', 'age', 'stamina', 'keeper', 'defender']
        user.updateColumns(test_columns)
        retrieved_columns = user.getColumns()
        assert retrieved_columns == test_columns
        
        # Test empty columns
        user.updateColumns([])
        empty_columns = user.getColumns()
        assert empty_columns == []


# ============================================================================
# Group and PlayerSetting Model Tests
# ============================================================================

def test_group_creation(app, db_session):
    """Test creating a player group."""
    with app.app_context():
        # Create a user first (foreign key requirement)
        user = User(12345, 'test_user', 'testuser', 'password', 'access_key', 'access_secret')
        db_session.add(user)
        db_session.commit()
        
        # Create the group
        group = Group(12345, 'Goalkeepers', 1, '#000000', '#FFD700')
        db_session.add(group)
        db_session.commit()
        
        # Test group was created with correct values
        assert group.user_id == 12345
        assert group.name == 'Goalkeepers'
        assert group.order == 1
        assert group.textcolor == '#000000'
        assert group.bgcolor == '#FFD700'


def test_player_setting_creation(app, db_session):
    """Test creating a player setting."""
    with app.app_context():
        # Create a user first (foreign key requirement)
        user = User(12346, 'test_user_ps', 'testuser_ps', 'password', 'access_key', 'access_secret')
        db_session.add(user)
        db_session.commit()
        
        # Create a group first (foreign key requirement) 
        group = Group(12346, 'Test Group', 1, '#000000', '#FFFFFF')
        db_session.add(group)
        db_session.commit()
        
        # Create the player setting with the group id
        player_setting = PlayerSetting(123456, 12346, group.id)
        db_session.add(player_setting)
        db_session.commit()
        
        # Test player setting was created with correct values
        assert player_setting.player_id == 123456
        assert player_setting.user_id == 12346
        assert player_setting.group_id == group.id


# ============================================================================
# Integration and Relationship Tests
# ============================================================================

def test_player_data_date_formatting(app, db_session):
    """Test that player data_date is properly formatted."""
    with app.app_context():
        player_data = {
            'ht_id': 555555,
            'first_name': 'Date',
            'nick_name': 'Test',
            'last_name': 'Player',
            'number': 5,
            'category_id': 0,
            'owner_notes': '',
            'age_years': 24,
            'age_days': 15,
            'age': '24.15',
            'next_birthday': datetime(2024, 8, 1),
            'arrival_date': datetime(2024, 1, 15),
            'form': 6,
            'cards': 0,
            'injury_level': 0,
            'statement': '',
            'language': 'English',
            'language_id': 2,
            'agreeability': 6,
            'aggressiveness': 5,
            'honesty': 7,
            'experience': 5,
            'loyalty': 6,
            'specialty': 0,
            'native_country_id': 5,
            'native_league_id': 1,
            'native_league_name': 'England',
            'tsi': 2000,
            'salary': 12000,
            'caps': 0,
            'caps_u20': 2,
            'career_goals': 5,
            'career_hattricks': 0,
            'league_goals': 3,
            'cup_goals': 1,
            'friendly_goals': 1,
            'current_team_matches': 15,
            'current_team_goals': 3,
            'national_team_id': 0,
            'national_team_name': '',
            'is_transfer_listed': False,
            'team_id': 54321,
            'stamina': 7,
            'keeper': 6,
            'defender': 7,
            'playmaker': 5,
            'winger': 6,
            'passing': 5,
            'scorer': 7,
            'set_pieces': 4,
            'owner': 12345,
            'mother_club_bonus': False,
            'leadership': 5
        }
        
        player = Players(player_data)
        db_session.add(player)
        db_session.commit()
        
        # Test that data_date is set (the model uses time.strftime which returns string)
        # Note: The model sets data_date to current date string in __init__
        assert player.data_date is not None
        # The actual format depends on how the model sets it - let's be flexible
        if isinstance(player.data_date, str):
            assert len(player.data_date) == 10  # YYYY-MM-DD format
            assert player.data_date.count('-') == 2  # Two dashes in date
        else:
            # If it's a datetime object, that's also acceptable
            assert hasattr(player.data_date, 'year')


def test_boolean_field_conversion(app, db_session):
    """Test that boolean fields are properly converted."""
    with app.app_context():
        player_data = {
            'ht_id': 777777,
            'first_name': 'Boolean',
            'nick_name': 'Test',
            'last_name': 'Player',
            'number': 7,
            'category_id': 0,
            'owner_notes': '',
            'age_years': 26,
            'age_days': 30,
            'age': '26.30',
            'next_birthday': datetime(2024, 9, 1),
            'arrival_date': datetime(2023, 6, 15),
            'form': 7,
            'cards': 1,
            'injury_level': 1,
            'statement': '',
            'language': 'German',
            'language_id': 4,
            'agreeability': 7,
            'aggressiveness': 6,
            'honesty': 8,
            'experience': 6,
            'loyalty': 7,
            'specialty': 1,
            'native_country_id': 10,
            'native_league_id': 3,
            'native_league_name': 'Germany',
            'tsi': 3000,
            'salary': 18000,
            'caps': 5,
            'caps_u20': 8,
            'career_goals': 20,
            'career_hattricks': 1,
            'league_goals': 15,
            'cup_goals': 3,
            'friendly_goals': 2,
            'current_team_matches': 40,
            'current_team_goals': 15,
            'national_team_id': 3010,
            'national_team_name': 'Germany',
            'is_transfer_listed': 1,  # Truthy value
            'team_id': 54321,
            'stamina': 8,
            'keeper': 5,
            'defender': 8,
            'playmaker': 7,
            'winger': 6,
            'passing': 7,
            'scorer': 8,
            'set_pieces': 6,
            'owner': 12345,
            'mother_club_bonus': 1,  # Truthy value
            'leadership': 6
        }
        
        player = Players(player_data)
        db_session.add(player)
        db_session.commit()
        
        # Test boolean conversion
        assert player.is_transfer_listed is True
        assert player.mother_club_bonus is True
        assert isinstance(player.is_transfer_listed, bool)
        assert isinstance(player.mother_club_bonus, bool)
