"""Test business logic and calculations for HTStatus application."""

import time
from datetime import datetime, timedelta

import pytest

from models import Players, Match, MatchPlay, User


class TestPlayerBusinessLogic:
    """Test business logic related to player management and calculations."""

    def test_player_age_calculations(self, app, db_session):
        """Test player age-related calculations."""
        with app.app_context():
            # Test young player
            young_player_data = {
                'ht_id': 501001,
                'first_name': 'Young',
                'nick_name': 'Player',
                'last_name': 'One',
                'number': 1,
                'category_id': 0,
                'owner_notes': '',
                'age_years': 17,
                'age_days': 45,
                'age': '17.45',
                'next_birthday': datetime.now() + timedelta(days=320),
                'arrival_date': datetime.now() - timedelta(days=100),
                'form': 6,
                'cards': 0,
                'injury_level': 0,
                'statement': '',
                'language': 'English',
                'language_id': 2,
                'agreeability': 6,
                'aggressiveness': 4,
                'honesty': 7,
                'experience': 2,  # Low experience for young player
                'loyalty': 8,
                'specialty': 0,
                'native_country_id': 5,
                'native_league_id': 1,
                'native_league_name': 'England',
                'tsi': 800,  # Low TSI for young player
                'salary': 3000,
                'caps': 0,
                'caps_u20': 0,
                'career_goals': 0,
                'career_hattricks': 0,
                'league_goals': 0,
                'cup_goals': 0,
                'friendly_goals': 0,
                'current_team_matches': 5,
                'current_team_goals': 0,
                'national_team_id': 0,
                'national_team_name': '',
                'is_transfer_listed': False,
                'team_id': 40001,
                'stamina': 6,
                'keeper': 5,
                'defender': 6,
                'playmaker': 4,
                'winger': 5,
                'passing': 4,
                'scorer': 5,
                'set_pieces': 3,
                'owner': 12345,
                'mother_club_bonus': True,  # Often true for young players
                'leadership': 2  # Low leadership for young player
            }
            
            # Test veteran player
            veteran_player_data = {
                'ht_id': 501002,
                'first_name': 'Veteran',
                'nick_name': 'Player',
                'last_name': 'Two',
                'number': 2,
                'category_id': 0,
                'owner_notes': '',
                'age_years': 34,
                'age_days': 15,
                'age': '34.15',
                'next_birthday': datetime.now() + timedelta(days=350),
                'arrival_date': datetime.now() - timedelta(days=2500),
                'form': 7,
                'cards': 2,
                'injury_level': 0,
                'statement': '',
                'language': 'Italian',
                'language_id': 5,
                'agreeability': 7,
                'aggressiveness': 6,
                'honesty': 8,
                'experience': 9,  # High experience for veteran
                'loyalty': 9,
                'specialty': 2,
                'native_country_id': 20,
                'native_league_id': 8,
                'native_league_name': 'Italy',
                'tsi': 4500,  # High TSI for experienced player
                'salary': 45000,
                'caps': 25,
                'caps_u20': 18,
                'career_goals': 89,
                'career_hattricks': 8,
                'league_goals': 65,
                'cup_goals': 15,
                'friendly_goals': 9,
                'current_team_matches': 180,
                'current_team_goals': 65,
                'national_team_id': 3020,
                'national_team_name': 'Italy',
                'is_transfer_listed': False,
                'team_id': 40001,
                'stamina': 7,  # Still good stamina
                'keeper': 4,
                'defender': 7,
                'playmaker': 8,
                'winger': 6,
                'passing': 8,
                'scorer': 9,  # Peak scoring ability
                'set_pieces': 8,
                'owner': 12345,
                'mother_club_bonus': False,
                'leadership': 8  # High leadership for veteran
            }
            
            young_player = Players(young_player_data)
            veteran_player = Players(veteran_player_data)
            db_session.add(young_player)
            db_session.add(veteran_player)
            db_session.commit()
            
            # Test age-related business logic
            assert young_player.age_years < 18  # Youth player
            assert veteran_player.age_years > 30  # Veteran
            
            # Test experience correlation with age
            assert young_player.experience < veteran_player.experience
            
            # Test leadership correlation with age/experience
            assert young_player.leadership < veteran_player.leadership
            
            # Test TSI correlation with experience
            assert young_player.tsi < veteran_player.tsi

    def test_player_skill_combinations(self, app, db_session):
        """Test business logic for different player skill combinations."""
        with app.app_context():
            # Goalkeeper profile
            goalkeeper_data = {
                'ht_id': 502001,
                'first_name': 'Goal',
                'nick_name': 'Keeper',
                'last_name': 'One',
                'number': 1,
                'category_id': 0,
                'owner_notes': '',
                'age_years': 26,
                'age_days': 0,
                'age': '26.0',
                'next_birthday': datetime.now() + timedelta(days=365),
                'arrival_date': datetime.now() - timedelta(days=365),
                'form': 7,
                'cards': 0,
                'injury_level': 0,
                'statement': '',
                'language': 'German',
                'language_id': 4,
                'agreeability': 7,
                'aggressiveness': 5,
                'honesty': 8,
                'experience': 6,
                'loyalty': 7,
                'specialty': 1,  # Quick goalkeeper specialty
                'native_country_id': 10,
                'native_league_id': 3,
                'native_league_name': 'Germany',
                'tsi': 3200,
                'salary': 25000,
                'caps': 5,
                'caps_u20': 8,
                'career_goals': 0,  # Goalkeepers rarely score
                'career_hattricks': 0,
                'league_goals': 0,
                'cup_goals': 0,
                'friendly_goals': 0,
                'current_team_matches': 45,
                'current_team_goals': 0,
                'national_team_id': 3010,
                'national_team_name': 'Germany',
                'is_transfer_listed': False,
                'team_id': 40002,
                'stamina': 7,
                'keeper': 10,  # Excellent goalkeeper skill
                'defender': 4,  # Low outfield skills for keeper
                'playmaker': 3,
                'winger': 3,
                'passing': 4,
                'scorer': 3,
                'set_pieces': 5,
                'owner': 12345,
                'mother_club_bonus': False,
                'leadership': 7
            }
            
            # Striker profile
            striker_data = {
                'ht_id': 502002,
                'first_name': 'Goal',
                'nick_name': 'Scorer',
                'last_name': 'Two',
                'number': 9,
                'category_id': 0,
                'owner_notes': '',
                'age_years': 25,
                'age_days': 100,
                'age': '25.100',
                'next_birthday': datetime.now() + timedelta(days=265),
                'arrival_date': datetime.now() - timedelta(days=800),
                'form': 8,
                'cards': 1,
                'injury_level': 0,
                'statement': '',
                'language': 'Brazilian',
                'language_id': 6,
                'agreeability': 6,
                'aggressiveness': 7,
                'honesty': 6,
                'experience': 7,
                'loyalty': 6,
                'specialty': 3,  # Head specialty
                'native_country_id': 25,
                'native_league_id': 10,
                'native_league_name': 'Brazil',
                'tsi': 3800,
                'salary': 35000,
                'caps': 12,
                'caps_u20': 15,
                'career_goals': 45,  # Many goals for striker
                'career_hattricks': 4,
                'league_goals': 32,
                'cup_goals': 8,
                'friendly_goals': 5,
                'current_team_matches': 60,
                'current_team_goals': 32,
                'national_team_id': 3025,
                'national_team_name': 'Brazil',
                'is_transfer_listed': False,
                'team_id': 40002,
                'stamina': 8,
                'keeper': 3,  # Low goalkeeper skill for outfield player
                'defender': 5,
                'playmaker': 6,
                'winger': 7,
                'passing': 6,
                'scorer': 10,  # Excellent scoring skill
                'set_pieces': 6,
                'owner': 12345,
                'mother_club_bonus': False,
                'leadership': 6
            }
            
            goalkeeper = Players(goalkeeper_data)
            striker = Players(striker_data)
            db_session.add(goalkeeper)
            db_session.add(striker)
            db_session.commit()
            
            # Test position-specific skill expectations
            assert goalkeeper.keeper > striker.keeper  # Keeper should have better keeper skill
            assert striker.scorer > goalkeeper.scorer  # Striker should have better scoring
            
            # Test goal statistics alignment with position
            assert goalkeeper.career_goals == 0  # Goalkeepers rarely score
            assert striker.career_goals > 0  # Strikers should have goals
            
            # Test position-appropriate specialties
            assert goalkeeper.specialty == 1  # Quick specialty for goalkeeper
            assert striker.specialty == 3  # Head specialty for striker

    def test_player_value_calculations(self, app, db_session):
        """Test business logic for player value and salary calculations."""
        with app.app_context():
            # High-value player
            star_player_data = {
                'ht_id': 503001,
                'first_name': 'Star',
                'nick_name': 'Player',
                'last_name': 'One',
                'number': 10,
                'category_id': 0,
                'owner_notes': '',
                'age_years': 23,
                'age_days': 200,
                'age': '23.200',
                'next_birthday': datetime.now() + timedelta(days=165),
                'arrival_date': datetime.now() - timedelta(days=400),
                'form': 8,
                'cards': 0,
                'injury_level': 0,
                'statement': '',
                'language': 'English',
                'language_id': 2,
                'agreeability': 7,
                'aggressiveness': 6,
                'honesty': 8,
                'experience': 6,
                'loyalty': 7,
                'specialty': 4,  # Unpredictable specialty
                'native_country_id': 5,
                'native_league_id': 1,
                'native_league_name': 'England',
                'tsi': 6500,  # Very high TSI
                'salary': 65000,  # High salary matching TSI
                'caps': 8,
                'caps_u20': 12,
                'career_goals': 28,
                'career_hattricks': 3,
                'league_goals': 20,
                'cup_goals': 5,
                'friendly_goals': 3,
                'current_team_matches': 35,
                'current_team_goals': 20,
                'national_team_id': 3005,
                'national_team_name': 'England',
                'is_transfer_listed': False,
                'team_id': 40003,
                'stamina': 9,  # Excellent stats across the board
                'keeper': 4,
                'defender': 8,
                'playmaker': 9,
                'winger': 8,
                'passing': 8,
                'scorer': 9,
                'set_pieces': 7,
                'owner': 12345,
                'mother_club_bonus': False,
                'leadership': 7
            }
            
            # Budget player
            budget_player_data = {
                'ht_id': 503002,
                'first_name': 'Budget',
                'nick_name': 'Player',
                'last_name': 'Two',
                'number': 15,
                'category_id': 0,
                'owner_notes': '',
                'age_years': 29,
                'age_days': 50,
                'age': '29.50',
                'next_birthday': datetime.now() + timedelta(days=315),
                'arrival_date': datetime.now() - timedelta(days=1200),
                'form': 5,
                'cards': 3,
                'injury_level': 1,  # Minor injury
                'statement': '',
                'language': 'Polish',
                'language_id': 7,
                'agreeability': 5,
                'aggressiveness': 6,
                'honesty': 6,
                'experience': 5,
                'loyalty': 8,
                'specialty': 0,  # No specialty
                'native_country_id': 30,
                'native_league_id': 12,
                'native_league_name': 'Poland',
                'tsi': 1200,  # Low TSI
                'salary': 8000,  # Low salary matching TSI
                'caps': 0,
                'caps_u20': 2,
                'career_goals': 8,
                'career_hattricks': 0,
                'league_goals': 6,
                'cup_goals': 1,
                'friendly_goals': 1,
                'current_team_matches': 25,
                'current_team_goals': 6,
                'national_team_id': 0,
                'national_team_name': '',
                'is_transfer_listed': True,  # On transfer list
                'team_id': 40003,
                'stamina': 6,  # Average stats
                'keeper': 4,
                'defender': 6,
                'playmaker': 5,
                'winger': 5,
                'passing': 5,
                'scorer': 6,
                'set_pieces': 4,
                'owner': 12345,
                'mother_club_bonus': False,
                'leadership': 4
            }
            
            star_player = Players(star_player_data)
            budget_player = Players(budget_player_data)
            db_session.add(star_player)
            db_session.add(budget_player)
            db_session.commit()
            
            # Test value correlations
            assert star_player.tsi > budget_player.tsi * 3  # Star player much higher TSI
            assert star_player.salary > budget_player.salary * 5  # Higher salary for better player
            
            # Test skill quality differences
            assert star_player.playmaker > budget_player.playmaker
            assert star_player.scorer > budget_player.scorer
            assert star_player.stamina > budget_player.stamina
            
            # Test transfer list status impact
            assert not star_player.is_transfer_listed  # Star players not usually for sale
            assert budget_player.is_transfer_listed  # Budget players more likely for sale
            
            # Test injury status impact
            assert star_player.injury_level == 0  # Star players better maintained
            assert budget_player.injury_level > 0  # Budget players may have issues


