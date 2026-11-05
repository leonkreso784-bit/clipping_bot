"""Zajedničke fixture: sintetički video iz FFmpeg lavfi, bez stvarnih medija."""

from __future__ import annotations

from pathlib import Path

import pytest

from clipping.ffmpeg import run


@pytest.fixture(scope="session")
def synthetic_video(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """8 s, 1280×720, 30 fps, testsrc2 + sinus 440 Hz, H.264/AAC."""
    out = tmp_path_factory.mktemp("media") / "sintetski.mp4"
    run(
        [
            "-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=30",
            "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000",
            "-t", "8",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            str(out),
        ]
    )  # fmt: skip
    return out
