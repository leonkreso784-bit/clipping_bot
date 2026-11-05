import json
import subprocess
from pathlib import Path

from clipping.audio import (
    Silence,
    detect_silences,
    extract_audio,
    generate_thumbnails,
    load_silences,
    save_silences,
)
from clipping.ffmpeg import ffprobe_path, probe, run


def _audio_stream(path: Path) -> dict[str, str]:
    out = subprocess.run(
        [ffprobe_path(), "-v", "error", "-print_format", "json", "-show_streams", str(path)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return next(s for s in json.loads(out)["streams"] if s["codec_type"] == "audio")


def test_extract_audio_is_16k_mono(synthetic_video: Path, tmp_path: Path) -> None:
    wav = extract_audio(synthetic_video, tmp_path / "a.wav")
    info = probe(wav)
    assert info.has_audio and not info.has_video
    assert abs(info.duration_s - 8.0) < 0.2
    stream = _audio_stream(wav)
    assert stream["sample_rate"] == "16000" and stream["channels"] == 1


def test_detect_silences_finds_gap(tmp_path: Path) -> None:
    wav = tmp_path / "gap.wav"
    # 2 s ton, 1 s tišina, 2 s ton
    run(
        [
            "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=16000:duration=2",
            "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono:d=1",
            "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=16000:duration=2",
            "-filter_complex", "[0:a][1:a][2:a]concat=n=3:v=0:a=1[a]",
            "-map", "[a]", "-ac", "1", "-c:a", "pcm_s16le", str(wav),
        ]
    )  # fmt: skip
    s = detect_silences(wav)
    assert len(s) == 1
    assert abs(s[0].start - 2.0) < 0.15 and abs(s[0].end - 3.0) < 0.15


def test_silences_roundtrip(tmp_path: Path) -> None:
    silences = [Silence(1.0, 1.5), Silence(4.25, 4.9)]
    save_silences(tmp_path / "s.json", silences)
    assert load_silences(tmp_path / "s.json") == silences


def test_thumbnails_every_interval(synthetic_video: Path, tmp_path: Path) -> None:
    thumbs = generate_thumbnails(synthetic_video, tmp_path / "t", interval_s=4)
    assert len(thumbs) == 2
    assert probe(thumbs[0]).width == 320
