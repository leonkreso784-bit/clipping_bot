"""Automatska provjera gotovog isječka (dizajn §6, korak 8).

Provjerava trajanje, glasnoću (ebur128), crne kadrove (blackdetect), prisutnost žiga (korelacija
svjetline s alfa-maskom žiga na poznatom položaju) i sinkron titlova (svaki ASS event počinje na
vremenu neke riječi, ±100 ms). Nalazi su na hrvatskom i idu u `PREGLED.md`.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pysubs2

from clipping import ffmpeg
from clipping.captions import STYLE_NAME
from clipping.export import (
    OUTPUT_HEIGHT,
    OUTPUT_WIDTH,
    WATERMARK_MARGIN_PX,
    watermark_render_size,
)
from clipping.profile import Watermark
from clipping.transcript import Word

LOUDNESS_RANGE_LUFS = (-16.0, -12.0)
CAPTION_TOLERANCE_S = 0.1
WATERMARK_MIN_CORRELATION = 0.5
WATERMARK_SAMPLE_AT_S = 1.0
BLACK_MIN_DURATION_S = 0.5


@dataclass
class ClipExpectation:
    min_s: float
    max_s: float
    watermark: Watermark | None
    ass_path: Path
    words: list[Word]
    start_s: float


@dataclass
class QaReport:
    ok: bool
    nalazi: list[str] = field(default_factory=list)


def check_clip(path: Path, *, expected: ClipExpectation) -> QaReport:
    """Pokreni sve provjere; `ok` je istina samo kad nema nalaza."""
    nalazi: list[str] = []
    info = ffmpeg.probe(path)
    if not expected.min_s <= info.duration_s <= expected.max_s:
        nalazi.append(
            f"trajanje {info.duration_s:.2f} s je izvan {expected.min_s:g}–{expected.max_s:g} s"
        )
    if (info.width, info.height) != (OUTPUT_WIDTH, OUTPUT_HEIGHT):
        nalazi.append(
            f"dimenzije {info.width}×{info.height}, očekivano {OUTPUT_WIDTH}×{OUTPUT_HEIGHT}"
        )
    if not info.has_audio:
        nalazi.append("nema zvuka")
    else:
        lufs = measure_loudness(path)
        if lufs is None:
            nalazi.append("glasnoća se ne može izmjeriti")
        elif not LOUDNESS_RANGE_LUFS[0] <= lufs <= LOUDNESS_RANGE_LUFS[1]:
            nalazi.append(f"glasnoća {lufs:.1f} LUFS je izvan {LOUDNESS_RANGE_LUFS}")
    black = detect_black(path)
    if black:
        nalazi.append(f"crni kadrovi: {', '.join(f'{s:.1f}–{e:.1f} s' for s, e in black)}")
    if expected.watermark is not None:
        score = watermark_score(
            path, expected.watermark, at_s=min(WATERMARK_SAMPLE_AT_S, info.duration_s / 2)
        )
        if score < WATERMARK_MIN_CORRELATION:
            nalazi.append(
                f"žig nije nađen na položaju {expected.watermark.polozaj} (korelacija {score:.2f})"
            )
    nalazi.extend(check_captions(expected.ass_path, expected.words, expected.start_s))
    return QaReport(ok=not nalazi, nalazi=nalazi)


def _ffmpeg_stderr(args: list[str]) -> str:
    result = subprocess.run(
        [ffmpeg.ffmpeg_path(), "-hide_banner", "-nostdin", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return result.stderr


def measure_loudness(path: Path) -> float | None:
    """Integrirana glasnoća (LUFS) kroz `ebur128`, ili `None` ako se ne može pročitati."""
    err = _ffmpeg_stderr(
        ["-i", str(path), "-vn", "-af", "ebur128=framelog=verbose", "-f", "null", "-"]
    )
    match = re.search(r"Integrated loudness:\s*I:\s*(-?[\d.]+) LUFS", err)
    return float(match.group(1)) if match else None


def detect_black(
    path: Path, *, min_duration_s: float = BLACK_MIN_DURATION_S
) -> list[tuple[float, float]]:
    """Rasponi crnih kadrova dužih od `min_duration_s`."""
    err = _ffmpeg_stderr(
        [
            "-i",
            str(path),
            "-an",
            "-vf",
            f"blackdetect=d={min_duration_s:g}:pic_th=0.98",
            "-f",
            "null",
            "-",
        ]
    )
    return [
        (float(m.group(1)), float(m.group(2)))
        for m in re.finditer(r"black_start:([\d.]+) black_end:([\d.]+)", err)
    ]


def _raw(args: list[str]) -> bytes:
    result = subprocess.run(
        [ffmpeg.ffmpeg_path(), "-hide_banner", "-nostdin", "-loglevel", "error", *args],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise ffmpeg.FFmpegError(result.stderr.decode("utf-8", "replace")[-500:])
    return result.stdout


def watermark_region(watermark: Watermark) -> tuple[int, int, int, int]:
    """`(x, y, w, h)` žiga u izlaznom kadru, po istom pravilu kao `export.watermark_position`."""
    info = ffmpeg.probe(watermark.path)
    w, h = watermark_render_size(info.width, info.height, OUTPUT_WIDTH)
    m = WATERMARK_MARGIN_PX
    positions = {
        "centar": ((OUTPUT_WIDTH - w) // 2, (OUTPUT_HEIGHT - h) // 2),
        "gore_lijevo": (m, m),
        "gore_desno": (OUTPUT_WIDTH - w - m, m),
        "dolje_lijevo": (m, OUTPUT_HEIGHT - h - m),
        "dolje_desno": (OUTPUT_WIDTH - w - m, OUTPUT_HEIGHT - h - m),
    }
    x, y = positions[watermark.polozaj]
    return x, y, w, h


def watermark_score(path: Path, watermark: Watermark, *, at_s: float) -> float:
    """Normalizirana korelacija svjetline u području žiga s alfa-maskom žiga (1 = savršeno)."""
    x, y, w, h = watermark_region(watermark)
    frame = _raw(
        ["-ss", f"{at_s:.3f}", "-i", str(path), "-frames:v", "1", "-vf", f"crop={w}:{h}:{x}:{y}",
         "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    )  # fmt: skip
    luma = np.frombuffer(frame, dtype=np.uint8).astype(np.float64)
    rgba = _raw(
        ["-i", str(watermark.path), "-frames:v", "1", "-vf", f"scale={w}:{h}", "-f", "rawvideo",
         "-pix_fmt", "rgba", "-"]
    )  # fmt: skip
    alpha = np.frombuffer(rgba, dtype=np.uint8)[3::4].astype(np.float64)
    if luma.size != alpha.size or alpha.std() == 0 or luma.std() == 0:
        return 0.0
    # Svijetli žig na tamnoj pozadini daje r blizu 1, tamni na svijetloj blizu -1; oboje znači
    # da je oblik žiga u kadru. Žig iste svjetline kao pozadina ostaje neprepoznat.
    return abs(float(np.corrcoef(luma, alpha)[0, 1]))


def check_captions(ass_path: Path, words: list[Word], start_s: float) -> list[str]:
    """Svaki titl mora početi na vremenu neke riječi (± 100 ms), relativno na početak isječka."""
    if not ass_path.is_file():
        return [f"titlovi: nema datoteke {ass_path.name}"]
    subs = pysubs2.load(str(ass_path), encoding="utf-8")
    events = [e for e in subs.events if e.style == STYLE_NAME]
    if words and not events:
        return ["titlovi: nema nijednog titla"]
    starts = np.array([w.start - start_s for w in words]) if words else np.array([0.0])
    bad = 0
    worst = 0.0
    for event in events:
        delta = float(np.min(np.abs(starts - event.start / 1000.0)))
        if delta > CAPTION_TOLERANCE_S:
            bad += 1
            worst = max(worst, delta)
    if bad:
        return [f"titlovi: {bad} od {len(events)} događaja kasni ili rani (najviše {worst:.2f} s)"]
    return []
