"""Tests for the release tooling (scripts/release, release notes format)."""

import re
import subprocess

import pytest


@pytest.mark.local_only  # needs git tags (CI checkout is shallow)
def test_detect_version_changes():
    """Test version detection script"""
    result = subprocess.run(
        ["./scripts/release/detect_version_changes.sh"], capture_output=True, text=True
    )

    # Script can return 1 if no changes are found, which is valid
    assert result.returncode in [
        0,
        1,
    ], f"Version detection failed unexpectedly: {result.stderr}"
    assert "Current version:" in result.stderr
    # If no changes found, should contain expected message
    if result.returncode == 1:
        assert (
            "No feature commits found since" in result.stderr
            or "No feature or significant commits found" in result.stderr
        )
    else:
        assert (
            "Feature commits found" in result.stderr
            or "Significant commits found" in result.stderr
        )


@pytest.mark.parametrize("notes", ["RELEASES.md", "RELEASES-INTERNAL.md"])
def test_release_headings_parse_for_changes_page(notes):
    """scripts/changelog.sh only picks up "## X.Y - <date>" headings (no "v")."""
    with open(notes) as f:
        headings = [line.rstrip() for line in f if line.startswith("## ")]
    assert headings
    bad = [h for h in headings if not re.match(r"^## \d+\.\d+ - .+$", h)]
    assert not bad, f"{notes}: headings /changes cannot parse: {bad}"
