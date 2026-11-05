from pathlib import Path

import pytest

from clipping.asr import SegmentTokens, tokens_to_words

GOLDEN_WAV = Path("data/izvori/JvLklMRThYs/audio.wav")


def test_tokens_to_words_basic() -> None:
    seg = SegmentTokens(10.0, 12.0, [" Hel", "lo", " world", "."], [0.0, 0.2, 0.6, 0.9])
    w = tokens_to_words([seg])
    assert [x.text for x in w] == ["Hello", "world."]
    assert w[0].start == pytest.approx(10.0) and w[0].end == pytest.approx(10.6)
    assert w[1].start == pytest.approx(10.6) and w[1].end == pytest.approx(12.0)


def test_words_absolute_across_segments() -> None:
    a = SegmentTokens(0.0, 1.0, [" a"], [0.1])
    b = SegmentTokens(70.0, 71.0, [" b"], [0.2])
    w = tokens_to_words([a, b])
    assert w[0].end == pytest.approx(1.0)
    assert w[1].start == pytest.approx(70.2) and w[1].end == pytest.approx(71.0)


def test_tokens_to_words_skips_empty_and_leading_piece_without_space() -> None:
    seg = SegmentTokens(0.0, 2.0, ["Hi", "", " there", " "], [0.0, 0.1, 0.5, 0.9])
    w = tokens_to_words([seg])
    assert [x.text for x in w] == ["Hi", "there"]
    assert w[0].end == pytest.approx(0.5) and w[1].end == pytest.approx(2.0)


def test_tokens_to_words_monotonic_even_if_timestamps_go_backwards() -> None:
    seg = SegmentTokens(0.0, 1.0, [" a", " b"], [0.6, 0.4])
    w = tokens_to_words([seg])
    assert w[0].start <= w[0].end <= w[1].start <= w[1].end


@pytest.mark.golden
def test_transcribe_30s_of_golden(tmp_path: Path) -> None:
    if not GOLDEN_WAV.exists():
        pytest.skip("nema zlatnog audio.wav")
    from clipping.asr import transcribe
    from clipping.ffmpeg import run

    clip = tmp_path / "30s.wav"
    run(["-i", str(GOLDEN_WAV), "-t", "30", "-c:a", "pcm_s16le", str(clip)])
    t = transcribe(clip)
    assert len(t.words) >= 50
    starts = [w.start for w in t.words]
    assert starts == sorted(starts)
    assert all(w.end >= w.start for w in t.words)
    assert t.words[-1].end <= 30.5
    assert t.model == "parakeet-tdt-0.6b-v3"
