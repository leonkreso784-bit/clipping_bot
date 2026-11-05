from clipping.audio import Silence
from clipping.boundaries import refine
from clipping.transcript import Transcript, Word


def _transcript(n: int = 40, *, sentence_every: int | None = 10) -> Transcript:
    words = []
    for i in range(n):
        text = f"w{i}"
        if sentence_every and (i + 1) % sentence_every == 0:
            text += "."
        words.append(Word(text, float(i), i + 0.8))
    return Transcript(words)


def test_refine_snaps_to_sentence() -> None:
    b = refine(_transcript(), 12, 25, silences=[], min_duration_s=5, max_duration_s=60)
    assert b is not None
    assert (b.start_word, b.end_word) == (10, 29)


def test_refine_none_when_too_long_without_sentence() -> None:
    b = refine(
        _transcript(sentence_every=None), 0, 39, silences=[], min_duration_s=5, max_duration_s=10
    )
    assert b is None


def test_refine_clamps_to_fitting_sentence() -> None:
    b = refine(_transcript(), 0, 39, silences=[], min_duration_s=5, max_duration_s=25)
    assert b is not None
    assert b.end_word == 19 and b.end_s - b.start_s <= 25


def test_refine_aligns_into_silence() -> None:
    silences = [Silence(9.0, 9.95), Silence(29.85, 30.9)]
    b = refine(_transcript(), 10, 29, silences=silences, min_duration_s=5, max_duration_s=60)
    assert b is not None
    assert 9.0 <= b.start_s < 10.0
    assert 29.8 < b.end_s <= 30.9


def test_refine_fallback_padding_without_silence() -> None:
    b = refine(_transcript(), 10, 29, silences=[], min_duration_s=5, max_duration_s=60)
    assert b is not None
    assert b.start_s < 10.0 and b.end_s > 29.8


def test_refine_empty_transcript() -> None:
    assert refine(Transcript(), 0, 5, silences=[], min_duration_s=1, max_duration_s=5) is None
