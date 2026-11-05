"""Orkestrator posla: od izvora do `PREGLED.md`, s nastavkom nakon prekida (dizajn §6 i §8).

Koraci: ulaz, zvuk, prijepis, tisine, prozor, izbor, rezanje, provjera, pregled. Svaki upisuje
`pocet` i `gotov` u bazu. Zvuk, prijepis i tišine se spremaju uz izvor (`data/izvori/<id>/`) s
hashem izvora u `<datoteka>.sha256`, pa ih ni novi posao istog izvora ne ponavlja. Isječak dobiva
red u bazi tek kad je MP4 potpun: izvoz piše u `*.part.mp4` pa preimenuje.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from clipping import audio as audio_module
from clipping.boundaries import Boundary, refine
from clipping.candidates import Candidate
from clipping.captions import PRESETS
from clipping.db import MAX_DUPLICATE_OVERLAP, Database, find_duplicate
from clipping.export import ExportRequest
from clipping.ingest import Downloaded, sha256_file
from clipping.profile import CampaignProfile
from clipping.qa import ClipExpectation, QaReport
from clipping.review import PregledRow, Review, write_pregled
from clipping.select.claude_runner import load_candidates, save_candidates
from clipping.select.window import write_window
from clipping.transcript import Transcript

STEPS = ("ulaz", "zvuk", "prijepis", "tisine", "prozor", "izbor", "rezanje", "provjera", "pregled")
#: Provjera trajanja dopušta ovoliko izvan profila (rez se slaže na kraj riječi i tišinu).
QA_DURATION_SLACK_S = 1.0


@dataclass
class Services:
    """Vanjski koraci posla; testovi ih zamjenjuju lažnima."""

    download: Callable[[str, Path], Downloaded]
    transcribe: Callable[[Path], Transcript]
    select: Callable[[Transcript, CampaignProfile, Path, Path], list[Candidate]]
    build_crop_path: Callable[..., Any]
    export_clip: Callable[..., Path]
    check_clip: Callable[..., QaReport]
    thumbnails: Callable[[Path, Path, float], list[Path]]
    review: Callable[..., Review]


def default_services() -> Services:
    """Pravi servisi; teški uvozi (onnx, mediapipe) tek kad posao stvarno krene."""
    from clipping import asr, export, ingest, qa, reframe, review
    from clipping.select import claude_runner

    def select(
        transcript: Transcript, profile: CampaignProfile, work_dir: Path, window: Path
    ) -> list[Candidate]:
        return claude_runner.select_candidates(transcript, profile, work_dir, window_path=window)

    def thumbnails(clip: Path, dest: Path, duration_s: float) -> list[Path]:
        return review.clip_thumbnails(clip, dest, duration_s=duration_s)

    return Services(
        download=lambda url, sources_dir: ingest.download(url, sources_dir),
        transcribe=lambda wav: asr.transcribe(wav),
        select=select,
        build_crop_path=reframe.build_crop_path,
        export_clip=export.export_clip,
        check_clip=qa.check_clip,
        thumbnails=thumbnails,
        review=review.independent_review,
    )


@dataclass
class JobResult:
    posao_id: str
    posao_dir: Path
    pregled: Path
    isjecaka: int
    odbijeni: list[str] = field(default_factory=list)


@dataclass
class _PlannedClip:
    redni: int
    candidate: Candidate
    boundary: Boundary
    stil: str
    destination: Path


class _Log:
    """Dnevnik posla: ekran, `izlaz/<posao>/dnevnik.log` i tablica `dogadjaj`."""

    def __init__(self, db: Database, echo: Callable[[str], None]) -> None:
        self.db = db
        self.echo = echo
        self.posao_id: str | None = None
        self.path: Path | None = None
        self._pending: list[str] = []

    def attach(self, posao_id: str, path: Path) -> None:
        self.posao_id, self.path = posao_id, path
        path.parent.mkdir(parents=True, exist_ok=True)
        pending, self._pending = self._pending, []
        for line in pending:
            self._write(line)

    def __call__(self, message: str, razina: str = "info") -> None:
        line = f"{datetime.now():%Y-%m-%d %H:%M:%S} {message}"
        self.echo(line)
        if self.path is None:
            self._pending.append(line)
        else:
            self._write(line)
        self.db.log_dogadjaj(self.posao_id, razina, message)

    def _write(self, line: str) -> None:
        assert self.path is not None
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def _sidecar(path: Path) -> Path:
    return path.with_name(path.name + ".sha256")


def cache_valid(path: Path, sha256: str) -> bool:
    marker = _sidecar(path)
    return path.is_file() and marker.is_file() and marker.read_text().strip() == sha256


def cache_mark(path: Path, sha256: str) -> None:
    _sidecar(path).write_text(sha256)


def run_job(
    profile: CampaignProfile,
    source: str,
    *,
    db: Database,
    root: Path,
    services: Services,
    platforme: list[str] | None = None,
    echo: Callable[[str], None] = print,
) -> JobResult:
    """Izvedi (ili nastavi) posao za izvor i vrati putanju `PREGLED.md`."""
    log = _Log(db, echo)
    db.migrate()
    kampanja_id = db.upsert_kampanja(profile)
    sources_dir = root / "data" / "izvori"

    # --- 1. ulaz (prije posla: tek iz hasha izvora znamo nastavlja li se posao) ---------------
    t0 = time.perf_counter()
    local = Path(source)
    if local.is_file():
        source_path = local.resolve()
        sha = sha256_file(source_path)
        url = str(source_path)
        cache_dir = sources_dir / f"datoteka-{sha[:12]}"
        log(f"ulaz: lokalna datoteka {source_path} (kanal se ne provjerava)", "upozorenje")
    else:
        got = services.download(source, sources_dir)
        source_path, sha, url = got.path, got.sha256, got.url
        cache_dir = source_path.parent
    cache_dir.mkdir(parents=True, exist_ok=True)
    zapis = f"{profile.izvori.zapis_prava} | izvor: {url} | {datetime.now():%Y-%m-%d}"
    izvor_id = db.get_or_create_izvor(kampanja_id, url, sha, zapis, str(source_path))

    posao_id = db.unfinished_posao(izvor_id)
    resumed = posao_id is not None
    if posao_id is None:
        posao_id = db.create_posao(izvor_id, list(platforme or profile.platforme))
    posao_row = db.posao(posao_id)
    job_platforms: list[str] = json.loads(posao_row["platforme_json"])
    posao_dir = root / "izlaz" / posao_id
    work_dir = posao_dir / "radno"
    clips_dir = posao_dir / "isjecci"
    work_dir.mkdir(parents=True, exist_ok=True)
    clips_dir.mkdir(parents=True, exist_ok=True)
    log.attach(posao_id, posao_dir / "dnevnik.log")
    log(f"posao {posao_id} {'se nastavlja' if resumed else 'počinje'}; izvor {url}")
    db.set_korak(posao_id, "ulaz", "gotov", f"{time.perf_counter() - t0:.1f} s")
    log(f"ulaz: gotov za {time.perf_counter() - t0:.1f} s")

    @contextmanager
    def step(name: str) -> Iterator[None]:
        start = time.perf_counter()
        db.set_korak(posao_id, name, "pocet")
        try:
            yield
        except Exception as exc:
            db.set_korak(posao_id, name, "greska", str(exc)[:500])
            log(f"{name}: greška: {exc}", "greska")
            raise
        took = time.perf_counter() - start
        db.set_korak(posao_id, name, "gotov", f"{took:.1f} s")
        log(f"{name}: gotov za {took:.1f} s")

    # --- 2. zvuk, 3. prijepis, 4. tišine (spremljeno uz izvor) -------------------------------
    wav = cache_dir / "audio.wav"
    if cache_valid(wav, sha):
        log("zvuk: preskočen (postoji za ovaj izvor)")
        db.set_korak(posao_id, "zvuk", "gotov", "preskočen")
    else:
        with step("zvuk"):
            audio_module.extract_audio(source_path, wav)
            cache_mark(wav, sha)

    transcript_path = cache_dir / "transcript.json"
    if cache_valid(transcript_path, sha):
        log("prijepis: preskočen (postoji za ovaj izvor)")
        db.set_korak(posao_id, "prijepis", "gotov", "preskočen")
        transcript = Transcript.load(transcript_path)
    else:
        with step("prijepis"):
            transcript = services.transcribe(wav)
            transcript.save(transcript_path)
            cache_mark(transcript_path, sha)
            log(f"prijepis: {len(transcript)} riječi, {transcript.duration / 60:.0f} min")

    silences_path = cache_dir / "silences.json"
    if cache_valid(silences_path, sha):
        log("tisine: preskočen (postoji za ovaj izvor)")
        db.set_korak(posao_id, "tisine", "gotov", "preskočen")
        silences = audio_module.load_silences(silences_path)
    else:
        with step("tisine"):
            silences = audio_module.detect_silences(wav)
            audio_module.save_silences(silences_path, silences)
            cache_mark(silences_path, sha)

    # --- 5. prozor, 6. izbor ------------------------------------------------------------------
    window = work_dir / "window.txt"
    with step("prozor"):
        write_window(transcript, window)

    candidates_path = work_dir / "candidates.json"
    if db.korak_status(posao_id, "izbor") == "gotov" and candidates_path.is_file():
        log("izbor: preskočen (candidates.json postoji)")
        candidates = load_candidates(candidates_path)
    else:
        with step("izbor"):
            candidates = services.select(transcript, profile, work_dir, window)
            save_candidates(candidates_path, candidates)
            log(f"izbor: {len(candidates)} kandidata")

    # --- 7. rezanje (po isječku; gotovi se ne režu ponovno) ----------------------------------
    # Plan se računa jednom i sprema: nastavak mora rezati iste raspone pod istim rednim brojem,
    # čak i ako se u međuvremenu nešto odobrilo ili se promijenio `refine` (pregled C3).
    plan_path = work_dir / "plan.json"
    if plan_path.is_file():
        planned, odbijeni = _load_plan(plan_path, clips_dir)
    else:
        odbijeni = []
        planned = _plan_clips(
            profile, transcript, silences, candidates, clips_dir, db, kampanja_id, sha, odbijeni
        )
        _save_plan(plan_path, planned, odbijeni)
    for reason in odbijeni:
        log(f"rezanje: odbijen {reason}", "upozorenje")
    existing = {int(r["redni"]): r for r in db.isjecci(posao_id)}
    with step("rezanje"):
        for clip in planned:
            row = existing.get(clip.redni)
            if row is not None and Path(row["putanja"]).is_file():
                log(f"rezanje: {clip.destination.name} preskočen (već izrezan)")
                continue
            _render(clip, profile, source_path, transcript, work_dir, services, log)
            db.insert_isjecak(
                posao_id,
                clip.redni,
                clip.candidate,
                start_word=clip.boundary.start_word,
                end_word=clip.boundary.end_word,
                start_s=clip.boundary.start_s,
                end_s=clip.boundary.end_s,
                path=clip.destination,
                stil=clip.stil,
            )

    # --- 8. provjera ----------------------------------------------------------------------------
    by_redni = {c.redni: c for c in planned}
    rules = profile.isjecak.trajanje_s
    with step("provjera"):
        for row in db.isjecci(posao_id):
            if row["qa_ok"] is not None or int(row["redni"]) not in by_redni:
                continue
            clip = by_redni[int(row["redni"])]
            report = services.check_clip(
                clip.destination,
                expected=ClipExpectation(
                    min_s=rules.min - QA_DURATION_SLACK_S,
                    max_s=rules.max + QA_DURATION_SLACK_S,
                    watermark=profile.grafika.zig,
                    ass_path=_workspace(work_dir, clip) / "captions.ass",
                    words=transcript.slice(clip.boundary.start_word, clip.boundary.end_word),
                    start_s=clip.boundary.start_s,
                ),
            )
            db.set_isjecak_qa(int(row["id"]), report.ok, report.nalazi)
            verdict = "OK" if report.ok else "PAO: " + "; ".join(report.nalazi)
            log(f"provjera: {clip.destination.name} {verdict}")

    # --- 9. pregled -----------------------------------------------------------------------------
    with step("pregled"):
        rows: list[PregledRow] = []
        for row in db.isjecci(posao_id):
            found = by_redni.get(int(row["redni"]))
            if found is None:
                continue
            clip = found
            problems: list[str] = json.loads(row["pregled_problemi_json"])
            score: int | None = row["pregled_ocjena"]
            if score is None:
                score, problems = _review(clip, profile, transcript, work_dir, services, log)
                db.set_isjecak_pregled(int(row["id"]), score, problems)
            rows.append(
                PregledRow(
                    redni=clip.redni,
                    datoteka=f"isjecci/{clip.destination.name}",
                    trajanje_s=clip.boundary.duration_s,
                    stil=clip.stil,
                    platforme=job_platforms,
                    naslov=clip.candidate.naslov,
                    udica=clip.candidate.udica,
                    ocjena_izbora=clip.candidate.ocjena,
                    pregled_ocjena=score,
                    pregled_problemi=problems,
                    qa_ok=None if row["qa_ok"] is None else bool(row["qa_ok"]),
                    qa_nalazi=json.loads(row["qa_nalazi_json"]),
                )
            )
        pregled = write_pregled(posao_dir, posao_id, rows, odbijeni)
    db.finish_posao(posao_id)
    log(f"posao gotov: {len(rows)} isječaka, pregled u {pregled}")
    return JobResult(posao_id, posao_dir, pregled, len(rows), odbijeni)


def _plan_clips(
    profile: CampaignProfile,
    transcript: Transcript,
    silences: list[audio_module.Silence],
    candidates: list[Candidate],
    clips_dir: Path,
    db: Database,
    kampanja_id: int,
    sha256: str,
    odbijeni: list[str],
) -> list[_PlannedClip]:
    """Plan rezova: granica, duplikat (po sadržaju izvora, ne po URL-u), stil, ime."""
    rules = profile.isjecak.trajanje_s
    committed = db.published_ranges(kampanja_id)
    planned: list[_PlannedClip] = []
    for cand in sorted(candidates, key=lambda c: c.start_word_index):
        boundary = refine(
            transcript,
            cand.start_word_index,
            cand.end_word_index,
            silences=silences,
            min_duration_s=rules.min,
            max_duration_s=rules.max,
        )
        if boundary is None:
            odbijeni.append(
                f"„{cand.naslov}”: nema granice rečenice unutar {rules.min:g}–{rules.max:g} s"
            )
            continue
        clash = find_duplicate(committed, sha256, boundary.start_s, boundary.end_s)
        if clash is not None:
            odbijeni.append(
                f"„{cand.naslov}”: duplikat, preklapa se više od {MAX_DUPLICATE_OVERLAP:.0%} s već "
                f"odobrenim ili objavljenim isječkom {clash.start_s:.0f}–{clash.end_s:.0f} s"
            )
            continue
        redni = len(planned) + 1
        stil = profile.caption_style_for(redni - 1)
        planned.append(
            _PlannedClip(redni, cand, boundary, stil, clips_dir / f"{redni:02d}_{stil}.mp4")
        )
    return planned


def _save_plan(path: Path, planned: list[_PlannedClip], odbijeni: list[str]) -> None:
    data = {
        "isjecci": [
            {
                "redni": c.redni,
                "kandidat": c.candidate.model_dump(),
                "granica": asdict(c.boundary),
                "stil": c.stil,
                "datoteka": c.destination.name,
            }
            for c in planned
        ],
        "odbijeni": odbijeni,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_plan(path: Path, clips_dir: Path) -> tuple[list[_PlannedClip], list[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    planned = [
        _PlannedClip(
            redni=int(item["redni"]),
            candidate=Candidate.model_validate(item["kandidat"]),
            boundary=Boundary(**item["granica"]),
            stil=str(item["stil"]),
            destination=clips_dir / str(item["datoteka"]),
        )
        for item in data["isjecci"]
    ]
    return planned, [str(r) for r in data["odbijeni"]]


def _part_path(clip: _PlannedClip) -> Path:
    return clip.destination.with_name(clip.destination.stem + ".part.mp4")


def _workspace(work_dir: Path, clip: _PlannedClip) -> Path:
    """Radna mapa izvoza (ASS i fontovi); `export_clip` je imenuje po imenu odredišta."""
    return work_dir / _part_path(clip).stem


def _render(
    clip: _PlannedClip,
    profile: CampaignProfile,
    source: Path,
    transcript: Transcript,
    work_dir: Path,
    services: Services,
    log: _Log,
) -> None:
    part = _part_path(clip)
    if part.exists():
        part.unlink()
        log(f"rezanje: {part.name} ostao od prekida, reže se ponovno")
    start = time.perf_counter()
    crop_path = services.build_crop_path(
        source, start_s=clip.boundary.start_s, end_s=clip.boundary.end_s
    )
    request = ExportRequest(
        source=source,
        destination=part,
        start_s=clip.boundary.start_s,
        end_s=clip.boundary.end_s,
        crop_path=crop_path,
        words=transcript.slice(clip.boundary.start_word, clip.boundary.end_word),
        style=PRESETS[clip.stil],
        watermark=profile.grafika.zig,
        top_text=profile.grafika.obvezni_tekst,
        mask_profanity=profile.pravila_sadrzaja.psovke.titlovi == "zvjezdice",
    )
    services.export_clip(request, work_dir=work_dir)
    part.replace(clip.destination)
    log(
        f"rezanje: {clip.destination.name} ({clip.boundary.duration_s:.0f} s) "
        f"za {time.perf_counter() - start:.0f} s"
    )


def _review(
    clip: _PlannedClip,
    profile: CampaignProfile,
    transcript: Transcript,
    work_dir: Path,
    services: Services,
    log: _Log,
) -> tuple[int | None, list[str]]:
    """Neovisni pregled ne blokira posao: greška postaje problem u izvještaju."""
    try:
        frames = services.thumbnails(
            clip.destination, work_dir / "slicice", clip.boundary.duration_s
        )
        result = services.review(
            transcript.text_between(clip.boundary.start_word, clip.boundary.end_word),
            profile,
            frames,
            naslov=clip.candidate.naslov,
            udica=clip.candidate.udica,
            trajanje_s=clip.boundary.duration_s,
        )
    except Exception as exc:
        log(f"pregled: {clip.destination.name} nije pregledan: {exc}", "upozorenje")
        return None, [f"pregled nije uspio: {str(exc)[:200]}"]
    log(f"pregled: {clip.destination.name} ocjena {result.ocjena}, problema {len(result.problemi)}")
    return result.ocjena, result.problemi
