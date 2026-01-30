"""Feedback system routes blueprint for HT Status application."""

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    request,
    session,
    url_for,
)
from sqlalchemy import desc
from werkzeug.exceptions import abort

from app.utils import create_page, dprint

# Create Blueprint for feedback routes
feedback_bp = Blueprint("feedback", __name__, url_prefix="/feedback")

# These will be set by setup_feedback_blueprint()
app = None
db = None


def setup_feedback_blueprint(app_instance, db_instance):
    """Initialize feedback blueprint with app and db instances."""
    global app, db
    app = app_instance
    db = db_instance

    # Add nl2br filter for formatting feedback text
    @app_instance.template_filter('nl2br')
    def nl2br_filter(text):
        """Convert newlines to HTML line breaks."""
        if not text:
            return ''
        return text.replace('\n', '<br>\n')


@feedback_bp.route("/", methods=["GET", "POST"])
def list_feedback():
    """Display list of all feedback items with voting and handle new submissions."""

    from models import Feedback, FeedbackVote, User

    # Check authentication - session only, no CHPP calls
    if "access_key" not in session or "current_user_id" not in session:
        return redirect(url_for("auth.login"))

    # Get user from database (no CHPP API call)
    user_id = session["current_user_id"]
    user = User.query.filter_by(ht_id=user_id).first()
    if not user:
        return redirect(url_for("auth.login"))

    # Handle form submission
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        feedback_type = request.form.get("feedback_type", "").strip()
        description = request.form.get("description", "").strip()

        # Validation
        if not title or len(title) > 255:
            flash("Title is required and must be 255 characters or less", "error")
            return redirect(url_for("feedback.list_feedback"))

        if feedback_type not in ["bug", "feature", "idea"]:
            flash("Invalid feedback type", "error")
            return redirect(url_for("feedback.list_feedback"))

        if not description or len(description) > 5000:
            flash("Description is required and must be 5000 characters or less", "error")
            return redirect(url_for("feedback.list_feedback"))

        # Create feedback
        feedback = Feedback(
            title=title,
            feedback_type=feedback_type,
            description=description,
            author_id=user.ht_id
        )
        db.session.add(feedback)
        db.session.commit()

        flash("Thank you for your feedback!", "success")
        return redirect(url_for("feedback.list_feedback"))

    # Get active feedback (non-archived) ordered by vote score and creation date
    active_feedback = Feedback.query.filter(~Feedback.archived).order_by(desc(Feedback.vote_score), desc(Feedback.created_at)).all()

    # Get archived feedback ordered by creation date (newest first)
    archived_feedback = Feedback.query.filter(Feedback.archived).order_by(desc(Feedback.created_at)).all()
    # Get user's votes for quick lookup
    user_votes = {}
    votes = FeedbackVote.query.filter_by(user_id=user.ht_id).all()
    user_votes = {vote.feedback_id: vote.vote_type for vote in votes}

    # Create minimal user context from session data (no CHPP calls)
    user_context = {
        "user": user,
        "teams": session.get("all_teams", []),
        "team_names": session.get("all_team_names", [])
    }

    return create_page(
        template="feedback/list.html",
        title="Feedback",
        active_feedback=active_feedback,
        archived_feedback=archived_feedback,
        user_votes=user_votes,
        user_context=user_context
    )


@feedback_bp.route("/new", methods=["GET", "POST"])
def new_feedback():
    """Create new feedback item."""
    dprint(1, f"new_feedback called with method: {request.method}")
    from models import Feedback, User

    # Check authentication - session only, no CHPP calls
    if "access_key" not in session or "current_user_id" not in session:
        return redirect(url_for("auth.login"))

    # Get user from database (no CHPP API call)
    user_id = session["current_user_id"]
    user = User.query.filter_by(ht_id=user_id).first()
    if not user:
        return redirect(url_for("auth.login"))

    # Create minimal user context from session data (no CHPP calls)
    user_context = {
        "user": user,
        "teams": session.get("all_teams", []),
        "team_names": session.get("all_team_names", [])
    }

    if request.method == "POST":
        dprint(1, "Processing feedback form submission")
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        feedback_type = request.form.get("feedback_type", "").strip()

        dprint(1, f"Form data - title: '{title}', description: '{description}', feedback_type: '{feedback_type}'")

        # Validation
        if not title or len(title) < 5:
            flash("Title must be at least 5 characters long.", "error")
            return create_page(
                template="feedback/new.html",
                title="Submit Feedback",
                user_context=user_context
            )

        if not description or len(description) < 10:
            flash("Description must be at least 10 characters long.", "error")
            return create_page(
                template="feedback/new.html",
                title="Submit Feedback",
                user_context=user_context
            )

        if feedback_type not in ["bug", "feature", "idea"]:
            flash("Please select a valid feedback type.", "error")
            return create_page(
                template="feedback/new.html",
                title="Submit Feedback",
                user_context=user_context
            )

        # Create feedback
        dprint(1, f"Creating feedback with author_id: {user.ht_id}")
        feedback = Feedback(
            title=title,
            description=description,
            feedback_type=feedback_type,
            author_id=user.ht_id
        )

        try:
            dprint(1, "Adding feedback to database")
            db.session.add(feedback)
            db.session.commit()
            dprint(1, f"Feedback created successfully with id: {feedback.id}")
            flash("Feedback submitted successfully!", "success")
            return redirect(url_for("feedback.detail", id=feedback.id))
        except Exception as e:
            db.session.rollback()
            dprint(1, f"Error creating feedback: {e}")
            flash("Error submitting feedback. Please try again.", "error")

    return create_page(
        template="feedback/new.html",
        title="Submit Feedback",
        user_context=user_context
    )


