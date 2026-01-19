"""Test CHPP API integration and mocking."""

from tests.mock_chpp import (
    create_mock_chpp_client,
    create_mock_player,
    create_mock_team,
    create_mock_user,
)


def test_mock_chpp_user(_mock_chpp_response):
    """Test CHPP user mock functionality."""
    user = create_mock_user(12345, 'testuser')

    assert user.user_id == 12345
    assert user.loginname == 'testuser'
    assert user.supporter_tier == 'none'

    # Test dict-like access
    assert user['user_id'] == 12345
    assert user['loginname'] == 'testuser'


def test_mock_chpp_team():
    """Test CHPP team mock functionality."""
    team = create_mock_team(54321, 'Test Team FC')

    assert team.team_id == 54321
    assert team.team_name == 'Test Team FC'
    assert team.short_team_name == 'Test'
    assert isinstance(team.players, list)


def test_mock_chpp_player(sample_player_data):
    """Test CHPP player mock functionality."""
    player = create_mock_player(**sample_player_data)

    assert player.ht_id == sample_player_data['ht_id']
    assert player.first_name == sample_player_data['first_name']
    assert player.nick_name == sample_player_data['nick_name']
    assert player.age == sample_player_data['age']

    # Test skills
    assert player.keeper == sample_player_data['keeper']
    assert player.defender == sample_player_data['defender']
    assert player.scorer == sample_player_data['scorer']

    # Test dict-like access
    assert player['first_name'] == sample_player_data['first_name']
    assert player['keeper'] == sample_player_data['keeper']


def test_mock_chpp_client():
    """Test CHPP client mock functionality."""
    chpp = create_mock_chpp_client()

    # Test user access
    user = chpp.user()
    assert user.user_id == 12345
    assert user.loginname == 'testuser'

    # Test team access
    team = chpp.team()
    assert team.team_id == 54321
    assert team.team_name == 'Test Team'

    # Test teams list
    teams = chpp.teams()
    assert len(teams) == 1
    assert teams[0].team_id == 54321


def test_mock_chpp_client_custom_data():
    """Test CHPP client with custom mock data."""
    custom_user = create_mock_user(99999, 'customuser')
    custom_player = create_mock_player(player_id=888888, first_name='Custom', scorer=15)
    custom_team = create_mock_team(77777, 'Custom Team', [custom_player])

    chpp = create_mock_chpp_client(
        user=custom_user,
        teams=[custom_team],
        players=[custom_player]
    )

    # Test custom user
    user = chpp.user()
    assert user.user_id == 99999
    assert user.loginname == 'customuser'

    # Test custom team
    team = chpp.team()
    assert team.team_id == 77777
    assert team.team_name == 'Custom Team'

    # Test custom player
    assert len(team.players) == 1
    player = team.players[0]
    assert player.player_id == 888888
    assert player.first_name == 'Custom'
    assert player.scorer == 15


def test_mock_chpp_team_by_id():
    """Test accessing team by specific ID."""
    team1 = create_mock_team(11111, 'Team One')
    team2 = create_mock_team(22222, 'Team Two')

    chpp = create_mock_chpp_client(teams=[team1, team2])

    # Test getting specific team by ID
    found_team = chpp.team(ht_id=22222)
    assert found_team.team_id == 22222
    assert found_team.team_name == 'Team Two'

    # Test getting team that doesn't exist
    not_found = chpp.team(ht_id=99999)
    assert not_found is None or not_found.team_id != 99999


def test_player_skill_calculations_data_structure():
    """Test that mock player data structure supports skill calculations."""
    player = create_mock_player(
        player_id=123456,
        keeper=8,
        defender=12,
        playmaker=10,
        winger=6,
        passing=9,
        scorer=15,
        set_pieces=7,
        experience=8,
        loyalty=9,
        form=7,
        stamina=9
    )

    # Test that all skill calculation attributes are available
    skills = ['keeper', 'defender', 'playmaker', 'winger', 'passing', 'scorer', 'set_pieces']
    for skill in skills:
        assert hasattr(player, skill)
        assert isinstance(getattr(player, skill), int)
        assert getattr(player, skill) > 0

    # Test additional calculation attributes
    calc_attrs = ['experience', 'loyalty', 'form', 'stamina']
    for attr in calc_attrs:
        assert hasattr(player, attr)
        assert isinstance(getattr(player, attr), int)
