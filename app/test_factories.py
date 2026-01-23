"""Simplified fixture utilities for testing."""

from datetime import date, datetime

from models import Group, Players, User


def create_test_user(db_session, ht_id=12345):
    """Create a test user with minimal required fields."""
    user = User(
        ht_id=ht_id,
        ht_user=f'testuser{ht_id}',
        username=f'testuser{ht_id}',
        password='test_password_hash',
        access_key='test_access_key',
        access_secret='test_access_secret'
    )
    user.role = 'user'
    user.player_columns = '["Name","Age","TSI"]'

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_test_players(db_session, user, count=3):
    """Create test players for a user and return their HT IDs."""
    player_ht_ids = []
    for i in range(count):
        player_data = {
            'ht_id': 10000 + i,
            'first_name': f'TestPlayer{i}',
            'nick_name': '',
            'last_name': f'LastName{i}',
            'number': i + 1,
            'category_id': 1,
            'owner_notes': '',
            'age_years': 20 + i,
            'age_days': 100,
            'age': '20.100',
            'next_birthday': datetime.now(),
            'arrival_date': datetime.now(),
            'form': 7,
            'cards': 0,
            'injury_level': 0,
            'statement': '',
            'language': 'English',
            'language_id': 2,
            'agreeability': 3,
            'aggressiveness': 3,
            'honesty': 3,
            'experience': 2,
            'loyalty': 2,
            'specialty': 0,
            'native_country_id': 1,
            'native_league_id': 1,
            'native_league_name': 'Test League',
            'tsi': 1000 + i,
            'salary': 5000 + i * 100,
            'caps': 0,
            'caps_u20': 0,
            'career_goals': 0,
            'career_hattricks': 0,
            'league_goals': 0,
            'cup_goals': 0,
            'friendly_goals': 0,
            'current_team_matches': 0,
            'current_team_goals': 0,
            'national_team_id': None,
            'national_team_name': None,
            'is_transfer_listed': False,
            'team_id': user.ht_id,
            'stamina': 7,
            'keeper': 1 + i,
            'defender': 2 + i,
            'playmaker': 3 + i,
            'winger': 4 + i,
            'passing': 5 + i,
            'scorer': 6 + i,
            'set_pieces': 2 + i,
            'owner': user.ht_id,
            'old_owner': None,
            'mother_club_bonus': False,
            'leadership': 1,
            'data_date': date.today()  # Required field for Players model
        }
        player_ht_ids.append(player_data['ht_id'])  # Store ID before creating object
        player = Players(player_data)
        db_session.add(player)

    # Commit to make visible to Flask routes
    db_session.commit()

    return player_ht_ids

def create_test_group(db_session, user, name='Test Group'):
    """Create a test player group for a user and return its ID."""
    group = Group(
        user_id=user.ht_id,
        name=name,
        order=1,
        textcolor='#000000',
        bgcolor='#ffffff'
    )

    db_session.add(group)
    db_session.flush()  # Get the ID
    group_id = group.id  # Store ID before commit
    db_session.commit()

    return group_id


def setup_authenticated_session(client, user_or_id, user_ht_user=None):
    """Set up an authenticated session for testing."""
    # Handle both User object and direct ID patterns
    if hasattr(user_or_id, 'ht_id'):
        # User object passed
        user_ht_id = user_or_id.ht_id
        user_ht_user = user_ht_user or user_or_id.ht_user
    else:
        # Direct ID passed (legacy pattern)
        user_ht_id = user_or_id
        user_ht_user = user_ht_user or f'testuser{user_ht_id}'

    with client.session_transaction() as sess:
        sess['current_user'] = user_ht_user
        sess['current_user_id'] = user_ht_id
        sess['all_teams'] = [user_ht_id]  # Use only primitive data types
        sess['all_team_names'] = ['Test Team']
        sess['team_id'] = 12345
    return client
