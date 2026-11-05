from pathlib import Path

from clipping.transcript import Transcript, Word


def test_roundtrip_json(tmp_path: Path) -> None:
    t = Transcript([Word("Hi.", 0.0, 0.3), Word("there", 0.4, 0.7)], "en", "test")
    t.save(tmp_path / "t.json")
    assert Transcript.load(tmp_path / "t.json") == t


def test_sentence_ends() -> None:
    t = Transcript([Word("Hi.", 0, 0.3), Word("Go!", 0.4, 0.7), Word("now", 0.8, 1)], "en", "x")
    assert t.sentence_end_indices() == [0, 1]
    assert t.words[0].ends_sentence and not t.words[2].ends_sentence


def test_time_range_clamps() -> None:
    t = Transcript([Word("a", 0, 1), Word("b", 1, 2)], "en", "x")
    assert t.time_range(-5, 99) == (0.0, 2.0)
    assert t.duration == 2.0


def test_slice_and_text_between() -> None:
    t = Transcript([Word("a", 0, 1), Word("b,", 1, 2), Word("c.", 2, 3)], "en", "x")
    assert [w.text for w in t.slice(1, 2)] == ["b,", "c."]
    assert t.text_between(0, 2) == "a b, c."
    assert len(t) == 3


def test_empty_transcript_is_safe() -> None:
    t = Transcript([], "en", "x")
    assert t.duration == 0.0 and t.time_range(0, 0) == (0.0, 0.0) and t.slice(0, 5) == []


def test_indices_in_range_picks_words_inside_window() -> None:
    t = Transcript([Word("a", 0, 1), Word("b", 1, 2), Word("c", 2, 3), Word("d", 3, 4)], "en", "x")
    assert t.indices_in_range(0.9, 3.1) == (1, 2)  # b i c leže unutar [0.9, 3.1]
    assert t.indices_in_range(1.5, 1.6) is None  # nijedna riječ cijela unutra
    assert t.indices_in_range(-1, 99) == (0, 3)
