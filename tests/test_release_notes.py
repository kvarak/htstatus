"""Release notes stay parseable by scripts/changelog.sh (the /changes page)."""

import re

import pytest


@pytest.mark.parametrize("notes", ["RELEASES.md", "RELEASES-INTERNAL.md"])
def test_release_headings_parse_for_changes_page(notes):
    """scripts/changelog.sh only picks up "## X.Y - <date>" headings (no "v")."""
    with open(notes) as f:
        headings = [line.rstrip() for line in f if line.startswith("## ")]
    assert headings
    bad = [h for h in headings if not re.match(r"^## \d+\.\d+ - .+$", h)]
    assert not bad, f"{notes}: headings /changes cannot parse: {bad}"
