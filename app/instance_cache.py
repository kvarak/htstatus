"""Small JSON files in the Flask instance folder (data fetched from CHPP at Update).

Used instead of new database tables for data that is fine to lose and refetch.
"""

import json
import os
import time

from flask import current_app

_cache: dict[str, tuple[float, object]] = {}


def path(folder, name):
    return os.path.join(current_app.instance_path, folder, f"{name}.json")


def read_json(folder, name):
    """Read a JSON file (None if missing/broken), reloading only when it changed."""
    file = path(folder, name)
    try:
        mtime = os.path.getmtime(file)
        if file not in _cache or _cache[file][0] != mtime:
            with open(file, encoding="utf-8") as f:
                _cache[file] = (mtime, json.load(f))
        return _cache[file][1]
    except (OSError, ValueError):
        return None


def write_json(folder, name, data):
    """Write atomically, so readers never see a half-written file."""
    text = json.dumps(data, ensure_ascii=False)
    file = path(folder, name)
    os.makedirs(os.path.dirname(file), exist_ok=True)
    tmp = f"{file}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, file)


def is_fresh(folder, name, max_age_seconds):
    try:
        return time.time() - os.path.getmtime(path(folder, name)) < max_age_seconds
    except OSError:
        return False


def clear():
    """Forget the in-memory copies (tests switch instance folders)."""
    _cache.clear()
