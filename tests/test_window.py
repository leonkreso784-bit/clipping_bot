from pathlib import Path

from clipping.select.window import write_window
from clipping.transcript import Transcript, Word


def test_window_format(tmp_path: Path) -> None:
    words = ["Men", "are", "just", "like", "this.", "Really?", "yes"]
    t = Transcript([Word(w, i, i + 0.5) for i, w in enumerate(words)], "en", "x")
    lines = write_window(t, tmp_path / "window.txt").read_text(encoding="utf-8").splitlines()
    assert lines[0] == "[0]Men [1]are [2]just [3]like [4]this."
    assert lines[1] == "[5]Really?"
    assert lines[2] == "[6]yes"
