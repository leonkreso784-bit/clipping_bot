"""Neovisni Claude pregled isječka i `PREGLED.md` za Leona (dizajn §6, koraci 8 i 9).

Pregled ne blokira: ocjena i problemi idu u izvještaj, a odluku donosi Leon (`clipping odobri`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from string import Template
from typing import Any

from pydantic import BaseModel, Field

from clipping import ffmpeg
from clipping.profile import CampaignProfile
from clipping.select.claude_runner import Runner, run_claude

REVIEW_PROMPT = Path(__file__).parent / "select" / "review_prompt.md"
REVIEW_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["ocjena", "problemi"],
    "additionalProperties": False,
    "properties": {
        "ocjena": {"type": "integer", "minimum": 0, "maximum": 100},
        "problemi": {"type": "array", "items": {"type": "string"}},
    },
}
THUMBNAIL_FRACTIONS = (0.15, 0.5, 0.85)


class Review(BaseModel):
    ocjena: int = Field(ge=0, le=100)
    problemi: list[str] = Field(default_factory=list)


def clip_thumbnails(clip: Path, destination_dir: Path, *, duration_s: float) -> list[Path]:
    """Tri sličice gotovog isječka (15 %, 50 %, 85 % trajanja), 540 px široke."""
    destination_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for i, fraction in enumerate(THUMBNAIL_FRACTIONS, start=1):
        out = destination_dir / f"{clip.stem}_{i}.jpg"
        ffmpeg.run(
            ["-ss", f"{duration_s * fraction:.2f}", "-i", str(clip), "-frames:v", "1",
             "-vf", "scale=540:-2", "-q:v", "4", str(out)]
        )  # fmt: skip
        paths.append(out)
    return paths


def build_review_prompt(
    profile: CampaignProfile,
    *,
    clip_text: str,
    naslov: str,
    udica: str,
    trajanje_s: float,
    thumbnails: list[Path],
) -> str:
    rules = profile.isjecak.trajanje_s
    return Template(REVIEW_PROMPT.read_text(encoding="utf-8")).substitute(
        kreator=profile.kreator,
        platforme=", ".join(profile.platforme),
        min_s=f"{rules.min:g}",
        max_s=f"{rules.max:g}",
        jezik=profile.isjecak.jezik,
        zabranjeno="; ".join(profile.pravila_sadrzaja.zabranjeno) or "(nothing listed)",
        naslov=naslov,
        udica=udica,
        trajanje=f"{trajanje_s:.0f}",
        tekst=clip_text,
        slicice="\n".join(f"- {p.resolve()}" for p in thumbnails) or "- (no frames)",
    )


def independent_review(
    clip_text: str,
    profile: CampaignProfile,
    thumbnails: list[Path],
    *,
    naslov: str,
    udica: str,
    trajanje_s: float,
    runner: Runner | None = None,
) -> Review:
    prompt = build_review_prompt(
        profile,
        clip_text=clip_text,
        naslov=naslov,
        udica=udica,
        trajanje_s=trajanje_s,
        thumbnails=thumbnails,
    )
    cwd = thumbnails[0].parent if thumbnails else None
    call: Runner = runner or (
        lambda p, s: run_claude(p, s, tools="Read", max_turns=8, cwd=cwd, timeout_s=600)
    )
    return Review.model_validate(call(prompt, REVIEW_SCHEMA))


@dataclass
class PregledRow:
    redni: int
    datoteka: str
    trajanje_s: float
    stil: str
    platforme: list[str]
    naslov: str
    udica: str
    ocjena_izbora: int
    pregled_ocjena: int | None
    pregled_problemi: list[str] = field(default_factory=list)
    qa_ok: bool | None = None
    qa_nalazi: list[str] = field(default_factory=list)


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").strip()


def write_pregled(
    posao_dir: Path, posao_id: str, rows: list[PregledRow], odbijeni: list[str]
) -> Path:
    """`PREGLED.md`: upute na vrhu, tablica isječaka, popis odbijenih kandidata."""
    lines = [
        f"# Pregled posla {posao_id}",
        "",
        f"Odobri cijelu seriju: `clipping odobri {posao_id}`",
        f"Izbaci pojedine (redni brojevi): `clipping odobri {posao_id} --izbaci 3,7`",
        "",
        "Isječci s padom automatske provjere (QA) se ne odobravaju ni bez `--izbaci`.",
        "",
        "| # | isječak | trajanje | stil | platforme | udica | ocjena izbora | pregled | QA |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        review = "—" if row.pregled_ocjena is None else str(row.pregled_ocjena)
        if row.pregled_problemi:
            review += ": " + "; ".join(row.pregled_problemi)
        if row.qa_ok is None:
            qa = "nije provjeren"
        elif row.qa_ok:
            qa = "OK"
        else:
            qa = "PAO: " + "; ".join(row.qa_nalazi)
        lines.append(
            f"| {row.redni} | {_cell(row.datoteka)} | {row.trajanje_s:.0f} s | {row.stil} | "
            f"{', '.join(row.platforme)} | {_cell(row.udica)} | {row.ocjena_izbora} | "
            f"{_cell(review)} | {_cell(qa)} |"
        )
    if odbijeni:
        lines += ["", "## Odbijeni kandidati", ""]
        lines += [f"- {_cell(reason)}" for reason in odbijeni]
    path = posao_dir / "PREGLED.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
