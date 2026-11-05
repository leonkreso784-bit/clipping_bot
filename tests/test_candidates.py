from typing import Any

from clipping.candidates import CANDIDATES_JSON_SCHEMA, Candidate, validate_candidates
from clipping.profile import ClipRules, Range
from clipping.transcript import Transcript, Word

RULES = ClipRules(trajanje_s=Range(min=20, max=90), jezik="en")


def _transcript(n: int) -> Transcript:
    return Transcript([Word(f"w{i}.", float(i), i + 0.8) for i in range(n)])


def _raw(start: int, end: int, ocjena: int = 80, **extra: Any) -> dict[str, Any]:
    return {
        "start_word_index": start,
        "end_word_index": end,
        "naslov": "Naslov",
        "udica": "Udica",
        "ocjena": ocjena,
        "razlog": "jer",
        "opis": "opis",
        **extra,
    }


def test_schema_requires_kandidati() -> None:
    assert "kandidati" in CANDIDATES_JSON_SCHEMA["required"]
    props = CANDIDATES_JSON_SCHEMA["properties"]["kandidati"]["items"]["properties"]
    assert {"start_word_index", "end_word_index", "naslov", "udica", "ocjena"} <= set(props)


def test_accepts_valid_candidate() -> None:
    ok, rejected = validate_candidates({"kandidati": [_raw(0, 30)]}, _transcript(200), RULES)
    assert rejected == []
    assert ok == [Candidate(**_raw(0, 30))]


def test_rejects_out_of_range() -> None:
    ok, rejected = validate_candidates({"kandidati": [_raw(0, 10)]}, _transcript(5), RULES)
    assert ok == [] and len(rejected) == 1
    assert "10" in rejected[0] and "5" in rejected[0]


def test_rejects_end_before_start() -> None:
    ok, rejected = validate_candidates({"kandidati": [_raw(30, 30)]}, _transcript(100), RULES)
    assert ok == [] and "end_word_index" in rejected[0]


def test_rejects_overlap_over_half() -> None:
    raw = {"kandidati": [_raw(0, 100, ocjena=80), _raw(40, 140, ocjena=90)]}
    ok, rejected = validate_candidates(raw, _transcript(200), RULES)
    assert [c.ocjena for c in ok] == [90]
    assert len(rejected) == 1 and "prekl" in rejected[0]


def test_keeps_small_overlap() -> None:
    raw = {"kandidati": [_raw(0, 100), _raw(90, 190)]}
    ok, _ = validate_candidates(raw, _transcript(200), RULES)
    assert len(ok) == 2


def test_rejects_invalid_fields_without_raising() -> None:
    raw = {"kandidati": [_raw(0, 30, ocjena=200), {"start_word_index": 0}, "nije mapa"]}
    ok, rejected = validate_candidates(raw, _transcript(200), RULES)
    assert ok == [] and len(rejected) == 3


def test_rejects_duration_far_outside_rules() -> None:
    raw = {"kandidati": [_raw(0, 3), _raw(0, 190)]}  # 3,8 s i 190,8 s uz pravila 20–90
    ok, rejected = validate_candidates(raw, _transcript(200), RULES)
    assert ok == [] and len(rejected) == 2


def test_missing_kandidati_key() -> None:
    ok, rejected = validate_candidates({"clips": []}, _transcript(10), RULES)
    assert ok == [] and rejected and "kandidati" in rejected[0]
