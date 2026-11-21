"""Delete a user's account and everything stored for it (DOC-033, /privacy).

Data is stored per Hattrick team, so the team ids decide what goes. A match
between two HattrickPlanner users' teams stays for the other user. Error logs
keep the error but lose the user id.
"""

from app import db, instance_cache, series, transfers


def delete_account(user):
    """Remove the user, their teams and all their data, then commit."""
    from models import (
        ActivityLog,
        AdminPreferences,
        ErrorLog,
        Feedback,
        FeedbackComment,
        FeedbackVote,
        Group,
        Match,
        MatchPlay,
        MatchPositionMinutes,
        Players,
        PlayerSetting,
        Team,
        TrainingWeek,
        TutorialAnalytics,
        User,
    )

    user_id = user.ht_id
    team_ids = [t.ht_id for t in Team.query.filter_by(user_id=user_id)]
    other_teams = db.session.query(Team.ht_id).filter(Team.user_id != user_id)

    if team_ids:
        own = Match.home_team_id.in_(team_ids) | Match.away_team_id.in_(team_ids)
        shared = Match.home_team_id.in_(other_teams) | Match.away_team_id.in_(
            other_teams
        )
        match_ids = [m.ht_id for m in Match.query.filter(own, ~shared)]
        if match_ids:
            MatchPlay.query.filter(MatchPlay.match_id.in_(match_ids)).delete(
                synchronize_session=False
            )
            Match.query.filter(Match.ht_id.in_(match_ids)).delete(
                synchronize_session=False
            )
        for model in (MatchPositionMinutes, TrainingWeek):
            model.query.filter(model.team_id.in_(team_ids)).delete(
                synchronize_session=False
            )
        Players.query.filter(Players.owner.in_(team_ids)).delete(
            synchronize_session=False
        )

    for feedback in Feedback.query.filter_by(author_id=user_id):
        db.session.delete(feedback)  # with its comments and votes
    db.session.flush()
    FeedbackComment.query.filter_by(author_id=user_id).delete()
    FeedbackVote.query.filter_by(user_id=user_id).delete()

    PlayerSetting.query.filter_by(user_id=user_id).delete()
    Group.query.filter_by(user_id=user_id).delete()
    AdminPreferences.query.filter_by(user_id=user_id).delete()
    TutorialAnalytics.query.filter_by(user_id=user_id).delete()
    ActivityLog.query.filter_by(user_id=user_id).delete()
    ErrorLog.query.filter_by(user_id=user_id).update({"user_id": None})
    Team.query.filter_by(user_id=user_id).delete()
    User.query.filter_by(ht_id=user_id).delete()
    db.session.commit()

    for team_id in team_ids:
        instance_cache.remove(series.FOLDER, team_id)
        instance_cache.remove(transfers.FOLDER, team_id)
