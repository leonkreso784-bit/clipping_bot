from pathlib import Path
from typing import Any

import pytest

from clipping.profile import load_profile
from clipping.review import (
    REVIEW_SCHEMA,
    PregledRow,
    build_review_prompt,
    clip_thumbnails,
    independent_review,
    write_pregled,
)

PROFILE = load_profile(Path(__file__).parent / "fixtures" / "kampanja_test.yaml")


def _row(redni: int, qa_ok: bool | None, nalazi: list[str]) -> PregledRow:
    return PregledRow(
        redni=redni,
        datoteka=f"isjecci/{redni:02d}_bold_pop.mp4",
        trajanje_s=42.0,
        stil="bold_pop",
        platforme=["tiktok", "instagram"],
        naslov="n",
        udica="Ona | kaže",
        ocjena_izbora=80,
        pregled_ocjena=None if qa_ok is None else 70,
        pregled_problemi=[],
        qa_ok=qa_ok,
        qa_nalazi=nalazi,
    )


def test_pregled_table_has_all_clips(tmp_path: Path) -> None:
    rows = [_row(1, True, []), _row(2, False, ["žig nedostaje"]), _row(3, None, [])]
    path = write_pregled(tmp_path, "20261105-test-abcd", rows, ["„x”: duplikat"])
    text = path.read_text(encoding="utf-8")
    assert "clipping odobri 20261105-test-abcd --izbaci 3,7" in text
    table = [line for line in text.splitlines() if line.startswith("| ") and "isjecci/" in line]
    assert len(table) == 3
    assert "Ona \\| kaže" in table[0]  # okomita crta ne lomi tablicu
    assert "PAO: žig nedostaje" in table[1] and "nije provjeren" in table[2]
    assert "## Odbijeni kandidati" in text and "duplikat" in text


def test_review_parses_fake_runner(tmp_path: Path) -> None:
    seen: dict[str, Any] = {}

    def runner(prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        seen["prompt"], seen["schema"] = prompt, schema
        return {"ocjena": 64, "problemi": ["počinje usred misli"]}

    frame = tmp_path / "a.jpg"
    review = independent_review(
        "she spent fifteen thousand", PROFILE, [frame],
        naslov="Slika", udica="She spent $15,300", trajanje_s=55.0, runner=runner,
    )  # fmt: skip
    assert review.ocjena == 64 and review.problemi == ["počinje usred misli"]
    assert seen["schema"] is REVIEW_SCHEMA
    assert "Testni Kreator" in seen["prompt"] and str(frame.resolve()) in seen["prompt"]
    assert "she spent fifteen thousand" in seen["prompt"]


def test_review_rejects_bad_score() -> None:
    with pytest.raises(ValueError):
        independent_review(
            "t", PROFILE, [], naslov="n", udica="u", trajanje_s=1.0,
            runner=lambda p, s: {"ocjena": 300, "problemi": []},
        )  # fmt: skip


def test_review_prompt_without_frames() -> None:
    prompt = build_review_prompt(
        PROFILE, clip_text="t", naslov="n", udica="u", trajanje_s=30, thumbnails=[]
    )
    assert "(no frames)" in prompt


def test_clip_thumbnails(synthetic_video: Path, tmp_path: Path) -> None:
    frames = clip_thumbnails(synthetic_video, tmp_path, duration_s=8.0)
    assert len(frames) == 3 and all(f.stat().st_size > 0 for f in frames)
