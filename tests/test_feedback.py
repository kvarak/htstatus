"""Tests for feedback blueprint models."""

import pytest

from models import Feedback, FeedbackComment, FeedbackVote, User

# NOTE: Feedback routes follow CHPP prevention policy (session + database only).
# See .github/agents/htplanner-ai-agent.md for CHPP API usage guidelines.


class TestFeedbackModels:
    """Test feedback database models."""

    def test_feedback_create(self, db_session):
        """Test creating a feedback item."""
        # Create test user
        user = User(
            ht_id=12345,
            ht_user="testuser",
            username="TestUser",
            password="password",
            access_key="test_key",
            access_secret="test_secret"
        )
        db_session.add(user)
        db_session.commit()

        # Create feedback
        feedback = Feedback(
            title="Test Feedback",
            description="Test description",
            feedback_type="bug",
            author_id=user.ht_id
        )
        db_session.add(feedback)
        db_session.commit()

        # Verify
        assert feedback.id is not None
        assert feedback.title == "Test Feedback"
        assert feedback.feedback_type == "bug"
        assert feedback.status == "open"
        assert feedback.author_id == user.ht_id
        assert feedback.vote_score == 0

    def test_feedback_update_vote_score(self, db_session):
        """Test updating vote score calculation."""
        # Create user and feedback
        user = User(
            ht_id=12345,
            ht_user="testuser",
            username="TestUser",
            password="password",
            access_key="test_key",
            access_secret="test_secret"
        )
        db_session.add(user)
        db_session.commit()

        feedback = Feedback(
            title="Vote Score Test",
            description="Test vote score",
            feedback_type="feature",
            author_id=user.ht_id
        )
        db_session.add(feedback)
        db_session.commit()

        # Add votes
        vote1 = FeedbackVote(
            feedback_id=feedback.id,
            user_id=user.ht_id,
            vote_type='up'
        )
        db_session.add(vote1)
        db_session.commit()

        # Update score
        feedback.update_vote_score()
        db_session.commit()

        assert feedback.vote_score == 1

    def test_feedback_relationships(self, db_session):
        """Test feedback model relationships."""
        # Create user
        user = User(
            ht_id=12345,
            ht_user="testuser",
            username="TestUser",
            password="password",
            access_key="test_key",
            access_secret="test_secret"
        )
        db_session.add(user)
        db_session.commit()

        # Create feedback
        feedback = Feedback(
            title="Relationship Test",
            description="Test relationships",
            feedback_type="idea",
            author_id=user.ht_id
        )
        db_session.add(feedback)
        db_session.commit()

        # Add comment
        comment = FeedbackComment(
            feedback_id=feedback.id,
            author_id=user.ht_id,
            content="Test comment",
            is_admin=False
        )
        db_session.add(comment)
        db_session.commit()

        # Add vote
        vote = FeedbackVote(
            feedback_id=feedback.id,
            user_id=user.ht_id,
            vote_type='up'
        )
        db_session.add(vote)
        db_session.commit()

        # Test relationships
        db_session.refresh(feedback)
        assert len(feedback.comments) == 1
        assert feedback.comments[0].content == "Test comment"
        assert len(feedback.votes) == 1
        assert feedback.votes[0].vote_type == 'up'
        assert feedback.author.ht_id == 12345

    def test_feedback_comment_create(self, db_session):
        """Test creating feedback comments."""
        # Create user and feedback
        user = User(
            ht_id=12345,
            ht_user="testuser",
            username="TestUser",
            password="password",
            access_key="test_key",
            access_secret="test_secret"
        )
        db_session.add(user)
        db_session.commit()

        feedback = Feedback(
            title="Comment Test",
            description="Test comments",
            feedback_type="feature",
            author_id=user.ht_id
        )
        db_session.add(feedback)
        db_session.commit()

        # Create comment
        comment = FeedbackComment(
            feedback_id=feedback.id,
            author_id=user.ht_id,
            content="This is a test comment",
            is_admin=False
        )
        db_session.add(comment)
        db_session.commit()

        # Verify
        assert comment.id is not None
        assert comment.content == "This is a test comment"
        assert comment.author_id == user.ht_id
        assert comment.is_admin is False
        assert comment.created_at is not None

    def test_feedback_vote_unique_constraint(self, db_session):
        """Test that users can only vote once per feedback."""
        # Create user and feedback
        user = User(
            ht_id=12345,
            ht_user="testuser",
            username="TestUser",
            password="password",
            access_key="test_key",
            access_secret="test_secret"
        )
        db_session.add(user)
        db_session.commit()

        feedback = Feedback(
            title="Vote Test",
            description="Test voting",
            feedback_type="bug",
            author_id=user.ht_id
        )
        db_session.add(feedback)
        db_session.commit()

        # First vote should succeed
        vote1 = FeedbackVote(
            feedback_id=feedback.id,
            user_id=user.ht_id,
            vote_type='up'
        )
        db_session.add(vote1)
        db_session.commit()

        # Second vote should fail due to unique constraint
        vote2 = FeedbackVote(
            feedback_id=feedback.id,
            user_id=user.ht_id,
            vote_type='up'
        )
        db_session.add(vote2)

        from sqlalchemy.exc import IntegrityError
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_feedback_admin_role(self, db_session):
        """Test admin user can be identified for status updates."""
        # Create admin user
        admin = User(
            ht_id=67890,
            ht_user="adminuser",
            username="AdminUser",
            password="password",
            access_key="admin_key",
            access_secret="admin_secret"
        )
        db_session.add(admin)
        db_session.commit()

        # Set role (using setter method since __init__ doesn't accept role)
        admin.setRole("admin")
        db_session.commit()

        # Verify
        assert admin.role == "admin"
        assert admin.getRole() == "admin"
