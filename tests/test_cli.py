from pathlib import Path
from avdoc.__main__ import avdoc


def test_output():
    result = avdoc(avsc=Path("tests/example.avsc"))
    assert result.startswith("<!DOCTYPE html>")
