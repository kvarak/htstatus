"""Run the JavaScript unit tests in tests/js with Node's built-in test runner."""

from pathlib import Path
import shutil
import subprocess  # nosec B404 - runs the static local test command only

import pytest

JS_TEST_DIR = Path(__file__).parent / "js"


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js not installed")
def test_javascript_unit_tests():
    test_files = sorted(str(p) for p in JS_TEST_DIR.glob("*.test.js"))
    result = subprocess.run(  # nosec B603 B607
        ["node", "--test", *test_files],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
