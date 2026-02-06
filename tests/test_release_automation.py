#!/usr/bin/env python3
"""
Tests for release automation scripts
Purpose: Ensure release generation works correctly
"""

import shutil
import subprocess
import tempfile


def test_detect_version_changes():
    """Test version detection script"""
    result = subprocess.run(
        ["./scripts/release/detect_version_changes.sh"],
        capture_output=True,
        text=True
    )

    # Script can return 1 if no changes are found, which is valid
    assert result.returncode in [0, 1], f"Version detection failed unexpectedly: {result.stderr}"
    assert "Current version:" in result.stderr
    # If no changes found, should contain expected message
    if result.returncode == 1:
        assert "No feature commits found since" in result.stderr or "No feature or significant commits found" in result.stderr
    else:
        assert "Feature commits found" in result.stderr or "Significant commits found" in result.stderr

def test_generate_release_content():
    """Test release content generation"""
    result = subprocess.run(
        ["./scripts/release/generate_release_content.sh", "v3.1"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Content generation failed: {result.stderr}"
    assert "## v3.1 - " in result.stdout
    assert "February 2026" in result.stdout
    assert "-" in result.stdout  # Should have bullet points

def test_update_releases():
    """Test RELEASES.md update process"""
    # Create a temporary RELEASES.md file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as temp_file:
        temp_file.write("""# Releases

**Purpose**: User-focused summaries
---

## v3.0 - January 2026
- Existing content
""")
        temp_file_path = temp_file.name

    # Backup original and replace with test file
    original_path = "RELEASES.md"
    backup_path = "RELEASES.md.backup"

    shutil.move(original_path, backup_path)
    shutil.move(temp_file_path, original_path)

    try:
        # Run update script
        result = subprocess.run(
            ["./scripts/release/update_releases.sh", "v3.2"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"Update script failed: {result.stderr}"

        # Check the updated file
        with open(original_path) as f:
            content = f.read()

        assert "## v3.2 - " in content
        assert "## v3.0 - January 2026" in content  # Original content preserved

    finally:
        # Restore original file
        shutil.move(backup_path, original_path)

if __name__ == "__main__":
    test_detect_version_changes()
    test_generate_release_content()
    test_update_releases()
    print("✅ All release automation tests passed!")

# To run: uv run python tests/test_release_automation.py