class TestMatchBusinessLogic:
    """Test business logic related to match management and statistics."""

    def test_match_result_analysis(self, app, db_session):
        """Test match result calculation and analysis."""
        with app.app_context():
            # Home win match
            home_win_data = {
                'ht_id': 601001,
                'home_team_id': 50001,
                'home_team_name': 'Home Winners FC',
                'away_team_id': 50002,
                'away_team_name': 'Away Losers United',
                'datetime': datetime.now() - timedelta(days=7),
                'matchtype': 1,  # League match
                'context_id': 0,
                'rule_id': 0,
                'cup_level': 0,
                'cup_level_index': 0,
                'home_goals': 3,
                'away_goals': 1
            }
            
            # Away win match
            away_win_data = {
                'ht_id': 601002,
                'home_team_id': 50002,
                'home_team_name': 'Home Losers FC',
                'away_team_id': 50001,
                'away_team_name': 'Away Winners United',
                'datetime': datetime.now() - timedelta(days=3),
                'matchtype': 1,  # League match
                'context_id': 0,
                'rule_id': 0,
                'cup_level': 0,
                'cup_level_index': 0,
                'home_goals': 0,
                'away_goals': 2
            }
            
            # Draw match
            draw_data = {
                'ht_id': 601003,
                'home_team_id': 50001,
                'home_team_name': 'Draw Team FC',
                'away_team_id': 50003,
                'away_team_name': 'Draw Opposition United',
                'datetime': datetime.now() - timedelta(days=1),
                'matchtype': 1,  # League match
                'context_id': 0,
                'rule_id': 0,
                'cup_level': 0,
                'cup_level_index': 0,
                'home_goals': 2,
                'away_goals': 2
            }
            
            home_win = Match(home_win_data)
            away_win = Match(away_win_data)
            draw = Match(draw_data)
            db_session.add(home_win)
            db_session.add(away_win)
            db_session.add(draw)
            db_session.commit()
            
            # Test result classifications
            # Home win
            assert home_win.home_goals > home_win.away_goals
            
            # Away win
            assert away_win.home_goals < away_win.away_goals
            
            # Draw
            assert draw.home_goals == draw.away_goals
            
            # Test team 50001 record (2 matches, 1 win, 1 draw)
            team_50001_matches = db_session.query(Match).filter(
                (Match.home_team_id == 50001) | (Match.away_team_id == 50001)
            ).all()
            
            assert len(team_50001_matches) == 3  # Team played 3 matches
            
            # Calculate wins, draws, losses for team 50001
            wins = 0
            draws = 0
            losses = 0
            
            for match in team_50001_matches:
                if match.home_team_id == 50001:  # Playing at home
                    if match.home_goals > match.away_goals:
                        wins += 1
                    elif match.home_goals == match.away_goals:
                        draws += 1
                    else:
                        losses += 1
                else:  # Playing away
                    if match.away_goals > match.home_goals:
                        wins += 1
                    elif match.away_goals == match.home_goals:
                        draws += 1
                    else:
                        losses += 1
            
            assert wins == 2  # Team 50001 won 2 matches
            assert draws == 1  # Team 50001 drew 1 match
            assert losses == 0  # Team 50001 lost 0 matches

    def test_player_performance_analysis(self, app, db_session):
        """Test player performance in matches."""
        with app.app_context():
            # Excellent performance
            excellent_performance_data = {
                'match_id': 601001,
                'player_id': 701001,
                'datetime': datetime.now() - timedelta(days=7),
                'first_name': 'Star',
                'nick_name': 'Performer',
                'last_name': 'One',
                'role_id': 109,  # Central midfielder
                'rating_stars': 9.0,  # Excellent rating
                'rating_stars_eom': 8.5,  # End of match rating
                'behaviour': 1  # Normal behaviour
            }
            
            # Poor performance
            poor_performance_data = {
                'match_id': 601001,
                'player_id': 701002,
                'datetime': datetime.now() - timedelta(days=7),
                'first_name': 'Poor',
                'nick_name': 'Performer',
                'last_name': 'Two',
                'role_id': 100,  # Goalkeeper
                'rating_stars': 4.0,  # Poor rating
                'rating_stars_eom': 4.5,  # Slightly better end of match
                'behaviour': 1  # Normal behaviour
            }
            
            # Average performance
            average_performance_data = {
                'match_id': 601002,
                'player_id': 701001,
                'datetime': datetime.now() - timedelta(days=3),
                'first_name': 'Star',
                'nick_name': 'Performer',
                'last_name': 'One',
                'role_id': 109,  # Central midfielder
                'rating_stars': 6.5,  # Average rating
                'rating_stars_eom': 6.0,  # End of match rating
                'behaviour': 1  # Normal behaviour
            }
            
            excellent_perf = MatchPlay(excellent_performance_data)
            poor_perf = MatchPlay(poor_performance_data)
            average_perf = MatchPlay(average_performance_data)
            db_session.add(excellent_perf)
            db_session.add(poor_perf)
            db_session.add(average_perf)
            db_session.commit()
            
            # Test performance categorization
            assert excellent_perf.rating_stars >= 8.0  # Excellent performance
            assert poor_perf.rating_stars <= 5.0  # Poor performance
            assert 6.0 <= average_perf.rating_stars <= 7.0  # Average performance
            
            # Test player consistency (player 701001 played multiple matches)
            player_performances = db_session.query(MatchPlay).filter_by(player_id=701001).all()
            assert len(player_performances) == 2  # Player played 2 matches
            
            # Calculate average rating
            total_rating = sum(perf.rating_stars for perf in player_performances)
            average_rating = total_rating / len(player_performances)
            assert average_rating > 7.0  # Good average performance


