"""Prijepis kao riječi s vremenima: zajednički rječnik cijelog lanca.

Claude bira indekse riječi, program iz njih računa vremena (ADR-005).
Po uzoru na artbyjazi/autoclip (MIT, Jad Ghazi), bez diarizacije.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

#: Riječ koja završava jednim od ovih znakova zatvara rečenicu; tu najradije režemo.
SENTENCE_END = re.compile(r"[.!?…]+[\"'”’)\]]*$")


@dataclass(frozen=True)
class Word:
    text: str
    start: float
    end: float

    @property
    def duration(self) -> float:
        return self.end - self.start

    @property
    def ends_sentence(self) -> bool:
        return bool(SENTENCE_END.search(self.text.strip()))


@dataclass
class Transcript:
    words: list[Word] = field(default_factory=list)
    language: str = "en"
    model: str = ""

    def __len__(self) -> int:
        return len(self.words)

    @property
    def duration(self) -> float:
        return self.words[-1].end if self.words else 0.0

    def _clamp(self, first: int, last: int) -> tuple[int, int]:
        top = len(self.words) - 1
        first = max(0, min(first, top))
        last = max(first, min(last, top))
        return first, last

    def time_range(self, first_word: int, last_word: int) -> tuple[float, float]:
        """`(start, end)` u sekundama za uključiv raspon indeksa, stegnut na prijepis."""
        if not self.words:
            return (0.0, 0.0)
        first, last = self._clamp(first_word, last_word)
        return (self.words[first].start, self.words[last].end)

    def slice(self, first_word: int, last_word: int) -> list[Word]:
        if not self.words:
            return []
        first, last = self._clamp(first_word, last_word)
        return self.words[first : last + 1]

    def text_between(self, first_word: int, last_word: int) -> str:
        return " ".join(w.text.strip() for w in self.slice(first_word, last_word)).strip()

    def indices_in_range(self, start_s: float, end_s: float) -> tuple[int, int] | None:
        """Indeksi prve i zadnje riječi koje cijele leže u `[start_s, end_s]`, ili `None`."""
        inside = [i for i, w in enumerate(self.words) if w.start >= start_s and w.end <= end_s]
        if not inside:
            return None
        return inside[0], inside[-1]

    def sentence_end_indices(self) -> list[int]:
        return [i for i, w in enumerate(self.words) if w.ends_sentence]

    def to_dict(self) -> dict[str, Any]:
        return {
            "language": self.language,
            "model": self.model,
            "words": [asdict(w) for w in self.words],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Transcript:
        return cls(
            words=[Word(w["text"], float(w["start"]), float(w["end"])) for w in data["words"]],
            language=data.get("language", "en"),
            model=data.get("model", ""),
        )

    def save(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path) -> Transcript:
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
