"""Essential CHPP model integration tests.

Focuses on critical functionality: YouthTeamId handling, field mappings, dict access.
Tests the fixes applied from real API documentation analysis.
"""

import pytest

from app.chpp.models import CHPPUser, CHPPTeam, CHPPPlayer


class TestCHPPEssentials:
    """Critical CHPP functionality tests only."""

    def test_youth_team_id_bug_fix(self):
        """YouthTeamId None handling - the key bug this work fixed."""
        user = CHPPUser(
            ht_id=123456,
            username="testuser",
            _teams_ht_id=[456789],
            youth_team_id=None,  # This was crashing before
            _SOURCE_FILE="managercompendium"
        )

        assert user.youth_team_id is None
        assert user['ht_id'] == 123456  # Dict access works
        assert 456789 in user._teams_ht_id

    def test_corrected_field_names(self):
        """Verify field name corrections from real API docs work."""
        player = CHPPPlayer(
            player_id=1001,     # PlayerID not PlayerId
            first_name="Test",
            last_name="Player",
            nick_name=None,
            age=24,
            age_days=150,
            tsi=1500,
            player_number=7,
            form=6,
            stamina=5,          # Stamina not StaminaSkill
            experience=4,
            loyalty=8,
            keeper=5,           # Keeper not KeeperSkill
            defender=8,
            playmaker=6,
            winger=4,
            passing=7,
            scorer=3,
            set_pieces=2,       # SetPieces not SetPiecesSkill
            _SOURCE_FILE="players"
        )

        assert player.player_id == 1001
        assert player.keeper == 5
        assert player.stamina == 5
        assert player.set_pieces == 2
        assert player['keeper'] == 5  # Dict interface
        assert player.set_pieces == 2
        assert player['keeper'] == 5  # Dict interface

    def test_team_player_integration(self):
        """Basic team-player relationship works."""
        team = CHPPTeam(
            team_id=456789,
            name="Test FC",
            short_team_name="Test",
            _SOURCE_FILE="teamdetails"
        )

        assert team['team_id'] == 456789
        assert team.players() == []  # Empty initially