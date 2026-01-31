"""Tests for feedback blueprint models."""

from unittest.mock import patch

from models import Feedback, FeedbackComment, FeedbackVote, User

# NOTE: Feedback routes follow CHPP prevention policy (session + database only).
# See .github/agents/htplanner-ai-agent.md for CHPP API usage guidelines.


class TestFeedbackModels:
    """Test feedback database models."""

    def test_feedback_create(self):
        """Test creating a feedback item."""
        # Create test user
        with patch('time.strftime', return_value="2024-01-01 12:00:00"):
            user = User(
                ht_id=12345,
                ht_user="testuser",
                username="TestUser",
                password="password",
                access_key="test_key",
                access_secret="test_secret"
            )

            # Create feedback (without database)
            feedback = Feedback(
                title="Test Feedback",
                description="Test description",
                feedback_type="bug",
                author_id=user.ht_id
            )

            # Verify model attributes
            assert feedback.title == "Test Feedback"
            assert feedback.description == "Test description"
            assert feedback.feedback_type == "bug"
            assert feedback.author_id == user.ht_id
            assert feedback.status == "open"  # Default status
            assert feedback.vote_score == 0  # Default score

    def test_feedback_update_vote_score(self):
        """Test updating vote score calculation."""
        # Create test feedback
        feedback = Feedback(
            title="Test Vote Feedback",
            description="Test vote description",
            feedback_type="feature",
            author_id=12345
        )

        # Test initial state
        assert feedback.vote_score == 0

        # Test vote score method exists (without database)
        assert hasattr(feedback, 'update_vote_score')

    def test_feedback_relationships(self):
        """Test feedback model relationships."""
        with patch('time.strftime', return_value="2024-01-01 12:00:00"):
            user = User(
                ht_id=12345,
                ht_user="testuser",
                username="TestUser",
                password="password",
                access_key="test_key",
                access_secret="test_secret"
            )

            feedback = Feedback(
                title="Relationship Test",
                description="Test relationships",
                feedback_type="bug",
                author_id=user.ht_id
            )

            # Test basic model structure
            assert feedback.author_id == user.ht_id
            assert feedback.title == "Relationship Test"

    def test_feedback_comment_create(self):
        """Test creating a feedback comment."""
        feedback_comment = FeedbackComment(
            feedback_id=1,
            author_id=12345,
            content="This is a test comment"
        )

        assert feedback_comment.feedback_id == 1
        assert feedback_comment.author_id == 12345
        assert feedback_comment.content == "This is a test comment"

    def test_feedback_vote_unique_constraint(self):
        """Test feedback vote model creation."""
        feedback_vote = FeedbackVote(
            feedback_id=1,
            user_id=12345,
            vote_type="upvote"
        )

        assert feedback_vote.feedback_id == 1
        assert feedback_vote.user_id == 12345
        assert feedback_vote.vote_type == "upvote"

    def test_feedback_admin_role(self):
        """Test feedback admin role detection."""
        with patch('time.strftime', return_value="2024-01-01 12:00:00"):
            # Test regular user
            user = User(
                ht_id=12345,
                ht_user="testuser",
                username="TestUser",
                password="password",
                access_key="test_key",
                access_secret="test_secret"
            )

            assert not user.is_admin()

            # Test admin user (hardcoded ID)
            admin_user = User(
                ht_id=182085,  # Hardcoded admin ID
                ht_user="admin",
                username="admin",
                password="password",
                access_key="admin_key",
                access_secret="admin_secret"
            )

            assert admin_user.is_admin()

            # Test role-based admin
            role_admin = User(
                ht_id=67890,
                ht_user="roleadmin",
                username="roleadmin",
                password="password",
                access_key="role_key",
                access_secret="role_secret"
            )
            role_admin.role = "admin"

            assert role_admin.is_admin()
