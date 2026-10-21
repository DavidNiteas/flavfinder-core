"""Smoke tests for the package skeleton and CLI."""

from __future__ import annotations

from flavfinder import __version__
from flavfinder.cli import main


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_cli_describe(capsys) -> None:
    assert main(["--describe"]) == 0
    out = capsys.readouterr().out
    assert "independent" in out
    assert "does not include" in out


def test_cli_default_help(capsys) -> None:
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "usage:" in out
