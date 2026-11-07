"""DOC-033: public privacy page and deleting an account with all its data."""

from datetime import date, datetime

import pytest

from tests.conftest import create_test_user
from tests.factories import make_player_record, setup_authenticated_session

US = 9838
OTHER = 4242
OUR_TEAM = 100
OTHER_TEAM = 200
STRANGER_TEAM = 300


def _match(ht_id, home, away):
    from models import Match

    return Match(
        {
            "ht_id": ht_id,
            "home_team_id": home,
            "home_team_name": f"Team {home}",
            "away_team_id": away,
            "away_team_name": f"Team {away}",
            "datetime": datetime(2026, 10, 1),
            "matchtype": 1,
            "context_id": 0,
            "rule_id": 0,
            "cup_level": 0,
            "cup_level_index": 0,
            "home_goals": 1,
            "away_goals": 0,
        }
    )


def _play(match_id, player_id):
    from models import MatchPlay

    return MatchPlay(
        {
            "match_id": match_id,
            "player_id": player_id,
            "datetime": datetime(2026, 10, 1),
            "first_name": "A",
            "nick_name": "",
            "last_name": "B",
            "role_id": 100,
            "rating_stars": 3.0,
            "rating_stars_eom": None,
            "behaviour": 0,
        }
    )


@pytest.fixture
def two_users(db_session):
    """Us and another user; our teams played each other once (match 2)."""
    from models import (
        ErrorLog,
        Feedback,
        FeedbackComment,
        FeedbackVote,
        Group,
        MatchPositionMinutes,
        PlayerSetting,
        Team,
        TrainingWeek,
    )

    create_test_user(db_session, user_id=US, username="kvarak")
    create_test_user(db_session, user_id=OTHER, username="other")
    db_session.add_all([Team(OUR_TEAM, "Us", US), Team(OTHER_TEAM, "Them", OTHER)])
    for ht_id, owner in ((1, OUR_TEAM), (2, OTHER_TEAM)):
        player = make_player_record(ht_id, owner)
        player.data_date = datetime(2026, 10, 1)
        db_session.add(player)
    db_session.add_all(
        [
            _match(1, OUR_TEAM, STRANGER_TEAM),
            _match(2, OUR_TEAM, OTHER_TEAM),
            _match(3, OTHER_TEAM, STRANGER_TEAM),
            TrainingWeek(team_id=OUR_TEAM, training_date=date(2026, 10, 2)),
            TrainingWeek(team_id=OTHER_TEAM, training_date=date(2026, 10, 2)),
            MatchPositionMinutes(
                match_id=1, team_id=OUR_TEAM, player_id=1, role_id=100, minutes=90
            ),
            ErrorLog("500", "boom", user_id=US),
        ]
    )
    db_session.flush()
    for play_id, (match_id, player_id) in enumerate(((1, 1), (2, 1), (2, 2)), 1):
        play = _play(match_id, player_id)
        play.id = play_id
        db_session.add(play)
    group = Group(US, "Keep", 1, "#000000", "#FFFFFF")
    db_session.add(group)
    ours = Feedback("Mine", "text", "idea", US)
    theirs = Feedback("Theirs", "text", "idea", OTHER)
    db_session.add_all([ours, theirs])
    db_session.flush()
    db_session.add_all(
        [
            PlayerSetting(1, US, group.id),
            FeedbackComment(ours.id, OTHER, "reply on ours"),
            FeedbackComment(theirs.id, US, "our comment"),
            FeedbackComment(theirs.id, OTHER, "their comment"),
            FeedbackVote(theirs.id, US, "up"),
        ]
    )
    db_session.commit()


def _client(app_with_routes):
    client = setup_authenticated_session(app_with_routes.test_client(), US, "kvarak")
    with client.session_transaction() as sess:
        sess["all_teams"] = [OUR_TEAM]
        sess["all_team_names"] = ["Us"]
    return client


def test_privacy_page_is_public_and_linked_from_footer(app_with_routes):
    client = app_with_routes.test_client()
    html = client.get("/privacy").get_data(as_text=True)
    assert "Delete your account" in html
    assert "HT-mail" in html
    assert 'href="/privacy"' in client.get("/changes").get_data(as_text=True)


@pytest.mark.usefixtures("two_users")
def test_delete_needs_the_token_from_settings(app_with_routes, db_session):
    from models import User

    client = _client(app_with_routes)
    response = client.post("/settings/delete-account", data={"token": "guess"})
    assert response.status_code == 302
    assert db_session.get(User, US) is not None


@pytest.mark.usefixtures("two_users")
def test_delete_account_removes_our_data_and_keeps_others(app_with_routes, db_session):
    from models import (
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
        User,
    )

    client = _client(app_with_routes)
    client.get("/settings")
    with client.session_transaction() as sess:
        token = sess["delete_account_token"]

    response = client.post("/settings/delete-account", data={"token": token})

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/privacy?deleted=1")
    with client.session_transaction() as sess:
        assert "current_user" not in sess
    db_session.expire_all()
    assert [u.ht_id for u in User.query.all()] == [OTHER]
    assert [t.ht_id for t in Team.query.all()] == [OTHER_TEAM]
    assert [p.owner for p in Players.query.all()] == [OTHER_TEAM]
    # The match against the other user's team stays, with its line-up
    assert sorted(m.ht_id for m in Match.query.all()) == [2, 3]
    assert sorted(p.match_id for p in MatchPlay.query.all()) == [2, 2]
    assert [t.team_id for t in TrainingWeek.query.all()] == [OTHER_TEAM]
    assert MatchPositionMinutes.query.count() == 0
    assert Group.query.count() == PlayerSetting.query.count() == 0
    assert [f.title for f in Feedback.query.all()] == ["Theirs"]
    assert [c.content for c in FeedbackComment.query.all()] == ["their comment"]
    assert FeedbackVote.query.count() == 0
    assert [e.user_id for e in ErrorLog.query.filter_by(message="boom")] == [None]
    assert "deleted" in client.get(response.headers["Location"]).get_data(as_text=True)


@pytest.mark.usefixtures("two_users")
def test_delete_account_removes_team_cache_files(app_with_routes, db_session):
    from app import account, instance_cache, series, transfers
    from models import User

    with app_with_routes.app_context():
        instance_cache.write_json(series.FOLDER, OUR_TEAM, {"a": 1})
        instance_cache.write_json(transfers.FOLDER, OTHER_TEAM, {"b": 2})
        account.delete_account(db_session.get(User, US))
        assert instance_cache.read_json(series.FOLDER, OUR_TEAM) is None
        assert instance_cache.read_json(transfers.FOLDER, OTHER_TEAM) == {"b": 2}
