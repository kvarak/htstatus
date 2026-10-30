"""Which player table columns a user sees.

New columns (appended to ALL_COLUMNS after COLUMNS_BEFORE_AUTO_ADD) are added
once to the end of every user's saved column list, so nobody misses them. The
user can hide them again in Settings; that choice sticks.
"""

from app import db
from app.constants import ALL_COLUMNS, COLUMNS_BEFORE_AUTO_ADD, DEFAULT_COLUMNS


def user_columns(user, all_columns=ALL_COLUMNS, default_columns=DEFAULT_COLUMNS):
    """The user's columns, appending (and saving) any they haven't seen yet."""
    shown = user.getColumns() if user else []
    if not shown:
        return list(default_columns)

    known = user.getKnownColumns()
    saved_before_tracking = known is None
    if saved_before_tracking:
        known = COLUMNS_BEFORE_AUTO_ADD
    shown_keys = {key for _title, key in shown}
    new = [c for c in all_columns if c[1] not in known and c[1] not in shown_keys]

    if new or saved_before_tracking:
        shown += new
        save_user_columns(user, shown, all_columns)
        db.session.commit()
    return shown


def save_user_columns(user, columns, all_columns=ALL_COLUMNS):
    """Save the chosen columns; every existing column now counts as seen."""
    user.updateColumns(columns, known_keys=[key for _title, key in all_columns])
