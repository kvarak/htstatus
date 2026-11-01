"""FEAT-035: the team's weekly training, saved at Update and shown on /training."""

from datetime import date
from unittest.mock import MagicMock
import xml.etree.ElementTree as ET

import pytest

from app import training_log
from app.chpp.parsers import parse_training
from tests.factories import setup_authenticated_session

TEAM = 12345

TRAINING_XML = """<HattrickData>
  <Team>
    <TeamID>12345</TeamID>
    <TeamName>Test Team</TeamName>
    <TrainingLevel>100</TrainingLevel>
    <NewTrainingLevel Available="False"></NewTrainingLevel>
    <TrainingType>8</TrainingType>
    <StaminaTrainingPart>15</StaminaTrainingPart>
    <LastTrainingTrainingType>3</LastTrainingTrainingType>
    <LastTrainingTrainingLevel>90</LastTrainingTrainingLevel>
    <LastTrainingStaminaTrainingPart>10</LastTrainingStaminaTrainingPart>
    <Trainer>
      <TrainerID>777</TrainerID>
      <TrainerName>Coach Carter</TrainerName>
    </Trainer>
  </Team>
</HattrickData>"""


def test_parse_training():
    data = parse_training(ET.fromstring(TRAINING_XML))

    assert data == {
        "team_id": 12345,
        "training_type": 8,
        "intensity": 100,
        "stamina_share": 15,
        "last_training_type": 3,
        "last_intensity": 90,
        "last_stamina_share": 10,
        "trainer_id": 777,
        "trainer_name": "Coach Carter",
    }


@pytest.mark.parametrize(
    ("today", "expected"),
    [
        (date(2026, 11, 5), date(2026, 10, 29)),  # Thursday: tonight's not done yet
        (date(2026, 11, 6), date(2026, 11, 5)),  # Friday
        (date(2026, 11, 11), date(2026, 11, 5)),  # Wednesday
    ],
)
def test_last_training_date(today, expected):
    assert training_log.last_training_date(today) == expected


def _chpp(**overrides):
    data = parse_training(ET.fromstring(TRAINING_XML)) | overrides
    chpp = MagicMock()
    chpp.training.return_value = data
    return chpp


def _weeks(app):
    from models import TrainingWeek

    with app.app_context():
        return {
            w.training_date: (w.training_type, w.intensity, w.planned)
            for w in TrainingWeek.query.filter_by(team_id=TEAM)
        }


@pytest.mark.usefixtures("db_session")
def test_refresh_saves_last_week_and_planned_week(app_with_routes):
    from app import db

    training_log.refresh(_chpp(), db, TEAM, today=date(2026, 11, 2))

    assert _weeks(app_with_routes) == {
        date(2026, 10, 29): (3, 90, False),
        date(2026, 11, 5): (8, 100, True),
    }


@pytest.mark.usefixtures("db_session")
def test_planned_week_becomes_final_and_finished_weeks_stay(app_with_routes):
    from app import db

    training_log.refresh(_chpp(), db, TEAM, today=date(2026, 11, 2))
    # A week later: the planned playmaking week happened at 80%
    later = _chpp(last_training_type=8, last_intensity=80, training_type=4)
    training_log.refresh(later, db, TEAM, today=date(2026, 11, 9))
    # Another Update that week with changed plans: only the planned week changes
    replanned = _chpp(last_training_type=8, last_intensity=80, training_type=3)
    training_log.refresh(replanned, db, TEAM, today=date(2026, 11, 9))

    weeks = _weeks(app_with_routes)
    assert weeks[date(2026, 10, 29)] == (3, 90, False)
    assert weeks[date(2026, 11, 5)] == (8, 80, False)
    assert weeks[date(2026, 11, 12)] == (3, 100, True)


@pytest.mark.usefixtures("db_session")
def test_plans_never_overwrite_a_finished_week(app_with_routes):
    from app import db

    # Friday: Thursday's training (playmaking 80%) is finished
    done = _chpp(last_training_type=8, last_intensity=80)
    training_log.refresh(done, db, TEAM, today=date(2026, 11, 6))
    # An Update dated that Thursday would write plans for the same week
    training_log.refresh(_chpp(), db, TEAM, today=date(2026, 10, 30))

    assert _weeks(app_with_routes)[date(2026, 11, 5)] == (8, 80, False)


@pytest.mark.usefixtures("db_session")
def test_refresh_failure_never_breaks_update(app_with_routes):
    from app import db

    chpp = MagicMock()
    chpp.training.side_effect = RuntimeError("CHPP down")

    training_log.refresh(chpp, db, TEAM, today=date(2026, 11, 2))

    assert _weeks(app_with_routes) == {}


def test_training_page_shows_the_log(app_with_routes, db_session):
    from app import db
    from tests.conftest import create_test_user

    user = create_test_user(db_session)
    training_log.refresh(_chpp(), db, TEAM, today=date(2026, 11, 2))
    client = setup_authenticated_session(app_with_routes.test_client(), user)

    html = client.get(f"/training?id={TEAM}").get_data(as_text=True)

    assert 'id="training-log"' in html
    assert "2026-10-29" in html
    assert "Defending" in html  # English fallback when no translations are cached
    assert "This week: Playmaking · 100%" in html
    assert "<em>(planned)</em>" in html


def test_training_page_explains_an_empty_log(app_with_routes, db_session):
    from tests.conftest import create_test_user

    user = create_test_user(db_session)
    client = setup_authenticated_session(app_with_routes.test_client(), user)

    html = client.get(f"/training?id={TEAM}").get_data(as_text=True)

    assert "to start the log" in html
