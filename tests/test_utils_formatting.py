#!/usr/bin/env python3
"""Additional utility function tests for better coverage."""

import unittest
from unittest.mock import Mock, patch

from app import utils


class TestFormattingUtilities(unittest.TestCase):
    """Test formatting and calculation utility functions."""

    def test_format_attribute_name_basic(self):
        """Test basic attribute name formatting."""
        assert utils._format_attribute_name("first_name") == "First Name"
        assert utils._format_attribute_name("last_name") == "Last Name"
        assert utils._format_attribute_name("player_id") == "Player Id"

    def test_format_attribute_name_special_cases(self):
        """Test special case attribute formatting."""
        assert utils._format_attribute_name("tsi") == "TSI"
        assert utils._format_attribute_name("set_pieces") == "Set Pieces"

    def test_format_attribute_name_single_word(self):
        """Test single word attribute formatting."""
        assert utils._format_attribute_name("keeper") == "Keeper"
        assert utils._format_attribute_name("defender") == "Defender"
        assert utils._format_attribute_name("winger") == "Winger"

    def test_format_attribute_name_already_formatted(self):
        """Test already formatted attribute names."""
        assert utils._format_attribute_name("Experience") == "Experience"
        assert utils._format_attribute_name("Form") == "Form"

    @patch('app.utils.dprint')
    def test_calculate_manmark_basic(self, mock_dprint):
        """Test basic manmark calculation."""
        # Mock player with object attributes
        player = Mock()
        player.experience = 10
        player.defender = 8

        result = utils.calculateManmark(player)

        # Expected: (8 + (10/5) * 0.3) * 0.95 = (8 + 0.6) * 0.95 = 8.17
        expected = round((8 + 2.0 * 0.3) * 0.95, 2)
        assert result == expected

    @patch('app.utils.dprint')
    def test_calculate_manmark_dictionary_input(self, mock_dprint):
        """Test manmark calculation with dictionary input."""
        player = {
            "experience": 15,
            "defender": 12
        }

        result = utils.calculateManmark(player)

        # Expected: (12 + (15/5) * 0.3) * 0.95 = (12 + 0.9) * 0.95 = 12.26
        expected = round((12 + 3.0 * 0.3) * 0.95, 2)
        assert result == expected

    @patch('app.utils.dprint')
    def test_calculate_manmark_none_values(self, mock_dprint):
        """Test manmark calculation with None values."""
        player = Mock()
        player.experience = None
        player.defender = None

        result = utils.calculateManmark(player)

        # Expected: (0 + 0 * 0.3) * 0.95 = 0.0
        assert result == 0.0

    @patch('app.utils.dprint')
    def test_calculate_manmark_high_experience(self, mock_dprint):
        """Test manmark calculation with high experience (should cap at 20)."""
        player = Mock()
        player.experience = 120  # Should be capped at 20 for calculation
        player.defender = 10

        result = utils.calculateManmark(player)

        # Expected: (10 + 20 * 0.3) * 0.95 = (10 + 6) * 0.95 = 15.2
        expected = round((10 + 20 * 0.3) * 0.95, 2)
        assert result == expected

    @patch('app.utils.dprint')
    def test_calculate_manmark_missing_attributes(self, mock_dprint):
        """Test manmark calculation with missing attributes."""
        player = {}  # Empty dictionary

        result = utils.calculateManmark(player)

        # Should default to 0 values: (0 + 0 * 0.3) * 0.95 = 0.0
        assert result == 0.0

    def test_calculate_manmark_edge_case_zero_defender(self):
        """Test manmark calculation with zero defender skill."""
        player = Mock()
        player.experience = 5
        player.defender = 0

        result = utils.calculateManmark(player)

        # Expected: (0 + (5/5) * 0.3) * 0.95 = (0 + 0.3) * 0.95 = 0.29
        expected = round((0 + 1.0 * 0.3) * 0.95, 2)
        assert result == expected

    def test_calculate_manmark_negative_values_protection(self):
        """Test manmark calculation protects against negative results."""
        player = Mock()
        player.experience = 0
        player.defender = -5  # Negative defender value

        result = utils.calculateManmark(player)

        # Should be max(0, negative_result) = 0.0
        assert result == 0.0


if __name__ == '__main__':
    unittest.main()
