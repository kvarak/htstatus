"""Tests for formation utilities in utils module."""

from unittest.mock import Mock

from app.utils import (
    FORMATION_TEMPLATES,
    calculate_formation_effectiveness,
    get_formation_list,
)


class TestFormationTemplates:
    """Test formation template data structure."""

    def test_formation_templates_exist(self):
        """Test that formation templates are available."""
        assert FORMATION_TEMPLATES is not None
        assert len(FORMATION_TEMPLATES) == 10

    def test_all_formations_present(self):
        """Test that all expected formations are defined."""
        expected_formations = [
            "5-5-0", "5-4-1", "5-3-2", "5-2-3", "4-5-1",
            "4-4-2", "4-3-3", "3-5-2", "3-4-3", "2-5-3"
        ]
        for formation in expected_formations:
            assert formation in FORMATION_TEMPLATES

    def test_formation_structure(self):
        """Test that each formation has required structure."""
        for _formation_key, formation in FORMATION_TEMPLATES.items():
            assert "name" in formation
            assert "description" in formation
            assert "positions" in formation
            assert isinstance(formation["positions"], dict)

            # Each position should have row, col, name
            for position_id, position_data in formation["positions"].items():
                assert "row" in position_data
                assert "col" in position_data
                assert "name" in position_data
                assert isinstance(position_id, int)
                assert position_data["row"] in [1, 2, 3, 4]
                assert position_data["col"] in [1, 2, 3, 4, 5]

    def test_formation_positions_count(self):
        """Test that all formations have exactly 11 positions."""
        for formation in FORMATION_TEMPLATES.values():
            assert len(formation["positions"]) == 11

    def test_formation_includes_goalkeeper(self):
        """Test that all formations include a goalkeeper (position 100)."""
        for formation in FORMATION_TEMPLATES.values():
            assert 100 in formation["positions"]
            assert formation["positions"][100]["row"] == 1  # GK always in row 1


class TestGetFormationList:
    """Test formation list utility function."""

    def test_get_formation_list_returns_list(self):
        """Test that get_formation_list returns a list."""
        result = get_formation_list()
        assert isinstance(result, list)
        assert len(result) == 10

    def test_formation_list_structure(self):
        """Test that formation list items have required structure."""
        result = get_formation_list()
        for item in result:
            assert "key" in item
            assert "name" in item
            assert "description" in item
            assert item["key"] in FORMATION_TEMPLATES


