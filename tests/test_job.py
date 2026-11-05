"""Orkestrator na sintetičkom videu: lažni prijepis, izbor, kadar i pregled; pravi izvoz i QA."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from clipping import export as export_module
from clipping import qa as qa_module
from clipping.candidates import Candidate
from clipping.db import Database
from clipping.ingest import Downloaded
from clipping.job import Services, run_job
from clipping.profile import CampaignProfile, load_profile
from clipping.reframe.croppath import CropPath, centre_crop
from clipping.review import Review
from clipping.transcript import Transcript, Word

FIXTURE = Path(__file__).parent / "fixtures" / "kampanja_test.yaml"


def _profile(tmp_path: Path) -> CampaignProfile:
    """Testni profil s trajanjem 1.5–4 s da stane u 8 s sintetičkog videa."""
    data = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    data["isjecak"]["trajanje_s"] = {"min": 1.5, "max": 4}
    path = tmp_path / "kampanja.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return load_profile(path)


def _transcript() -> Transcript:
    """20 riječi po 0.4 s, rečenica od 5 riječi (2 s)."""
    words = [
        Word(f"w{i}" + ("." if i % 5 == 4 else ""), i * 0.4, i * 0.4 + 0.35) for i in range(20)
    ]
    return Transcript(words, "en", "lazni")


def _cand(start: int, end: int, ocjena: int) -> Candidate:
    return Candidate(
        start_word_index=start, end_word_index=end, naslov=f"k{start}", udica="u", ocjena=ocjena
    )


class Fakes:
    def __init__(self) -> None:
        self.calls: dict[str, int] = {"transcribe": 0, "select": 0, "export": 0, "review": 0}
        self.fail_export_after: int | None = None

    def services(self) -> Services:
        return Services(
            download=self.download,
            transcribe=self.transcribe,
            select=self.select,
            build_crop_path=self.crop,
            export_clip=self.export,
            check_clip=qa_module.check_clip,
            thumbnails=lambda clip, dest, duration: [],
            review=self.review,
        )

    def download(self, url: str, sources_dir: Path) -> Downloaded:
        raise AssertionError("testovi koriste lokalnu datoteku")

    def transcribe(self, wav: Path) -> Transcript:
        self.calls["transcribe"] += 1
        return _transcript()

    def select(self, t: Transcript, p: CampaignProfile, work: Path, win: Path) -> list[Candidate]:
        self.calls["select"] += 1
        assert win.is_file()
        return [_cand(0, 9, 80), _cand(10, 19, 70)]

    def crop(self, source: Path, *, start_s: float, end_s: float) -> CropPath:
        return centre_crop(1280, 720, end_s - start_s)

    def export(self, request: Any, *, work_dir: Path) -> Path:
        if self.fail_export_after is not None and self.calls["export"] >= self.fail_export_after:
            raise KeyboardInterrupt  # kao Ctrl+C usred rezanja
        self.calls["export"] += 1
        assert request.destination.name.endswith(".part.mp4")
        assert not request.destination.exists()  # ostatak prekida mora biti obrisan prije izvoza
        return export_module.export_clip(request, work_dir=work_dir)

    def review(self, text: str, profile: CampaignProfile, frames: list[Path], **kw: Any) -> Review:
        self.calls["review"] += 1
        return Review(ocjena=77, problemi=["kratko"])


@pytest.fixture
def env(tmp_path: Path, synthetic_video: Path) -> tuple[CampaignProfile, Database, Path, Path]:
    root = tmp_path / "korijen"
    db = Database(root / "data" / "clipping.db")
    return _profile(tmp_path), db, root, synthetic_video


def test_full_job_produces_clips(env: Any) -> None:
    profile, db, root, video = env
    fakes = Fakes()
    result = run_job(profile, str(video), db=db, root=root, services=fakes.services())
    clips = sorted((result.posao_dir / "isjecci").glob("*.mp4"))
    assert [c.name for c in clips] == ["01_bold_pop.mp4", "02_clean_lower.mp4"]
    rows = db.isjecci(result.posao_id)
    assert [r["status"] for r in rows] == ["provjeren", "provjeren"], [
        r["qa_nalazi_json"] for r in rows
    ]
    pregled = result.pregled.read_text(encoding="utf-8")
    assert f"clipping odobri {result.posao_id}" in pregled
    assert "01_bold_pop.mp4" in pregled and "77: kratko" in pregled
    assert db.posao(result.posao_id)["zavrseno"] is not None
    log = (result.posao_dir / "dnevnik.log").read_text(encoding="utf-8")
    assert "prijepis: gotov" in log


def test_resume_skips_transcribe(env: Any) -> None:
    profile, db, root, video = env
    first = Fakes()
    result = run_job(profile, str(video), db=db, root=root, services=first.services())
    second = Fakes()
    again = run_job(profile, str(video), db=db, root=root, services=second.services())
    assert second.calls["transcribe"] == 0
    assert again.posao_id != result.posao_id  # dovršen posao se ne nastavlja; novi posao
    log = (again.posao_dir / "dnevnik.log").read_text(encoding="utf-8")
    assert "prijepis: preskočen" in log


def test_resume_skips_rendered_clips(env: Any) -> None:
    profile, db, root, video = env
    first = Fakes()
    first.fail_export_after = 1
    with pytest.raises(KeyboardInterrupt):
        run_job(profile, str(video), db=db, root=root, services=first.services())
    assert first.calls == {"transcribe": 1, "select": 1, "export": 1, "review": 0}

    second = Fakes()
    result = run_job(profile, str(video), db=db, root=root, services=second.services())
    assert second.calls["transcribe"] == 0 and second.calls["select"] == 0
    assert second.calls["export"] == 1  # samo drugi isječak
    assert len(db.isjecci(result.posao_id)) == 2
    log = (result.posao_dir / "dnevnik.log").read_text(encoding="utf-8")
    assert "se nastavlja" in log and "01_bold_pop.mp4 preskočen" in log


def test_partial_file_is_rerendered(env: Any) -> None:
    profile, db, root, video = env
    first = Fakes()
    first.fail_export_after = 0
    with pytest.raises(KeyboardInterrupt):
        run_job(profile, str(video), db=db, root=root, services=first.services())
    posao_dir = next((root / "izlaz").iterdir())
    leftover = posao_dir / "isjecci" / "01_bold_pop.part.mp4"
    leftover.write_bytes(b"pola datoteke")

    second = Fakes()
    result = run_job(profile, str(video), db=db, root=root, services=second.services())
    assert second.calls["export"] == 2
    assert not leftover.exists()
    assert (posao_dir / "isjecci" / "01_bold_pop.mp4").stat().st_size > 1000
    assert all(r["qa_ok"] == 1 for r in db.isjecci(result.posao_id))


def test_duplicate_over_half_rejected(env: Any) -> None:
    profile, db, root, video = env
    first = run_job(profile, str(video), db=db, root=root, services=Fakes().services())
    first_rows = db.isjecci(first.posao_id)
    db.set_isjecak_status(int(first_rows[0]["id"]), "odobren")

    second = run_job(profile, str(video), db=db, root=root, services=Fakes().services())
    rows = db.isjecci(second.posao_id)
    assert len(rows) == 1 and rows[0]["naslov"] == "k10"
    assert any("duplikat" in r for r in second.odbijeni)
    assert "duplikat" in second.pregled.read_text(encoding="utf-8")


def test_resume_uses_saved_plan_after_approval_elsewhere(env: Any) -> None:
    """Pregled C3: odobrenje drugog posla prije nastavka ne smije pomaknuti redne brojeve."""
    profile, db, root, video = env
    job_a = run_job(profile, str(video), db=db, root=root, services=Fakes().services())

    killed = Fakes()
    killed.fail_export_after = 1
    with pytest.raises(KeyboardInterrupt):
        run_job(profile, str(video), db=db, root=root, services=killed.services())
    db.set_isjecak_status(int(db.isjecci(job_a.posao_id)[0]["id"]), "odobren")

    resumed = Fakes()
    job_b = run_job(profile, str(video), db=db, root=root, services=resumed.services())
    assert job_b.posao_id != job_a.posao_id and resumed.calls["export"] == 1
    assert [r["naslov"] for r in db.isjecci(job_b.posao_id)] == ["k0", "k10"]
