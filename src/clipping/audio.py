"""Zvuk za prijepis (16 kHz mono WAV), tišine za granice rezova, sličice za pregled.

Po uzoru na artbyjazi/autoclip (MIT, Jad Ghazi), `pipeline/prepare.py`.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from clipping import ffmpeg

AUDIO_SAMPLE_RATE = 16_000
THUMBNAIL_INTERVAL_S = 15
THUMBNAIL_WIDTH = 320


@dataclass(frozen=True)
class Silence:
    start: float
    end: float

    @property
    def duration(self) -> float:
        return self.end - self.start


def extract_audio(source: Path, destination: Path) -> Path:
    """Mono 16 kHz PCM WAV iz bilo kojeg ulaza; isto što Parakeet očekuje."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg.run(
        [
            "-i",
            str(source),
            "-vn",
            "-ac",
            "1",
            "-ar",
            str(AUDIO_SAMPLE_RATE),
            "-c:a",
            "pcm_s16le",
            str(destination),
        ]
    )
    return destination


_SILENCE_START = re.compile(r"silence_start:\s*([-\d.]+)")
_SILENCE_END = re.compile(r"silence_end:\s*([-\d.]+)")


def detect_silences(
    audio: Path, *, noise_db: float = -32.0, min_duration_s: float = 0.2
) -> list[Silence]:
    """Tihi rasponi iz FFmpeg `silencedetect`; rez unutar tišine zvuči namjerno."""
    command = [
        ffmpeg.ffmpeg_path(),
        "-hide_banner",
        "-nostdin",
        "-i",
        str(audio),
        "-af",
        f"silencedetect=noise={noise_db}dB:d={min_duration_s}",
        "-f",
        "null",
        "-",
    ]
    proc = subprocess.run(
        command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False
    )
    if proc.returncode != 0:
        raise ffmpeg.FFmpegError(f"silencedetect je pao za {audio.name}:\n{proc.stderr[-800:]}")

    silences: list[Silence] = []
    pending_start: float | None = None
    for line in proc.stderr.splitlines():
        if match := _SILENCE_START.search(line):
            pending_start = float(match.group(1))
        elif match := _SILENCE_END.search(line):
            end = float(match.group(1))
            start = pending_start if pending_start is not None else end
            silences.append(Silence(start=max(0.0, start), end=end))
            pending_start = None
    return silences


def save_silences(path: Path, silences: list[Silence]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([asdict(s) for s in silences]), encoding="utf-8")
    return path


def load_silences(path: Path) -> list[Silence]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [Silence(float(s["start"]), float(s["end"])) for s in raw]


def generate_thumbnails(
    source: Path,
    destination_dir: Path,
    *,
    interval_s: int = THUMBNAIL_INTERVAL_S,
    width: int = THUMBNAIL_WIDTH,
) -> list[Path]:
    """Jedna JPEG sličica svakih `interval_s` sekundi, kronološki."""
    destination_dir.mkdir(parents=True, exist_ok=True)
    pattern = destination_dir / "slicica_%05d.jpg"
    ffmpeg.run(
        [
            "-i",
            str(source),
            "-vf",
            f"fps=1/{interval_s},scale={width}:-2",
            "-q:v",
            "5",
            str(pattern),
        ]
    )
    return sorted(destination_dir.glob("slicica_*.jpg"))