@feedback_bp.route("/<int:id>")
def detail(id):
    """Display feedback details with comments."""
    from models import Feedback, FeedbackComment, FeedbackVote, User

    # Check authentication - session only, no CHPP calls
    if "access_key" not in session or "current_user_id" not in session:
        return redirect(url_for("auth.login"))

    # Get user from database (no CHPP API call)
    user_id = session["current_user_id"]
    user = User.query.filter_by(ht_id=user_id).first()
    if not user:
        return redirect(url_for("auth.login"))

    feedback = Feedback.query.get_or_404(id)

    # Get user's vote
    vote = FeedbackVote.query.filter_by(feedback_id=id, user_id=user.ht_id).first()
    user_vote = vote.vote_type if vote else None

    # Get comments ordered by creation date
    comments = FeedbackComment.query.filter_by(feedback_id=id).order_by(FeedbackComment.created_at).all()

    # Create minimal user context from session data (no CHPP calls)
    user_context = {
        "user": user,
        "teams": session.get("all_teams", []),
        "team_names": session.get("all_team_names", [])
    }

    return create_page(
        template="feedback/detail.html",
        title=f"Feedback: {feedback.title}",
        feedback=feedback,
        comments=comments,
        user_vote=user_vote,
        user_context=user_context
    )


@feedback_bp.route("/<int:id>/vote", methods=["POST"])
def vote(id):
    """Handle voting on feedback items."""
    from models import Feedback, FeedbackVote

    # Check authentication - just verify session, no CHPP calls needed
    if "access_key" not in session or "current_user_id" not in session:
        return jsonify({"error": "Authentication required"}), 401

    user_id = session["current_user_id"]

    feedback = Feedback.query.get_or_404(id)
    vote_type = request.json.get("vote_type")

    if vote_type != "up":
        return jsonify({"error": "Invalid vote type"}), 400

    try:
        # Check if user already voted
        existing_vote = FeedbackVote.query.filter_by(
            feedback_id=id,
            user_id=user_id
        ).first()

        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # Remove vote (toggle off)
                db.session.delete(existing_vote)
                new_vote_type = None
            else:
                # Change vote
                existing_vote.vote_type = vote_type
                new_vote_type = vote_type
        else:
            # Create new vote
            new_vote = FeedbackVote(
                feedback_id=id,
                user_id=user_id,
                vote_type=vote_type
            )
            db.session.add(new_vote)
            new_vote_type = vote_type

        db.session.commit()

        # Update vote score cache
        feedback.update_vote_score()

        return jsonify({
            "success": True,
            "vote_score": feedback.vote_score,
            "user_vote": new_vote_type
        })

    except Exception as e:
        db.session.rollback()
        dprint(1, f"Error voting on feedback: {e}")
        return jsonify({"error": "Error processing vote"}), 500


@feedback_bp.route("/<int:id>/comment", methods=["POST"])
def add_comment(id):
    """Add comment to feedback item."""
    from models import Feedback, FeedbackComment, User

    # Check authentication - just verify session
    if "access_key" not in session or "current_user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["current_user_id"]

    # Get user from database to check admin status
    user = User.query.filter_by(ht_id=user_id).first()
    if not user:
        return redirect(url_for("auth.login"))

    # Verify feedback exists (404 if not)
    Feedback.query.get_or_404(id)
    content = request.form.get("content", "").strip()

    if not content or len(content) < 5:
        flash("Comment must be at least 5 characters long.", "error")
        return redirect(url_for("feedback.detail", id=id))

    # Check if user is admin (includes hardcoded admin user)
    is_admin = user.is_admin()

    comment = FeedbackComment(
        feedback_id=id,
        author_id=user_id,
        content=content,
        is_admin=is_admin
    )

    try:
        db.session.add(comment)
        db.session.commit()
        flash("Comment added successfully!", "success")
    except Exception as e:
        db.session.rollback()
        dprint(1, f"Error adding comment: {e}")
        flash("Error adding comment. Please try again.", "error")

    return redirect(url_for("feedback.detail", id=id))


@feedback_bp.route("/<int:id>/status", methods=["POST"])
def update_status(id):
    """Update feedback status (admin only)."""
    from models import Feedback, User

    # Check authentication - verify admin without CHPP calls
    if "access_key" not in session or "current_user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["current_user_id"]
    user = User.query.filter_by(ht_id=user_id).first()

    if not user or not user.is_admin():
        abort(403)

    feedback = Feedback.query.get_or_404(id)
    new_status = request.form.get("status")

    valid_statuses = ["open", "planned", "in-progress", "completed", "wont-do"]
    if new_status not in valid_statuses:
        flash("Invalid status.", "error")
        return redirect(url_for("feedback.detail", id=id))

    try:
        feedback.status = new_status
        db.session.commit()
        flash(f"Status updated to '{new_status}'.", "success")
    except Exception as e:
        db.session.rollback()
        dprint(1, f"Error updating status: {e}")
        flash("Error updating status.", "error")

    return redirect(url_for("feedback.detail", id=id))


@feedback_bp.route("/<int:id>/archive", methods=["POST"])
def toggle_archive(id):
    """Toggle feedback archive status (admin only)."""
    from models import Feedback, User

    # Check authentication - verify admin without CHPP calls
    if "access_key" not in session or "current_user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["current_user_id"]
    user = User.query.filter_by(ht_id=user_id).first()

    if not user or not user.is_admin():
        abort(403)

    feedback = Feedback.query.get_or_404(id)

    try:
        feedback.archived = not feedback.archived
        db.session.commit()

        action = "archived" if feedback.archived else "unarchived"
        flash(f"Feedback {action} successfully.", "success")
    except Exception as e:
        db.session.rollback()
        dprint(1, f"Error toggling archive: {e}")
        flash("Error updating archive status.", "error")

    return redirect(url_for("feedback.detail", id=id))