class TestUserBusinessLogic:
    """Test business logic related to user management and activity tracking."""

    def test_user_activity_patterns(self, app, db_session):
        """Test user activity tracking and patterns."""
        with app.app_context():
            # Active user
            active_user = User(80001, 'active_user_ht', 'active_user', 'password', 'key1', 'secret1')
            db_session.add(active_user)
            db_session.commit()
            
            # Simulate active usage patterns
            for _ in range(5):
                active_user.login()
            for _ in range(10):
                active_user.player()
            for _ in range(7):
                active_user.matches()
            for _ in range(3):
                active_user.training()
            for _ in range(2):
                active_user.updatedata()
            
            # Test activity levels
            assert active_user.c_login >= 5  # Multiple logins
            assert active_user.c_player >= 10  # Regular player viewing
            assert active_user.c_matches >= 7  # Regular match viewing
            assert active_user.c_training >= 3  # Some training usage
            assert active_user.c_update >= 2  # Data updates
            
            # Test most active features
            assert active_user.c_player > active_user.c_matches  # More player than match activity
            assert active_user.c_matches > active_user.c_training  # More match than training activity

    def test_user_role_management(self, app, db_session):
        """Test user role assignment and management."""
        with app.app_context():
            # Regular user
            regular_user = User(80002, 'regular_user_ht', 'regular_user', 'password', 'key2', 'secret2')
            
            # Admin user
            admin_user = User(80003, 'admin_user_ht', 'admin_user', 'password', 'key3', 'secret3')
            
            db_session.add(regular_user)
            db_session.add(admin_user)
            db_session.commit()
            
            # Set roles
            regular_user.setRole('user')
            admin_user.setRole('admin')
            
            # Test role assignment
            assert regular_user.getRole() == 'user'
            assert admin_user.getRole() == 'admin'
            
            # Test role permissions (conceptual)
            assert admin_user.getRole() != regular_user.getRole()

    def test_user_preferences_management(self, app, db_session):
        """Test user preference management for player columns."""
        with app.app_context():
            user = User(80004, 'pref_user_ht', 'pref_user', 'password', 'key4', 'secret4')
            db_session.add(user)
            db_session.commit()
            
            # Test default preferences
            default_columns = user.getColumns()
            assert default_columns == []  # Empty by default
            
            # Set preferred columns
            preferred_columns = ['name', 'age', 'stamina', 'keeper', 'defender', 'playmaker', 'scorer']
            user.updateColumns(preferred_columns)
            
            # Test preference persistence
            retrieved_columns = user.getColumns()
            assert retrieved_columns == preferred_columns
            
            # Test preference modification
            modified_columns = ['name', 'age', 'form', 'stamina', 'scorer', 'leadership']
            user.updateColumns(modified_columns)
            
            updated_columns = user.getColumns()
            assert updated_columns == modified_columns
            assert updated_columns != preferred_columns


