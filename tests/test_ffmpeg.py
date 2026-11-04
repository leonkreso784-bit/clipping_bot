from pathlib import Path

import pytest

from clipping.ffmpeg import FFmpegError, ffmpeg_path, ffprobe_path, probe, run


def test_binaries_found() -> None:
    assert ffmpeg_path().lower().endswith(("ffmpeg", "ffmpeg.exe"))
    assert ffprobe_path().lower().endswith(("ffprobe", "ffprobe.exe"))


def test_probe_synthetic(synthetic_video: Path) -> None:
    info = probe(synthetic_video)
    assert abs(info.duration_s - 8.0) < 0.2
    assert (info.width, info.height) == (1280, 720)
    assert abs(info.fps - 30.0) < 0.01
    assert info.has_audio


def test_run_raises_on_bad_args(tmp_path: Path) -> None:
    with pytest.raises(FFmpegError) as exc:
        run(["-i", str(tmp_path / "nema.mp4"), "-f", "null", "-"])
    assert "nema.mp4" in str(exc.value)
