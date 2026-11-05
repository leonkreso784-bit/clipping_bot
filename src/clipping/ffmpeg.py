"""Omotač oko FFmpeg-a i ffprobe-a: pokretanje s greškom koja nosi stderr, i podaci o mediju."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any


class FFmpegError(RuntimeError):
    """FFmpeg ili ffprobe je završio s greškom; poruka nosi stderr."""


@dataclass(frozen=True)
class MediaInfo:
    duration_s: float
    width: int
    height: int
    fps: float
    has_audio: bool
    has_video: bool


def ffmpeg_path() -> str:
    return _binary("ffmpeg")


def ffprobe_path() -> str:
    return _binary("ffprobe")


def _binary(name: str) -> str:
    found = shutil.which(name)
    if found is None:
        raise FFmpegError(f"{name} nije na PATH-u; instaliraj FFmpeg 9.")
    return found


def run(args: list[str], *, cwd: Path | None = None) -> None:
    """Pokreni `ffmpeg -hide_banner -nostdin -y <args>`; greška diže FFmpegError sa stderr-om."""
    command = [ffmpeg_path(), "-hide_banner", "-nostdin", "-y", *args]
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        tail = "\n".join(result.stderr.strip().splitlines()[-15:])
        raise FFmpegError(f"ffmpeg je pao (kod {result.returncode}):\n{tail}")


def probe(path: Path) -> MediaInfo:
    """Pročitaj trajanje, dimenzije, fps i prisutnost zvuka kroz ffprobe."""
    command = [
        ffprobe_path(),
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_streams",
        "-show_format",
        str(path),
    ]
    result = subprocess.run(
        command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False
    )
    if result.returncode != 0:
        raise FFmpegError(f"ffprobe je pao za {path.name}:\n{result.stderr.strip()}")
    data: dict[str, Any] = json.loads(result.stdout or "{}")
    streams: list[dict[str, Any]] = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = any(s.get("codec_type") == "audio" for s in streams)
    duration = float(data.get("format", {}).get("duration") or 0.0)
    return MediaInfo(
        duration_s=duration,
        width=int(video.get("width", 0)) if video else 0,
        height=int(video.get("height", 0)) if video else 0,
        fps=_pick_fps(video) if video else 0.0,
        has_audio=audio,
        has_video=video is not None,
    )


def _pick_fps(video: dict[str, Any]) -> float:
    """avg_frame_rate je "0/0" za VFR izvore; tada vrijedi r_frame_rate."""
    return _fps(video.get("avg_frame_rate")) or _fps(video.get("r_frame_rate"))


def _fps(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        return float(Fraction(value))
    except (ZeroDivisionError, ValueError):
        return 0.0