class TestCalculationBusinessLogic:
    """Test calculations and derived data business logic."""

    def test_team_statistics_calculations(self, app, db_session):
        """Test team-level statistics calculations."""
        with app.app_context():
            team_id = 90001
            
            # Create team players with varying skills
            players_data = []
            for i in range(11):  # Full team
                player_data = {
                    'ht_id': 900001 + i,
                    'first_name': f'Player{i+1}',
                    'nick_name': f'Nick{i+1}',
                    'last_name': f'Last{i+1}',
                    'number': i + 1,
                    'category_id': 0,
                    'owner_notes': '',
                    'age_years': 20 + (i % 8),
                    'age_days': i * 20,
                    'age': f'{20 + (i % 8)}.{i * 20}',
                    'next_birthday': datetime.now() + timedelta(days=300 + i * 10),
                    'arrival_date': datetime.now() - timedelta(days=200 + i * 50),
                    'form': 5 + (i % 4),
                    'cards': i % 3,
                    'injury_level': 0,
                    'statement': '',
                    'language': 'English',
                    'language_id': 2,
                    'agreeability': 5 + (i % 4),
                    'aggressiveness': 4 + (i % 5),
                    'honesty': 6 + (i % 3),
                    'experience': 3 + (i % 6),
                    'loyalty': 5 + (i % 4),
                    'specialty': i % 6,
                    'native_country_id': 5,
                    'native_league_id': 1,
                    'native_league_name': 'Test League',
                    'tsi': 1500 + (i * 300),
                    'salary': 8000 + (i * 2000),
                    'caps': i,
                    'caps_u20': i + 2,
                    'career_goals': i * 3,
                    'career_hattricks': i // 5,
                    'league_goals': i * 2,
                    'cup_goals': i,
                    'friendly_goals': i // 2,
                    'current_team_matches': 10 + (i * 2),
                    'current_team_goals': i * 2,
                    'national_team_id': 0,
                    'national_team_name': '',
                    'is_transfer_listed': i % 4 == 0,
                    'team_id': team_id,
                    'stamina': 5 + (i % 4),
                    'keeper': 8 if i == 0 else 3 + (i % 4),  # First player is keeper
                    'defender': 3 + (i % 6),
                    'playmaker': 3 + (i % 6),
                    'winger': 3 + (i % 6),
                    'passing': 4 + (i % 5),
                    'scorer': 4 + (i % 5),
                    'set_pieces': 3 + (i % 5),
                    'owner': 12345,
                    'mother_club_bonus': i % 5 == 0,
                    'leadership': 3 + (i % 6)
                }
                players_data.append(player_data)
            
            # Add players to database
            for player_data in players_data:
                player = Players(player_data)
                db_session.add(player)
            
            db_session.commit()
            
            # Test team statistics
            team_players = db_session.query(Players).filter_by(team_id=team_id).all()
            assert len(team_players) == 11  # Full team
            
            # Calculate team averages
            avg_age = sum(p.age_years for p in team_players) / len(team_players)
            avg_experience = sum(p.experience for p in team_players) / len(team_players)
            avg_stamina = sum(p.stamina for p in team_players) / len(team_players)
            total_salary = sum(p.salary for p in team_players)
            total_tsi = sum(p.tsi for p in team_players)
            
            # Test reasonable team statistics
            assert 20 <= avg_age <= 28  # Reasonable average age
            assert avg_experience >= 3  # Some team experience
            assert avg_stamina >= 5  # Decent team fitness
            assert total_salary > 100000  # Significant total salary
            assert total_tsi > 15000  # Significant total TSI
            
            # Test positional distribution
            goalkeepers = [p for p in team_players if p.keeper >= 7]
            outfield_players = [p for p in team_players if p.keeper < 7]
            
            assert len(goalkeepers) >= 1  # At least one goalkeeper
            assert len(outfield_players) >= 10  # At least 10 outfield players

    def test_form_and_performance_correlations(self, app, db_session):
        """Test correlations between form, experience, and performance."""
        with app.app_context():
            # High form, high experience player
            experienced_form_data = {
                'ht_id': 910001,
                'first_name': 'Experienced',
                'nick_name': 'Former',
                'last_name': 'Player',
                'number': 10,
                'category_id': 0,
                'owner_notes': '',
                'age_years': 27,
                'age_days': 150,
                'age': '27.150',
                'next_birthday': datetime.now() + timedelta(days=215),
                'arrival_date': datetime.now() - timedelta(days=1000),
                'form': 8,  # High form
                'cards': 1,
                'injury_level': 0,
                'statement': '',
                'language': 'English',
                'language_id': 2,
                'agreeability': 7,
                'aggressiveness': 6,
                'honesty': 8,
                'experience': 8,  # High experience
                'loyalty': 7,
                'specialty': 2,
                'native_country_id': 5,
                'native_league_id': 1,
                'native_league_name': 'England',
                'tsi': 4200,
                'salary': 38000,
                'caps': 15,
                'caps_u20': 20,
                'career_goals': 35,
                'career_hattricks': 3,
                'league_goals': 25,
                'cup_goals': 7,
                'friendly_goals': 3,
                'current_team_matches': 65,
                'current_team_goals': 25,
                'national_team_id': 3005,
                'national_team_name': 'England',
                'is_transfer_listed': False,
                'team_id': 91001,
                'stamina': 8,
                'keeper': 4,
                'defender': 7,
                'playmaker': 8,
                'winger': 6,
                'passing': 7,
                'scorer': 8,
                'set_pieces': 6,
                'owner': 12345,
                'mother_club_bonus': False,
                'leadership': 7
            }
            
            # Low form, low experience player
            inexperienced_poor_form_data = {
                'ht_id': 910002,
                'first_name': 'Inexperienced',
                'nick_name': 'Poor',
                'last_name': 'Former',
                'number': 15,
                'category_id': 0,
                'owner_notes': '',
                'age_years': 19,
                'age_days': 50,
                'age': '19.50',
                'next_birthday': datetime.now() + timedelta(days=315),
                'arrival_date': datetime.now() - timedelta(days=100),
                'form': 3,  # Poor form
                'cards': 0,
                'injury_level': 2,  # Injured
                'statement': '',
                'language': 'Spanish',
                'language_id': 3,
                'agreeability': 5,
                'aggressiveness': 4,
                'honesty': 6,
                'experience': 2,  # Low experience
                'loyalty': 8,
                'specialty': 0,
                'native_country_id': 15,
                'native_league_id': 5,
                'native_league_name': 'Spain',
                'tsi': 800,
                'salary': 4000,
                'caps': 0,
                'caps_u20': 0,
                'career_goals': 1,
                'career_hattricks': 0,
                'league_goals': 1,
                'cup_goals': 0,
                'friendly_goals': 0,
                'current_team_matches': 8,
                'current_team_goals': 1,
                'national_team_id': 0,
                'national_team_name': '',
                'is_transfer_listed': True,
                'team_id': 91001,
                'stamina': 5,
                'keeper': 3,
                'defender': 4,
                'playmaker': 3,
                'winger': 4,
                'passing': 3,
                'scorer': 4,
                'set_pieces': 2,
                'owner': 12345,
                'mother_club_bonus': True,
                'leadership': 2
            }
            
            experienced_player = Players(experienced_form_data)
            inexperienced_player = Players(inexperienced_poor_form_data)
            db_session.add(experienced_player)
            db_session.add(inexperienced_player)
            db_session.commit()
            
            # Test form and experience correlations
            assert experienced_player.form > inexperienced_player.form
            assert experienced_player.experience > inexperienced_player.experience
            
            # Test performance indicators
            assert experienced_player.career_goals > inexperienced_player.career_goals
            assert experienced_player.current_team_matches > inexperienced_player.current_team_matches
            
            # Test value correlations
            assert experienced_player.tsi > inexperienced_player.tsi * 3
            assert experienced_player.salary > inexperienced_player.salary * 5
            
            # Test injury impact on form/value
            assert inexperienced_player.injury_level > experienced_player.injury_level
            assert inexperienced_player.form < 5  # Poor form often correlates with injuries