class TestCalculateFormationEffectiveness:
    """Test formation effectiveness calculation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_player = Mock()
        self.mock_player.ht_id = 12345
        self.mock_player.first_name = "Test"
        self.mock_player.last_name = "Player"
        # Configure mock skill attributes
        self.mock_player.keeper = 10
        self.mock_player.defender = 10
        self.mock_player.playmaker = 10
        self.mock_player.winger = 5
        self.mock_player.passing = 5
        self.mock_player.scorer = 5
        self.mock_player.set_pieces = 5

    def test_calculate_formation_effectiveness_invalid_formation(self):
        """Test with invalid formation key."""
        result = calculate_formation_effectiveness("invalid", {})
        assert "error" in result
        assert result["total_score"] == 0

    def test_calculate_formation_effectiveness_empty_assignments(self):
        """Test with valid formation but no player assignments."""
        result = calculate_formation_effectiveness("4-4-2", {})
        assert "total_score" in result
        assert "average_score" in result
        assert "position_scores" in result
        assert "formation_name" in result
        assert result["total_score"] == 0
        assert result["average_score"] == 0
        assert len(result["position_scores"]) == 11

    def test_calculate_formation_effectiveness_with_players(self):
        """Test with player assignments."""
        # Mock calculateContribution to return a predictable value
        import app.utils
        original_calc = app.utils.calculateContribution
        app.utils.calculateContribution = Mock(return_value=8.5)

        try:
            player_assignments = {
                100: self.mock_player,  # Goalkeeper
                101: self.mock_player,  # Right back
            }

            result = calculate_formation_effectiveness("4-4-2", player_assignments)

            assert result["total_score"] == 17.0  # 2 players * 8.5 each
            assert result["average_score"] == round(17.0 / 11, 2)  # Total / 11 positions
            assert len(result["position_scores"]) == 11
            assert result["formation_name"] == FORMATION_TEMPLATES["4-4-2"]["name"]

            # Check assigned positions have player data
            assert result["position_scores"][100]["contribution"] == 8.5
            assert "Test Player" in result["position_scores"][100]["player_name"]

            # Check unassigned positions
            assert result["position_scores"][102]["contribution"] == 0
            assert result["position_scores"][102]["player_name"] == "No player assigned"

        finally:
            app.utils.calculateContribution = original_calc

    def test_calculate_formation_effectiveness_all_positions(self):
        """Test with all positions assigned."""
        import app.utils
        original_calc = app.utils.calculateContribution
        app.utils.calculateContribution = Mock(return_value=7.2)

        try:
            formation = FORMATION_TEMPLATES["4-4-2"]
            player_assignments = {}

            # Assign mock player to all positions
            for position_id in formation["positions"]:
                player_assignments[position_id] = self.mock_player

            result = calculate_formation_effectiveness("4-4-2", player_assignments)

            expected_total = 7.2 * 11  # 11 positions * 7.2 each
            assert result["total_score"] == expected_total
            assert result["average_score"] == 7.2

            # All positions should have contributions
            for position_scores in result["position_scores"].values():
                assert position_scores["contribution"] == 7.2
                assert "Test Player" in position_scores["player_name"]

        finally:
            app.utils.calculateContribution = original_calc


class TestFormationTemplateDetails:
    """Test specific formation template details."""

    def test_4_4_2_formation_structure(self):
        """Test the classic 4-4-2 formation structure."""
        formation = FORMATION_TEMPLATES["4-4-2"]

        assert formation["name"] == "4-4-2 (Classic)"
        assert "4 defenders, 4 midfielders, 2 forwards" in formation["description"]

        positions = formation["positions"]
        # Should have goalkeeper + 4 defenders + 4 midfielders + 2 forwards
        assert 100 in positions  # Goalkeeper

        # Defenders: RB, RCB, LCB, LB
        defenders = [101, 102, 104, 105]
        for pos in defenders:
            assert pos in positions
            assert positions[pos]["row"] == 2

        # Midfielders: RIM, CM, LIM, LM
        midfielders = [107, 108, 109, 110]
        for pos in midfielders:
            assert pos in positions
            assert positions[pos]["row"] == 3

        # Forwards: RF, LF
        forwards = [111, 113]
        for pos in forwards:
            assert pos in positions
            assert positions[pos]["row"] == 4

    def test_5_5_0_formation_structure(self):
        """Test the defensive 5-5-0 formation structure."""
        formation = FORMATION_TEMPLATES["5-5-0"]

        assert formation["name"] == "5-5-0 (Defensive)"

        positions = formation["positions"]

        # Should have 5 defenders (row 2) and 5 midfielders (row 3)
        defenders = [pos for pos, data in positions.items() if data["row"] == 2]
        midfielders = [pos for pos, data in positions.items() if data["row"] == 3]
        forwards = [pos for pos, data in positions.items() if data["row"] == 4]

        assert len(defenders) == 5
        assert len(midfielders) == 5
        assert len(forwards) == 0  # No forwards in 5-5-0

    def test_formation_position_uniqueness(self):
        """Test that each formation has unique grid positions."""
        for formation_key, formation in FORMATION_TEMPLATES.items():
            grid_positions = set()

            for position_data in formation["positions"].values():
                grid_pos = (position_data["row"], position_data["col"])
                assert grid_pos not in grid_positions, f"Duplicate grid position in {formation_key}: {grid_pos}"
                grid_positions.add(grid_pos)
