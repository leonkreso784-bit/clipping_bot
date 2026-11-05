from typer.testing import CliRunner

from clipping.cli import app


def test_help_lists_commands() -> None:
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    for name in ("kreni", "odobri", "verzija"):
        assert name in result.output


def test_verzija_prints_version() -> None:
    result = CliRunner().invoke(app, ["verzija"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_help_survives_piped_cp1252_stdout() -> None:
    """Windows: kroz cijev stdout je cp1252, a pomoć sadrži hrvatske znakove."""
    import os
    import subprocess
    import sys

    env = {k: v for k, v in os.environ.items() if k != "PYTHONIOENCODING"}
    env["PYTHONUTF8"] = "0"
    result = subprocess.run(
        [sys.executable, "-m", "clipping.cli", "--help"],
        capture_output=True,
        env=env,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
    assert b"kreni" in result.stdout
