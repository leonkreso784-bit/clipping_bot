"""Reprodukcija probe (dokaz cigle C2): 9 kandidata iz probe ponovno izrezano našim lancem.

Pokretanje: uv run python scripts/izrezi_probu.py [--izlaz izlaz/proba-c2]
Ulazi: kampanje/caleb-hammer.yaml, data/izvori/JvLklMRThYs/{source.mp4,audio.wav,transcript.json,
whisper_referenca.json}, izlaz/proba-2026-11-04-caleb-hammer/radno/candidates.json.
Indeksi probe se odnose na Whisperov prijepis; prevode se preko vremena na Parakeetov prijepis.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

from clipping.audio import detect_silences, load_silences, save_silences
from clipping.boundaries import refine
from clipping.candidates import validate_candidates
from clipping.captions import PRESETS
from clipping.export import ExportRequest, export_clip
from clipping.profile import REPO_ROOT, load_profile
from clipping.qa import ClipExpectation, check_clip
from clipping.reframe import build_crop_path
from clipping.transcript import Transcript

PROFILE = REPO_ROOT / "kampanje" / "caleb-hammer.yaml"
SOURCE_DIR = REPO_ROOT / "data" / "izvori" / "JvLklMRThYs"
PROBE_CANDIDATES = (
    REPO_ROOT / "izlaz" / "proba-2026-11-04-caleb-hammer" / "radno" / "candidates.json"
)
FALLBACK_WATERMARK = REPO_ROOT / "tests" / "fixtures" / "zig_test.png"


def ensure_watermark() -> str | None:
    """Pravi žig ne postoji dok ga Leon ne doda; privremeno se koristi testni krug."""
    target = REPO_ROOT / "kampanje" / "caleb-hammer" / "zig.png"
    if target.is_file():
        return None
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(FALLBACK_WATERMARK, target)
    return (
        f"NAPOMENA: pravi žig ne postoji; privremeno kopiran {FALLBACK_WATERMARK.name} u {target}"
    )


def translate_candidates(
    raw_clips: list[dict[str, object]], whisper: Transcript, ours: Transcript
) -> dict[str, object]:
    """Whisperovi indeksi → vremena → Parakeetovi indeksi; ključevi probe → ključevi plana."""
    kandidati = []
    for clip in raw_clips:
        start_s, end_s = whisper.time_range(
            int(clip["start_word_index"]), int(clip["end_word_index"])
        )  # type: ignore[call-overload]
        span = ours.indices_in_range(start_s - 0.05, end_s + 0.05)
        if span is None:
            print(
                f"  preskačem kandidat {clip['title']!r}: nema riječi u {start_s:.1f}–{end_s:.1f} s"
            )
            continue
        kandidati.append(
            {
                "start_word_index": span[0],
                "end_word_index": span[1],
                "naslov": clip["title"],
                "udica": clip["hook"],
                "ocjena": clip["score"],
                "razlog": clip.get("reason", ""),
                "opis": "",
            }
        )
    return {"kandidati": kandidati}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    parser = argparse.ArgumentParser()
    parser.add_argument("--izlaz", type=Path, default=REPO_ROOT / "izlaz" / "proba-c2")
    args = parser.parse_args()
    out_dir: Path = args.izlaz
    work_dir = out_dir / "radno"
    out_dir.mkdir(parents=True, exist_ok=True)

    note = ensure_watermark()
    if note:
        print(note)
    profile = load_profile(PROFILE)
    source = SOURCE_DIR / "source.mp4"
    ours = Transcript.load(SOURCE_DIR / "transcript.json")
    whisper = Transcript.load(SOURCE_DIR / "whisper_referenca.json")

    silences_path = SOURCE_DIR / "silences.json"
    if silences_path.exists():
        silences = load_silences(silences_path)
    else:
        t0 = time.perf_counter()
        silences = detect_silences(SOURCE_DIR / "audio.wav")
        save_silences(silences_path, silences)
        print(f"tišine: {len(silences)} u {time.perf_counter() - t0:.0f} s")

    raw_clips = json.loads(PROBE_CANDIDATES.read_text(encoding="utf-8"))["clips"]
    accepted, rejected = validate_candidates(
        translate_candidates(raw_clips, whisper, ours), ours, profile.isjecak
    )
    for reason in rejected:
        print(f"  odbijen: {reason}")
    rules = profile.isjecak.trajanje_s

    rows: list[dict[str, object]] = []
    for index, cand in enumerate(sorted(accepted, key=lambda c: c.start_word_index)):
        boundary = refine(
            ours,
            cand.start_word_index,
            cand.end_word_index,
            silences=silences,
            min_duration_s=rules.min,
            max_duration_s=rules.max,
        )
        if boundary is None:
            print(f"  {cand.naslov!r}: nema granice unutar {rules.min:g}–{rules.max:g} s")
            continue
        t0 = time.perf_counter()
        crop_path = build_crop_path(source, start_s=boundary.start_s, end_s=boundary.end_s)
        t_kadar = time.perf_counter() - t0
        style_key = profile.caption_style_for(index)
        words = ours.slice(boundary.start_word, boundary.end_word)
        destination = out_dir / f"{index + 1:02d}_{style_key}.mp4"
        request = ExportRequest(
            source=source,
            destination=destination,
            start_s=boundary.start_s,
            end_s=boundary.end_s,
            crop_path=crop_path,
            words=words,
            style=PRESETS[style_key],
            watermark=profile.grafika.zig,
            top_text=profile.grafika.obvezni_tekst,
            mask_profanity=profile.pravila_sadrzaja.psovke.titlovi == "zvjezdice",
        )
        t1 = time.perf_counter()
        export_clip(request, work_dir=work_dir)
        t_izvoz = time.perf_counter() - t1
        t2 = time.perf_counter()
        report = check_clip(
            destination,
            expected=ClipExpectation(
                min_s=rules.min - 1.0,
                max_s=rules.max + 1.0,
                watermark=profile.grafika.zig,
                ass_path=work_dir / destination.stem / "captions.ass",
                words=words,
                start_s=boundary.start_s,
            ),
        )
        t_qa = time.perf_counter() - t2
        total = time.perf_counter() - t0
        strategies = ",".join(s.strategy for s in crop_path.segments)
        rows.append(
            {
                "isjecak": destination.name,
                "naslov": cand.naslov,
                "trajanje_s": round(boundary.duration_s, 1),
                "kadar_s": round(t_kadar, 1),
                "izvoz_s": round(t_izvoz, 1),
                "qa_s": round(t_qa, 1),
                "ukupno_s": round(total, 1),
                "segmenti": strategies,
                "qa_ok": report.ok,
                "nalazi": report.nalazi,
            }
        )
        verdict = "OK" if report.ok else "PAO " + "; ".join(report.nalazi)
        print(
            f"{destination.name}: {boundary.duration_s:.1f} s, kadar {t_kadar:.0f} s, "
            f"izvoz {t_izvoz:.0f} s, QA {t_qa:.0f} s, ukupno {total:.0f} s, {verdict}",
            flush=True,
        )

    avg = sum(float(r["ukupno_s"]) for r in rows) / len(rows) if rows else 0.0  # type: ignore[arg-type]
    summary = {
        "isjecaka": len(rows),
        "prosjek_s": round(avg, 1),
        "svi_qa_ok": all(bool(r["qa_ok"]) for r in rows),
        "prolaz": len(rows) >= 9 and avg < 120 and all(bool(r["qa_ok"]) for r in rows),
        "napomena": note,
        "redovi": rows,
    }
    (out_dir / "rezultat.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    qa_text = "svi OK" if summary["svi_qa_ok"] else "ima padova"
    print(f"isječaka {len(rows)}, prosjek {avg:.0f} s po isječku, QA {qa_text}")
    return 0 if summary["prolaz"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
