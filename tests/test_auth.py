"""Test authentication and session management."""



def test_session_structure(client):
    """Test that session has expected structure for authenticated users."""
    with client.session_transaction() as session:
        session['access_key'] = 'test_access_key'
        session['access_secret'] = 'test_access_secret'
        session['current_user'] = 'test_user'
        session['all_teams'] = [12345]
        session['all_team_names'] = ['Test Team']

    # Test that session data persists
    with client.session_transaction() as session:
        assert session.get('access_key') == 'test_access_key'
        assert session.get('access_secret') == 'test_access_secret'
        assert session.get('current_user') == 'test_user'
        assert session.get('all_teams') == [12345]
        assert session.get('all_team_names') == ['Test Team']


def test_multi_team_support(client):
    """Test multi-team session support."""
    with client.session_transaction() as session:
        # Test multiple teams
        session['all_teams'] = [12345, 67890]
        session['all_team_names'] = ['Team One', 'Team Two']

    with client.session_transaction() as session:
        teams = session.get('all_teams')
        names = session.get('all_team_names')

        assert len(teams) == 2
        assert len(names) == 2
        assert teams[0] == 12345
        assert teams[1] == 67890
        assert names[0] == 'Team One'
        assert names[1] == 'Team Two'


def test_session_cleanup(client):
    """Test that sessions can be properly cleared."""
    # Set session data
    with client.session_transaction() as session:
        session['access_key'] = 'test_key'
        session['test_data'] = 'should_be_cleared'

    # Clear session
    with client.session_transaction() as session:
        session.clear()

    # Verify session is empty
    with client.session_transaction() as session:
        assert session.get('access_key') is None
        assert session.get('test_data') is None


def test_authentication_required_decorator_simulation(authenticated_session):
    """Test simulation of authentication-required routes."""
    # This tests our authenticated_session fixture
    with authenticated_session.session_transaction() as session:
        assert session.get('access_key') is not None
        assert session.get('access_secret') is not None
        assert session.get('current_user') is not None


def test_oauth_token_storage(client):
    """Test that OAuth tokens are stored correctly in session."""
    test_access_key = 'test_oauth_access_key_12345'
    test_access_secret = 'test_oauth_access_secret_67890'

    with client.session_transaction() as session:
        session['access_key'] = test_access_key
        session['access_secret'] = test_access_secret

    # Verify tokens are stored correctly
    with client.session_transaction() as session:
        assert session['access_key'] == test_access_key
        assert session['access_secret'] == test_access_secret
        # Tokens should be strings
        assert isinstance(session['access_key'], str)
        assert isinstance(session['access_secret'], str)
