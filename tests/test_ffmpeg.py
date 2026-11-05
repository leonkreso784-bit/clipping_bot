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


def test_fps_parsing_handles_vfr_and_zero_division() -> None:
    from clipping.ffmpeg import _fps, _pick_fps

    assert _fps("30000/1001") == pytest.approx(29.97, abs=0.01)
    assert _fps("0/0") == 0.0
    assert _fps("1/0") == 0.0
    assert _fps(None) == 0.0
    # avg_frame_rate "0/0" (VFR) mora pasti na r_frame_rate
    assert _pick_fps({"avg_frame_rate": "0/0", "r_frame_rate": "30/1"}) == 30.0
