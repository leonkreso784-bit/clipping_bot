import json
from pathlib import Path
from typing import Any

import pytest

from clipping.candidates import CANDIDATES_JSON_SCHEMA
from clipping.profile import load_profile
from clipping.select.claude_runner import (
    SelectionError,
    build_prompt,
    load_candidates,
    run_claude,
    select_candidates,
)
from clipping.select.window import write_window
from clipping.transcript import Transcript, Word

FIXTURES = Path(__file__).parent / "fixtures"
FAKE = str(FIXTURES / "fake_claude.py")
PROFILE = load_profile(FIXTURES / "kampanja_test.yaml")


def _transcript(n_sentences: int = 40) -> Transcript:
    """Rečenice od 10 riječi po 0.5 s = 5 s; kandidat od 6 rečenica traje 30 s."""
    words: list[Word] = []
    t = 0.0
    for s in range(n_sentences):
        for k in range(10):
            text = f"w{s}_{k}" + ("." if k == 9 else "")
            words.append(Word(text, t, t + 0.45))
            t += 0.5
    return Transcript(words, "en", "test")


def _cand(start: int, end: int, ocjena: int = 70) -> dict[str, Any]:
    return {"start_word_index": start, "end_word_index": end, "naslov": "n", "udica": "u",
            "ocjena": ocjena, "razlog": "r", "opis": "o"}  # fmt: skip


def _good_six() -> dict[str, Any]:
    return {"kandidati": [_cand(i * 60, i * 60 + 59) for i in range(6)]}


def test_run_claude_parses_structured_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_CLAUDE_OUTPUT", json.dumps({"kandidati": [_cand(0, 5)]}))
    monkeypatch.setenv("FAKE_CLAUDE_ARGS", str(tmp_path / "args.json"))
    out = run_claude("uputa", CANDIDATES_JSON_SCHEMA, exe=FAKE)
    assert out["kandidati"][0]["start_word_index"] == 0
    argv = json.loads((tmp_path / "args.json").read_text(encoding="utf-8"))["argv"]
    sent = json.loads(argv[argv.index("--json-schema") + 1])
    assert "$schema" not in sent and sent["required"] == ["kandidati"]
    assert "-p" in argv and argv[argv.index("--output-format") + 1] == "json"
    assert argv[argv.index("--setting-sources") + 1] == ""
    assert "--strict-mcp-config" in argv


def test_run_claude_raises_on_exit_code(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FAKE_CLAUDE_EXIT", "3")
    with pytest.raises(SelectionError, match="kodom 3"):
        run_claude("uputa", {}, exe=FAKE)


def test_prompt_has_rules_window_and_feedback(tmp_path: Path) -> None:
    window = write_window(_transcript(2), tmp_path / "window.txt")
    prompt = build_prompt(PROFILE, window, feedback=["kandidat 0: indeks 99999 izvan prijepisa"])
    assert "Testni Kreator" in prompt and "ismijavanje gosta" in prompt
    assert "[0]w0_0" in prompt and "between 20 and 90 seconds" in prompt
    assert "indeks 99999" in prompt


def test_rejects_out_of_range(tmp_path: Path) -> None:
    t = _transcript()
    window = write_window(t, tmp_path / "window.txt")
    answers = [{"kandidati": [_cand(0, 99999)]}, _good_six()]
    prompts: list[str] = []

    def runner(prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        prompts.append(prompt)
        return answers[len(prompts) - 1]

    got = select_candidates(t, PROFILE, tmp_path, window_path=window, runner=runner, log=print)
    assert len(got) == 6 and len(prompts) == 2
    assert "99999" in prompts[1]
    assert len(load_candidates(tmp_path / "candidates.json")) == 6


def test_retries_then_fails(tmp_path: Path) -> None:
    t = _transcript()
    window = write_window(t, tmp_path / "window.txt")
    calls: list[int] = []

    def runner(prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        calls.append(1)
        return {"kandidati": [_cand(0, 59)]}

    with pytest.raises(SelectionError, match="3 pokušaja"):
        select_candidates(t, PROFILE, tmp_path, window_path=window, runner=runner, log=print)
    assert len(calls) == 3
    assert not (tmp_path / "candidates.json").exists()
