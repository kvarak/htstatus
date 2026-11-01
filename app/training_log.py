"""Training log (FEAT-035): which training a team ran each week.

Fetched at Update only (CHPP policy). CHPP returns this week's settings and the
last training, so every Update saves two rows: the last training (final) and
the coming one (planned, overwritten by a later Update once it has happened).
"""

from datetime import date, timedelta

from app import translations
from app.utils import dprint

TRAINING_WEEKDAY = 3  # Thursday: the weekly training update
HISTORY_WEEKS = 16  # one season

# English fallbacks for CHPP trainingType ids (Hattrick's own words come from
# the cached translations, section TrainingTypes)
TRAINING_TYPE_NAMES = {
    0: "General (form)",
    1: "Stamina",
    2: "Set pieces",
    3: "Defending",
    4: "Scoring",
    5: "Crossing (winger)",
    6: "Shooting",
    7: "Short passes",
    8: "Playmaking",
    9: "Goalkeeping",
    10: "Through passes",
    11: "Defensive positions",
    12: "Wing attacks",
}


def last_training_date(today):
    """The Thursday of the most recent training before ``today``.

    On a Thursday itself we assume the training (at night) hasn't happened yet.
    """
    days_back = (today.weekday() - TRAINING_WEEKDAY) % 7 or 7
    return today - timedelta(days=days_back)


def type_name(training_type):
    if training_type is None:
        return ""
    fallback = TRAINING_TYPE_NAMES.get(training_type, f"Type {training_type}")
    return translations.ht_term("TrainingTypes", training_type, fallback)


def _save_week(db, team_id, training_date, values, planned):
    from models import TrainingWeek

    row = TrainingWeek.query.filter_by(
        team_id=team_id, training_date=training_date
    ).first()
    if row is None:
        row = TrainingWeek(team_id=team_id, training_date=training_date)
        db.session.add(row)
    elif planned and not row.planned:
        return  # never overwrite a finished week with plans
    for key, value in values.items():
        setattr(row, key, value)
    row.planned = planned


def refresh(chpp, db, team_id, today=None):
    """Fetch and save the team's training; failures are logged, never raised."""
    try:
        data = chpp.training(team_id)
        trainer = {
            "trainer_id": data["trainer_id"],
            "trainer_name": data["trainer_name"] or None,
        }
        last = last_training_date(today or date.today())
        if data["last_training_type"] is not None:
            _save_week(
                db,
                team_id,
                last,
                {
                    "training_type": data["last_training_type"],
                    "intensity": data["last_intensity"],
                    "stamina_share": data["last_stamina_share"],
                    **trainer,
                },
                planned=False,
            )
        _save_week(
            db,
            team_id,
            last + timedelta(days=7),
            {
                "training_type": data["training_type"],
                "intensity": data["intensity"],
                "stamina_share": data["stamina_share"],
                **trainer,
            },
            planned=True,
        )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        dprint(1, f"Could not refresh training for team {team_id}: {e}")


def history(team_id, weeks=HISTORY_WEEKS):
    """The team's saved training weeks, newest first (planned week included)."""
    from models import TrainingWeek

    return (
        TrainingWeek.query.filter_by(team_id=team_id)
        .order_by(TrainingWeek.training_date.desc())
        .limit(weeks + 1)
        .all()
    )
