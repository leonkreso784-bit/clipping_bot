"""Kandidati za isječke: što Claude vraća i kako ih program provjerava (ADR-005).

Claude vraća samo indekse prve i zadnje riječi i tekst (naslov, udica, razlog, opis); program
odbija sve što ne stane u prijepis ili profil, ne pada i ne popravlja tiho.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clipping.profile import ClipRules
from clipping.transcript import Transcript

#: Preklapanje (po riječima) iznad kojega dva kandidata smatramo istim trenutkom (ADR-011).
MAX_OVERLAP = 0.5
#: Koliko trajanje smije odstupati od profila prije nego ga odbijemo bez pokušaja dotjerivanja;
#: `boundaries.refine` manja odstupanja slaže na granicu rečenice.
DURATION_SLACK = 1.5


class Candidate(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    start_word_index: int = Field(ge=0)
    end_word_index: int = Field(ge=0)
    naslov: str = Field(min_length=1, max_length=120)
    udica: str = Field(min_length=1, max_length=120)
    ocjena: int = Field(ge=0, le=100)
    razlog: str = ""
    opis: str = ""

    @property
    def word_count(self) -> int:
        return self.end_word_index - self.start_word_index + 1


CANDIDATES_JSON_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Kandidati za isječke",
    "type": "object",
    "required": ["kandidati"],
    "additionalProperties": False,
    "properties": {
        "kandidati": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["start_word_index", "end_word_index", "naslov", "udica", "ocjena"],
                "properties": {
                    "start_word_index": {"type": "integer", "minimum": 0},
                    "end_word_index": {"type": "integer", "minimum": 0},
                    "naslov": {"type": "string", "maxLength": 120},
                    "udica": {"type": "string", "maxLength": 120},
                    "ocjena": {"type": "integer", "minimum": 0, "maximum": 100},
                    "razlog": {"type": "string"},
                    "opis": {"type": "string"},
                },
            },
        }
    },
}


def _overlap_ratio(a: Candidate, b: Candidate) -> float:
    shared = min(a.end_word_index, b.end_word_index) - max(a.start_word_index, b.start_word_index)
    if shared < 0:
        return 0.0
    return (shared + 1) / min(a.word_count, b.word_count)


def validate_candidates(
    raw: dict[str, Any], transcript: Transcript, rules: ClipRules
) -> tuple[list[Candidate], list[str]]:
    """Vrati prihvaćene kandidate (po `ocjena` silazno) i razloge odbijanja na hrvatskom."""
    rejected: list[str] = []
    items = raw.get("kandidati") if isinstance(raw, dict) else None
    if not isinstance(items, list):
        return [], ["odgovor nema popis 'kandidati'"]

    parsed: list[Candidate] = []
    for i, item in enumerate(items):
        try:
            cand = Candidate.model_validate(item)
        except ValidationError as exc:
            problems = "; ".join(
                f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()
            )
            rejected.append(f"kandidat {i}: neispravna polja ({problems})")
            continue
        n = len(transcript)
        if cand.end_word_index >= n or cand.start_word_index >= n:
            rejected.append(
                f"kandidat {i}: indeks {max(cand.start_word_index, cand.end_word_index)} "
                f"izvan prijepisa od {n} riječi"
            )
            continue
        if cand.end_word_index <= cand.start_word_index:
            rejected.append(
                f"kandidat {i}: end_word_index {cand.end_word_index} nije iza "
                f"start_word_index {cand.start_word_index}"
            )
            continue
        start_s, end_s = transcript.time_range(cand.start_word_index, cand.end_word_index)
        duration = end_s - start_s
        lo = rules.trajanje_s.min / DURATION_SLACK
        hi = rules.trajanje_s.max * DURATION_SLACK
        if not lo <= duration <= hi:
            rejected.append(
                f"kandidat {i}: trajanje {duration:.1f} s predaleko od profila "
                f"{rules.trajanje_s.min:g}–{rules.trajanje_s.max:g} s"
            )
            continue
        parsed.append(cand)

    accepted: list[Candidate] = []
    for cand in sorted(parsed, key=lambda c: c.ocjena, reverse=True):
        clash = next((a for a in accepted if _overlap_ratio(a, cand) > MAX_OVERLAP), None)
        if clash is not None:
            rejected.append(
                f"kandidat {cand.start_word_index}–{cand.end_word_index} se preklapa više od "
                f"{MAX_OVERLAP:.0%} s kandidatom {clash.start_word_index}–{clash.end_word_index} "
                f"(ocjena {clash.ocjena} ≥ {cand.ocjena})"
            )
            continue
        accepted.append(cand)
    return accepted, rejected
