"""Naredbe `clipping`: `kreni` (izvor → PREGLED.md), `odobri` (serija → mobitel/), `verzija`."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from clipping import __version__
from clipping.job import Services, default_services, run_job
from clipping.profile import REPO_ROOT, CampaignProfile, ProfileError, load_profile


def _utf8_stdio() -> None:
    """Windows kroz cijev daje cp1252, a poruke su na hrvatskom; ispis ne smije pasti."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


_utf8_stdio()

app = typer.Typer(no_args_is_help=True, help="Alat za plaćene clipping kampanje.")


def make_services() -> Services:
    """Servisi posla; testovi ovo zamjenjuju lažnima."""
    return default_services()


def _fail(message: str, code: int = 2) -> typer.Exit:
    typer.echo(message, err=True)
    return typer.Exit(code=code)


def _load(root: Path, slug: str) -> CampaignProfile:
    try:
        return load_profile(root / "kampanje" / f"{slug}.yaml")
    except ProfileError as exc:
        raise _fail(str(exc)) from exc


@app.command()
def kreni(
    kampanja: str = typer.Option(..., help="Slug profila kampanje u kampanje/<slug>.yaml."),
    izvor: str | None = typer.Option(None, help="URL ili datoteka izvora; bez toga alat sam bira."),
    platforma: list[str] | None = typer.Option(
        None, help="Samo ove platforme iz profila (može više puta); zadano su sve iz profila."
    ),
    korijen: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Pokreni (ili nastavi) posao od izvora do mape za pregled."""
    from clipping.db import Database
    from clipping.ingest import IngestError, check_source, pick_new_video
    from clipping.select.claude_runner import SelectionError

    profile = _load(korijen, kampanja)
    chosen = list(platforma or [])
    outside = [p for p in chosen if p not in profile.platforme]
    if outside:
        raise _fail(
            f"platforma {', '.join(outside)} nije u profilu {kampanja} "
            f"({', '.join(profile.platforme)}); kampanja ne plaća tamo"
        )
    db = Database(korijen / "data" / "clipping.db")
    db.migrate()
    try:
        if izvor is None:
            kampanja_id = db.upsert_kampanja(profile)
            video = pick_new_video(profile, db.known_source_urls(kampanja_id))
            if video is None:
                raise _fail("nema novog videa na dopuštenim kanalima kampanje", code=1)
            typer.echo(f"izabran najnoviji neobrađeni video: {video.title} ({video.url})")
            izvor = video.url
        elif not Path(izvor).is_file():
            meta = check_source(izvor, profile)
            if meta is None:
                raise _fail(
                    f"izvor {izvor} nije s dopuštenog kanala kampanje "
                    f"({', '.join(profile.izvori.dopusteni_kanali)}); ADR-004"
                )
            izvor = meta.url  # dalje ide samo provjereni kanonski URL videa
        result = run_job(
            profile,
            izvor,
            db=db,
            root=korijen,
            services=make_services(),
            platforme=chosen or None,
        )
    except (IngestError, SelectionError) as exc:
        raise _fail(f"posao je stao: {exc}", code=1) from exc
    typer.echo(f"Gotovo: {result.isjecaka} isječaka. Pregled: {result.pregled}")


@app.command()
def odobri(
    posao: str = typer.Argument(..., help="ID posla iz izlaz/<posao>/."),
    izbaci: str = typer.Option("", help="Redni brojevi isječaka za izbaciti, odvojeni zarezom."),
    korijen: Path = typer.Option(REPO_ROOT, hidden=True),
) -> None:
    """Odobri seriju (bez izbačenih) i pripremi mapu izlaz/mobitel/."""
    from clipping.approve import ApproveError, approve
    from clipping.db import Database

    try:
        excluded = {int(part) for part in izbaci.replace(" ", "").split(",") if part}
    except ValueError as exc:
        raise _fail(f"--izbaci traži brojeve odvojene zarezom, dobiveno {izbaci!r}") from exc
    try:
        result = approve(
            posao,
            izbaci=excluded,
            db=Database(korijen / "data" / "clipping.db"),
            root=korijen,
            profile=None,
        )
    except (ApproveError, ProfileError) as exc:
        raise _fail(str(exc)) from exc
    for warning in result.upozorenja:
        typer.echo(f"upozorenje: {warning}", err=True)
    typer.echo(
        f"Odobreno {len(result.odobreni)}, izbačeno {len(result.izbaceni)}; "
        f"{len(result.datoteke)} videa u {korijen / 'izlaz' / 'mobitel'}"
    )


@app.command()
def verzija() -> None:
    """Ispiši verziju alata."""
    typer.echo(f"clipping {__version__}")


if __name__ == "__main__":
    app()
