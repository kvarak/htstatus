"""Tests for FEAT-027: Hattrick's own names for game terms (app/translations.py)."""

import os
import re
import time
from unittest.mock import MagicMock
import xml.etree.ElementTree as ET

import pytest

from app import instance_cache, translations
from app.chpp.parsers import parse_translations, parse_user, parse_worldlanguages

# Trimmed from a real CHPP translations response (languageId=5, Français)
TRANSLATIONS_XML = """<HattrickData>
  <FileName>translations.xml</FileName>
  <Language Id="5">Français</Language>
  <Texts>
    <SkillNames>
      <Skill Type="Keeper">Gardien</Skill>
      <Skill Type="Defender">Défense</Skill>
      <Skill Type="Kicker">Coup franc</Skill>
      <Skill Type="LeaderShip">Tempérament de chef</Skill>
    </SkillNames>
    <SkillLevels>
      <Level Value="0">inexistant</Level>
      <Level Value="7">honorable</Level>
    </SkillLevels>
    <PlayerSpecialties Label="Spécialité ">
      <Item Value="0">Aucune spécialité</Item>
      <Item Value="1">Technique</Item>
      <Item Value="8">Chef d'orchestre</Item>
    </PlayerSpecialties>
    <PlayerHonesty Label="Honnêteté">
      <Level Value="2">honnête</Level>
    </PlayerHonesty>
    <MatchPositions Label="Position">
      <Item Type="Keeper">Gardien de but</Item>
      <Item Type="Forward">Attaquant</Item>
    </MatchPositions>
  </Texts>
</HattrickData>"""

WORLDLANGUAGES_XML = """<HattrickData>
  <LanguageList>
    <Language><LanguageID>5</LanguageID><LanguageName>Français</LanguageName></Language>
    <Language><LanguageID>1</LanguageID><LanguageName>Svenska</LanguageName></Language>
    <Language><LanguageID>2</LanguageID><LanguageName>English (UK)</LanguageName></Language>
  </LanguageList>
</HattrickData>"""

FRENCH = parse_translations(ET.fromstring(TRANSLATIONS_XML))
LANGUAGES = parse_worldlanguages(ET.fromstring(WORLDLANGUAGES_XML))


@pytest.fixture
def tr_app(app_with_routes):
    """Routed app; conftest gives it an empty temp instance folder."""
    return app_with_routes


def _fake_chpp():
    chpp = MagicMock()
    chpp.translations.return_value = FRENCH
    chpp.worldlanguages.return_value = LANGUAGES
    return chpp


class TestParsers:
    def test_parse_translations(self):
        assert FRENCH["language_id"] == 5
        assert FRENCH["language_name"] == "Français"
        assert FRENCH["texts"]["SkillNames"]["Kicker"] == "Coup franc"
        assert FRENCH["texts"]["SkillLevels"]["7"] == "honorable"
        assert FRENCH["texts"]["PlayerSpecialties"]["8"] == "Chef d'orchestre"
        assert FRENCH["labels"]["PlayerSpecialties"] == "Spécialité"

    def test_parse_worldlanguages_sorted_by_name(self):
        assert LANGUAGES == [(2, "English (UK)"), (5, "Français"), (1, "Svenska")]

    def test_parse_user_language(self):
        root = ET.fromstring(
            "<HattrickData><Manager><UserId>7</UserId><Loginname>k</Loginname>"
            "<Language><LanguageId>1</LanguageId><LanguageName>Svenska</LanguageName>"
            "</Language></Manager></HattrickData>"
        )
        assert parse_user(root).language_id == 1
        assert parse_user(ET.fromstring("<HattrickData/>")).language_id is None


