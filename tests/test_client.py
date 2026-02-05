"""Tests for app/chpp/client.py"""

import xml.etree.ElementTree as ET
from unittest.mock import patch

from app.chpp.client import CHPP


def test_module_imports():
    """Test that CHPP client module imports without errors."""
    import app.chpp.client
    assert app.chpp.client is not None


class TestCHPPClient:
    """Test CHPP client functionality."""

    def test_matches_endpoint(self):
        """Test matches endpoint call."""
        # Create mock XML response
        xml_response = '''<?xml version="1.0" encoding="UTF-8"?>
        <HattrickData>
            <Team>
                <TeamID>1001</TeamID>
                <TeamName>Test Team</TeamName>
                <MatchList>
                    <Match>
                        <MatchID>12345</MatchID>
                        <MatchDate>2024-01-15 14:30:00</MatchDate>
                        <HomeTeamID>1001</HomeTeamID>
                        <HomeTeamName>Home FC</HomeTeamName>
                        <AwayTeamID>1002</AwayTeamID>
                        <AwayTeamName>Away FC</AwayTeamName>
                        <HomeGoals>2</HomeGoals>
                        <AwayGoals>1</AwayGoals>
                        <MatchType>1</MatchType>
                        <MatchContextId>5001</MatchContextId>
                        <MatchRuleId>0</MatchRuleId>
                        <CupLevel>0</CupLevel>
                        <CupLevelIndex>0</CupLevelIndex>
                    </Match>
                </MatchList>
            </Team>
        </HattrickData>'''

        # Create CHPP client
        client = CHPP("test_key", "test_secret", "access_key", "access_secret")

        # Mock the request method
        with patch.object(client, 'request') as mock_request:
            mock_request.return_value = ET.fromstring(xml_response)

            # Test matches method
            matches = client.matches(id_=1001, is_youth=False)

            # Verify request was made with correct parameters
            mock_request.assert_called_once_with("matches", "2.6", teamID=1001, isYouth=False)

            # Verify returned data
            assert len(matches) == 1
            assert matches[0].ht_id == 12345
            assert matches[0].home_team_name == "Home FC"
            assert matches[0].away_team_name == "Away FC"
            assert matches[0].home_goals == 2
            assert matches[0].away_goals == 1

    def test_matches_archive_endpoint(self):
        """Test matches_archive endpoint call."""
        # Create CHPP client
        client = CHPP("test_key", "test_secret", "access_key", "access_secret")

        # Mock the request method
        with patch.object(client, 'request') as mock_request:
            mock_request.return_value = ET.fromstring('<HattrickData><Team><MatchList></MatchList></Team></HattrickData>')

            # Test matches_archive method
            matches = client.matches_archive(id_=1001, is_youth=False)

            # Verify request was made with correct parameters
            mock_request.assert_called_once_with("matchesarchive", "1.5", teamID=1001, isYouthTeam=False)

            # Verify returned data structure
            assert isinstance(matches, list)


# TODO: Add comprehensive tests for CHPP client
# TODO: Test CHPP API authentication
# TODO: Test API request methods and responses
# TODO: Test error handling for API failures
# TODO: Test rate limiting and retry logic
# TODO: Test data parsing and transformation
