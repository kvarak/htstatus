"""Hattrick's own names for game terms (skills, skill levels, specialties...).

Translations come from CHPP and are only fetched at login and Update (CHPP
policy). They are cached as JSON in the instance folder and refreshed monthly.
Anything missing falls back to the English text used in the templates.
"""

import json
import os
import time

from flask import current_app, has_request_context, request, session

from app.constants import ALL_COLUMNS
from app.utils import dprint

DEFAULT_LANGUAGE_ID = 2  # English (UK)
LANGUAGE_COOKIE = "htstatus-language"
LEVEL_FORMAT_COOKIE = "htstatus-level-format"
LEVEL_FORMATS = ("numbers", "words", "both")
DEFAULT_LEVEL_FORMAT = "both"
PREFERENCE_COOKIE_MAX_AGE = 5 * 365 * 24 * 3600
MAX_AGE_SECONDS = 30 * 24 * 3600
LANGUAGES_FILE = "languages"

# Player column key -> (translations section, item); item None = the section label
COLUMN_TERMS = {
    "keeper": ("SkillNames", "Keeper"),
    "defender": ("SkillNames", "Defender"),
    "playmaker": ("SkillNames", "Playmaker"),
    "winger": ("SkillNames", "Winger"),
    "passing": ("SkillNames", "Passer"),
    "scorer": ("SkillNames", "Scorer"),
    "set_pieces": ("SkillNames", "Kicker"),
    "stamina": ("SkillNames", "Stamina"),
    "experience": ("SkillNames", "Experience"),
    "leadership": ("SkillNames", "LeaderShip"),
    "form": ("SkillNames", "Form"),
    "specialty": ("PlayerSpecialties", None),
    "agreeability": ("PlayerAgreeability", None),
    "aggressiveness": ("PlayerAgressiveness", None),
    "honesty": ("PlayerHonesty", None),
}

ENGLISH_SPECIALTIES = {
    0: "No specialty",
    1: "Technical",
    2: "Quick",
    3: "Powerful",
    4: "Unpredictable",
    5: "Head specialist",
    6: "Resilient",
    8: "Support",
}

_cache: dict[str, tuple[float, object]] = {}


def _path(name):
    return os.path.join(current_app.instance_path, "translations", f"{name}.json")


def _read(name):
    """Read a cached JSON file, reloading it only when it changed on disk."""
    path = _path(name)
    try:
        mtime = os.path.getmtime(path)
        if path not in _cache or _cache[path][0] != mtime:
            with open(path, encoding="utf-8") as f:
                _cache[path] = (mtime, json.load(f))
        return _cache[path][1]
    except (OSError, ValueError):
        return None


def _write(name, data):
    text = json.dumps(data, ensure_ascii=False)
    path = _path(name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def _is_fresh(name):
    try:
        return time.time() - os.path.getmtime(_path(name)) < MAX_AGE_SECONDS
    except OSError:
        return False


def language_id():
    """Language chosen in Settings, else the user's Hattrick language, else English."""
    if not has_request_context():
        return DEFAULT_LANGUAGE_ID
    override = request.cookies.get(LANGUAGE_COOKIE, "")
    if override.isdigit():
        return int(override)
    return session.get("ht_language_id") or DEFAULT_LANGUAGE_ID


def refresh(chpp, hattrick_language_id=None):
    """Remember the user's Hattrick language and cache missing/stale translations.

    Only call this from login or Update. Failures are logged, never raised.
    """
    if isinstance(hattrick_language_id, int) and hattrick_language_id > 0:
        session["ht_language_id"] = hattrick_language_id
    lang = language_id()
    try:
        if not _is_fresh(lang):
            _write(lang, chpp.translations(lang))
        if not _is_fresh(LANGUAGES_FILE):
            _write(LANGUAGES_FILE, chpp.worldlanguages())
    except Exception as e:
        dprint(1, f"Could not refresh Hattrick translations: {e}")


def available_languages():
    """All Hattrick languages as ``[language_id, name]`` pairs (empty until cached)."""
    return _read(LANGUAGES_FILE) or []


def _terms():
    return _read(language_id()) or {}


def ht_term(section, key, default=""):
    """Hattrick's name for an item, e.g. ``ht_term("PlayerSpecialties", 1)``."""
    return _terms().get("texts", {}).get(section, {}).get(str(key), default)


def ht_label(section, default=""):
    """Hattrick's label for a whole section, e.g. "Specialty"."""
    return _terms().get("labels", {}).get(section, default)


def column_label(title, key):
    """Translated player column title, or the English title."""
    section, item = COLUMN_TERMS.get(key, (None, None))
    if section is None:
        return title
    return ht_term(section, item, title) if item else ht_label(section, title)


def skill_labels():
    """Translated titles for all translatable player columns, keyed by column."""
    titles = {key: title for title, key in ALL_COLUMNS}
    return {key: column_label(titles.get(key, key), key) for key in COLUMN_TERMS}


def specialty_name(specialty):
    return ht_term(
        "PlayerSpecialties", specialty, ENGLISH_SPECIALTIES.get(specialty, "")
    )


def specialty_names():
    return {key: specialty_name(key) for key in ENGLISH_SPECIALTIES}


def level_format():
    """How levels are shown, chosen in Settings: "both" (default), "numbers" or "words"."""
    choice = request.cookies.get(LEVEL_FORMAT_COOKIE) if has_request_context() else None
    return choice if choice in LEVEL_FORMATS else DEFAULT_LEVEL_FORMAT


def level_text(value, section="SkillLevels"):
    """A level as the user wants it: "7", "solid" or "solid (7)".

    Falls back to the number when the word isn't known (e.g. not cached yet).
    """
    fmt = level_format()
    word = ht_term(section, value) if fmt != "numbers" else ""
    if not word:
        return str(value)
    return f"{word} ({value})" if fmt == "both" else word


def level_hint(value, section="SkillLevels"):
    """The form not shown, for tooltips ("" when both are already shown)."""
    fmt = level_format()
    if fmt == "words":
        return str(value)
    return ht_term(section, value) if fmt == "numbers" else ""


def init_app(app):
    """Make the translation helpers available in all templates."""

    @app.context_processor
    def inject_translations():
        return {
            "ht_term": ht_term,
            "ht_label": ht_label,
            "column_label": column_label,
            "level_format": level_format,
            "level_text": level_text,
            "level_hint": level_hint,
            "skill_labels": skill_labels,
            "specialty_name": specialty_name,
            "specialty_names": specialty_names,
        }
