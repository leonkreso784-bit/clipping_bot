"""Naredbe `clipping`. Logika posla dolazi u cigli C3; ovdje je samo ulaz."""

from __future__ import annotations

import sys

import typer

from clipping import __version__


def _utf8_stdio() -> None:
    """Windows kroz cijev daje cp1252, a poruke su na hrvatskom; ispis ne smije pasti."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


_utf8_stdio()

app = typer.Typer(no_args_is_help=True, help="Alat za plaćene clipping kampanje.")

NIJE_IZGRADJENO = "Još nije izgrađeno (cigla C3)."


@app.command()
def kreni(
    kampanja: str = typer.Option(..., help="Slug profila kampanje u kampanje/<slug>.yaml."),
    izvor: str | None = typer.Option(None, help="URL ili datoteka izvora; bez toga alat sam bira."),
) -> None:
    """Pokreni posao od izvora do mape za pregled."""
    typer.echo(NIJE_IZGRADJENO, err=True)
    raise typer.Exit(code=2)


@app.command()
def odobri(
    posao: str = typer.Argument(..., help="ID posla iz izlaz/<posao>/."),
    izbaci: str = typer.Option("", help="ID-evi isječaka za izbaciti, odvojeni zarezom."),
) -> None:
    """Odobri seriju i pripremi mapu mobitel/."""
    typer.echo(NIJE_IZGRADJENO, err=True)
    raise typer.Exit(code=2)


@app.command()
def verzija() -> None:
    """Ispiši verziju alata."""
    typer.echo(f"clipping {__version__}")


if __name__ == "__main__":
    app()