class TestTranslations:
    def test_english_fallback_without_cache(self, tr_app):
        with tr_app.test_request_context("/"):
            assert translations.column_label("Set pieces", "set_pieces") == "Set pieces"
            assert translations.column_label("Name", "name") == "Name"
            assert translations.specialty_name(8) == "Support"
            assert translations.level_text(7) == "7"
            assert translations.level_hint(7) == ""
            assert translations.available_languages() == []

    def test_refresh_caches_and_translates(self, tr_app):
        chpp = _fake_chpp()
        with tr_app.test_request_context("/"):
            translations.refresh(chpp, 5)
            from flask import session

            assert session["ht_language_id"] == 5
            assert translations.column_label("Set pieces", "set_pieces") == "Coup franc"
            assert translations.column_label("Specialty", "specialty") == "Spécialité"
            assert translations.column_label("Name", "name") == "Name"
            assert translations.specialty_name(1) == "Technique"
            assert translations.level_text(7) == "honorable (7)"  # default: both
            assert translations.level_hint(7) == ""
            assert translations.skill_labels()["keeper"] == "Gardien"
            assert translations.specialty_names()[2] == "Quick"  # untranslated
            assert translations.available_languages() == [list(x) for x in LANGUAGES]
        chpp.translations.assert_called_once_with(5)

    def test_refresh_skips_fresh_cache_and_refetches_stale(self, tr_app):
        chpp = _fake_chpp()
        with tr_app.test_request_context("/"):
            translations.refresh(chpp, 5)
            translations.refresh(chpp, 5)
            assert chpp.translations.call_count == 1

            old = time.time() - translations.MAX_AGE_SECONDS - 60
            os.utime(instance_cache.path(translations.FOLDER, 5), (old, old))
            translations.refresh(chpp, 5)
            assert chpp.translations.call_count == 2

    def test_refresh_never_raises(self, tr_app):
        chpp = MagicMock()
        chpp.translations.side_effect = RuntimeError("CHPP down")
        with tr_app.test_request_context("/"):
            translations.refresh(chpp, MagicMock())  # non-int language is ignored
            assert translations.language_id() == translations.DEFAULT_LANGUAGE_ID

    def test_cookie_override_wins(self, tr_app):
        cookie = f"{translations.LANGUAGE_COOKIE}=1"
        with tr_app.test_request_context("/", headers={"Cookie": cookie}):
            from flask import session

            session["ht_language_id"] = 5
            assert translations.language_id() == 1

    def test_words_level_format(self, tr_app):
        cookie = f"{translations.LEVEL_FORMAT_COOKIE}=words"
        with tr_app.test_request_context("/", headers={"Cookie": cookie}):
            translations.refresh(_fake_chpp(), 5)
            assert translations.level_format() == "words"
            assert translations.level_text(7) == "honorable"
            assert translations.level_hint(7) == "7"
            assert translations.level_text(2, "PlayerHonesty") == "honnête"
            assert translations.level_text(13) == "13"  # unknown word -> number

    def test_numbers_level_format(self, tr_app):
        cookie = f"{translations.LEVEL_FORMAT_COOKIE}=numbers"
        with tr_app.test_request_context("/", headers={"Cookie": cookie}):
            translations.refresh(_fake_chpp(), 5)
            assert translations.level_format() == "numbers"
            assert translations.level_text(7) == "7"
            assert translations.level_hint(7) == "honorable"

    def test_unknown_level_format_cookie_means_default(self, tr_app):
        cookie = f"{translations.LEVEL_FORMAT_COOKIE}=bogus"
        with tr_app.test_request_context("/", headers={"Cookie": cookie}):
            assert translations.level_format() == "both"

    def test_language_id_outside_request(self):
        assert translations.language_id() == translations.DEFAULT_LANGUAGE_ID


class TestSettingsLanguage:
    def _client(self, tr_app, db_session):
        from tests.conftest import create_test_user

        create_test_user(db_session)
        db_session.commit()
        client = tr_app.test_client()
        with client.session_transaction() as sess:
            sess["access_key"] = "k"
            sess["access_secret"] = "s"
            sess["current_user_id"] = 12345
            sess["current_user"] = "testuser"
            sess["all_teams"] = [12345]
            sess["all_team_names"] = ["Test Team"]
        return client

    def test_settings_lists_languages_and_saves_cookie(self, tr_app, db_session):
        with tr_app.test_request_context("/"):
            translations._write(translations.LANGUAGES_FILE, LANGUAGES)
        client = self._client(tr_app, db_session)

        html = client.get("/settings").get_data(as_text=True)
        assert "Use my Hattrick language" in html
        assert "Svenska" in html

        response = client.post("/settings", data={"language": "1"})
        assert f"{translations.LANGUAGE_COOKIE}=1" in response.headers["Set-Cookie"]
        assert re.search(r'value="1"\s+selected', response.get_data(as_text=True))

        response = client.post("/settings", data={"language": ""})
        assert "Max-Age=0" in response.headers["Set-Cookie"] or (
            "expires=Thu, 01 Jan 1970" in response.headers["Set-Cookie"]
        )

    def test_settings_without_language_list(self, tr_app, db_session):
        html = self._client(tr_app, db_session).get("/settings").get_data(as_text=True)
        assert "language list is loaded from Hattrick" in html
        assert 'name="language"' not in html
        assert re.search(r'value="both"\s+selected', html)

    def test_settings_saves_level_format(self, tr_app, db_session):
        client = self._client(tr_app, db_session)
        response = client.post("/settings", data={"level_format": "words"})
        assert (
            f"{translations.LEVEL_FORMAT_COOKIE}=words"
            in response.headers["Set-Cookie"]
        )
        assert re.search(r'value="words"\s+selected', response.get_data(as_text=True))
        # Saving only the level format leaves the language cookie alone
        assert translations.LANGUAGE_COOKIE not in response.headers["Set-Cookie"]

        response = client.post("/settings", data={"level_format": "numbers"})
        assert (
            f"{translations.LEVEL_FORMAT_COOKIE}=numbers"
            in response.headers["Set-Cookie"]
        )

        # Choosing the default clears the cookie
        response = client.post("/settings", data={"level_format": "both"})
        assert f"{translations.LEVEL_FORMAT_COOKIE}=;" in response.headers["Set-Cookie"]
        assert re.search(r'value="both"\s+selected', response.get_data(as_text=True))
