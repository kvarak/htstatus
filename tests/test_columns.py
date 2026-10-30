"""New player table columns reach every user, once (app/columns.py)."""

import pickle

from app.columns import save_user_columns, user_columns
from app.constants import ALL_COLUMNS, COLUMNS_BEFORE_AUTO_ADD, DEFAULT_COLUMNS
from models import User

ALL = [("Name", "name"), ("Age", "age_years"), ("TSI", "tsi"), ("New", "new_col")]
DEFAULTS = [("Name", "name"), ("New", "new_col")]


def _user(db_session, columns=None, known=None, legacy=None):
    user = User(777001, "cols", "cols", "x", "k", "s")
    if legacy is not None:
        user.player_columns = pickle.dumps(legacy)
    elif columns is not None:
        user.updateColumns(columns, known_keys=known or ())
    db_session.add(user)
    db_session.commit()
    return user


def test_new_columns_are_default_and_at_the_end():
    added = [c for c in ALL_COLUMNS if c[1] not in COLUMNS_BEFORE_AUTO_ADD]
    assert ("Current bid", "current_bid") in added
    assert DEFAULT_COLUMNS[-len(added) :] == added
    assert ALL_COLUMNS[-len(added) :] == added


def test_no_saved_columns_uses_defaults(db_session):
    assert user_columns(_user(db_session), ALL, DEFAULTS) == DEFAULTS
    assert user_columns(None, ALL, DEFAULTS) == DEFAULTS


def test_unseen_column_is_appended_once_and_saved(db_session):
    user = _user(db_session, [("Age", "age_years")], known=["name", "age_years", "tsi"])

    assert user_columns(user, ALL, DEFAULTS) == [
        ("Age", "age_years"),
        ("New", "new_col"),
    ]
    db_session.refresh(user)
    assert user.getKnownColumns() == {"name", "age_years", "tsi", "new_col"}

    # Hiding it again sticks
    save_user_columns(user, [("Age", "age_years")], ALL)
    db_session.commit()
    assert user_columns(user, ALL, DEFAULTS) == [("Age", "age_years")]


def test_hidden_known_columns_stay_hidden(db_session):
    user = _user(db_session, [("Age", "age_years")], known=[k for _t, k in ALL])
    assert user_columns(user, ALL, DEFAULTS) == [("Age", "age_years")]


def test_list_saved_before_tracking_gets_only_new_columns(db_session):
    user = _user(db_session, legacy=[("Name", "name")])  # e.g. "tsi" was hidden

    shown = user_columns(user, ALL_COLUMNS, DEFAULT_COLUMNS)

    assert shown == [("Name", "name"), ("Current bid", "current_bid")]
    db_session.refresh(user)
    assert user.getKnownColumns() == {k for _t, k in ALL_COLUMNS}
    assert user_columns(user, ALL_COLUMNS, DEFAULT_COLUMNS) == shown


def test_already_shown_new_column_is_not_duplicated(db_session):
    user = _user(db_session, legacy=[("Current bid", "current_bid")])
    assert user_columns(user, ALL_COLUMNS, DEFAULT_COLUMNS) == [
        ("Current bid", "current_bid")
    ]


def test_settings_shows_new_column_for_old_saved_list(app_with_routes, db_session):
    from tests.factories import setup_authenticated_session

    user = _user(db_session, legacy=[("Name", "name"), ("Age", "age_years")])
    client = setup_authenticated_session(app_with_routes.test_client(), user)

    html = client.get("/settings").get_data(as_text=True)

    shown_part = html[: html.index("Hidden columns")]
    assert 'id="current_bid">Current bid</div>' in shown_part
    assert shown_part.index('id="age_years"') < shown_part.index('id="current_bid"')
