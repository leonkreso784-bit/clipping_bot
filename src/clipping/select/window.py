"""Prozor prijepisa za Claudea: jedna rečenica po retku, svaka riječ s indeksom `[i]tekst`.

Claude iz prozora vraća indekse prve i zadnje riječi (ADR-005); program iz njih računa vremena.
"""

from __future__ import annotations

from pathlib import Path

from clipping.transcript import Transcript


def render_window(transcript: Transcript) -> str:
    lines: list[str] = []
    current: list[str] = []
    for index, word in enumerate(transcript.words):
        current.append(f"[{index}]{word.text.strip()}")
        if word.ends_sentence:
            lines.append(" ".join(current))
            current = []
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines) + "\n"


def write_window(transcript: Transcript, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_window(transcript), encoding="utf-8")
    return path
