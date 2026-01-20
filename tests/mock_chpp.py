"""Mock CHPP API responses for testing."""

class MockCHPPUser:
    """Mock CHPP User object."""

    def __init__(self, user_id=12345, loginname='testuser'):
        self.user_id = user_id
        self.loginname = loginname
        self.supporter_tier = 'none'
        self._SOURCE_FILE = 'managercompendium'  # Expected by team route
        self._teams_ht_id = [54321]  # List of team IDs this user manages

    def __getitem__(self, key):
        """Allow dict-like access for backward compatibility."""
        return getattr(self, key, None)


class MockCHPPTeam:
    """Mock CHPP Team object."""

    def __init__(self, team_id=54321, team_name='Test Team'):
        self.team_id = team_id
        self.team_name = team_name
        self.name = team_name  # Expected by team route
        self.short_team_name = team_name.split()[0]
        self.players = []

    def __getitem__(self, key):
        """Allow dict-like access for backward compatibility."""
        return getattr(self, key, None)


class MockCHPPPlayer:
    """Mock CHPP Player object."""

    def __init__(self, player_id=123456, **kwargs):
        # Basic info
        self.player_id = player_id
        self.ht_id = player_id
        self.first_name = kwargs.get('first_name', 'Test')
        self.nick_name = kwargs.get('nick_name', 'TestPlayer')
        self.last_name = kwargs.get('last_name', 'Player')
        self.age = kwargs.get('age', 25)

        # Skills
        self.keeper = kwargs.get('keeper', 5)
        self.defender = kwargs.get('defender', 8)
        self.playmaker = kwargs.get('playmaker', 6)
        self.winger = kwargs.get('winger', 7)
        self.passing = kwargs.get('passing', 6)
        self.scorer = kwargs.get('scorer', 9)
        self.set_pieces = kwargs.get('set_pieces', 4)

        # Additional attributes
        self.experience = kwargs.get('experience', 7)
        self.loyalty = kwargs.get('loyalty', 8)
        self.form = kwargs.get('form', 6)
        self.stamina = kwargs.get('stamina', 8)

    def __getitem__(self, key):
        """Allow dict-like access for backward compatibility."""
        return getattr(self, key, None)


class MockCHPP:
    """Mock CHPP API client for testing."""

    def __init__(self, consumer_key=None, consumer_secret=None,
                 access_key=None, access_secret=None):
        self.consumer_key = consumer_key or 'test_consumer'
        self.consumer_secret = consumer_secret or 'test_secret'
        self.access_key = access_key or 'test_access'
        self.access_secret = access_secret or 'test_access_secret'

        # Default mock data
        self._mock_user = MockCHPPUser()
        self._mock_teams = [MockCHPPTeam()]
        self._mock_players = [MockCHPPPlayer()]

        # Add players to team
        self._mock_teams[0].players = self._mock_players

    def user(self):
        """Return mock user object."""
        return self._mock_user

    def team(self, ht_id=None):
        """Return mock team object."""
        if ht_id:
            # Find team by ID or return first team
            for team in self._mock_teams:
                if team.team_id == ht_id:
                    return team
        return self._mock_teams[0] if self._mock_teams else None

    def teams(self):
        """Return list of mock teams."""
        return self._mock_teams

    def set_mock_user(self, user):
        """Set custom mock user for testing."""
        self._mock_user = user

    def set_mock_teams(self, teams):
        """Set custom mock teams for testing."""
        self._mock_teams = teams

    def set_mock_players(self, players):
        """Set custom mock players for testing."""
        self._mock_players = players
        # Update first team's players
        if self._mock_teams:
            self._mock_teams[0].players = players


# Factory functions for creating test data
def create_mock_player(**kwargs):
    """Create a mock player with specified attributes."""
    return MockCHPPPlayer(**kwargs)


def create_mock_team(team_id=54321, team_name='Test Team', players=None):
    """Create a mock team with optional players."""
    team = MockCHPPTeam(team_id, team_name)
    if players:
        team.players = players
    return team


def create_mock_user(user_id=12345, loginname='testuser'):
    """Create a mock user."""
    return MockCHPPUser(user_id, loginname)


def create_mock_chpp_client(**kwargs):
    """Create a mock CHPP client with optional custom data."""
    chpp = MockCHPP()

    if 'user' in kwargs:
        chpp.set_mock_user(kwargs['user'])

    if 'teams' in kwargs:
        chpp.set_mock_teams(kwargs['teams'])

    if 'players' in kwargs:
        chpp.set_mock_players(kwargs['players'])

    return chpp
