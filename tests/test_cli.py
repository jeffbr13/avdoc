import subprocess
import sys
import tomllib
from pathlib import Path

from avdoc.__main__ import avdoc

PYPROJECT = Path(__file__).parent.parent / "pyproject.toml"


def test_output():
    result = avdoc(avsc=Path("tests/example.avsc"))
    assert result.startswith("<!DOCTYPE html>")


def test_cli_version_matches_pyproject():
    expected = tomllib.loads(PYPROJECT.read_text())["project"]["version"]
    result = subprocess.run(
        [sys.executable, "-m", "avdoc", "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == expected
