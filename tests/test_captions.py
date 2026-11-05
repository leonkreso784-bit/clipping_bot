from pathlib import Path

import pytest

from clipping.captions import FONT_DIR, PRESETS, TOP_STYLE_NAME, build_ass, write_ass
from clipping.profile import load_profile
from clipping.transcript import Word

FIXTURE = Path(__file__).parent / "fixtures" / "kampanja_test.yaml"

WORDS = [
    Word("What", 100.0, 100.2),
    Word("the", 100.25, 100.4),
    Word("shit,", 100.45, 100.9),
    Word("man.", 101.0, 101.4),
    Word("Really", 101.9, 102.3),
    Word("now", 102.35, 102.6),
]


def test_presets_have_fonts_on_disk() -> None:
    assert {"bold_pop", "clean_lower", "boxed"} <= set(PRESETS)
    for style in PRESETS.values():
        assert (FONT_DIR / style.font_file).is_file(), style.font_file


def test_events_follow_word_times() -> None:
    subs = build_ass(WORDS, PRESETS["bold_pop"], width=1080, height=1920, time_offset_s=100.0)
    dialogue = [e for e in subs.events if e.style != TOP_STYLE_NAME]
    assert dialogue[0].start == pytest.approx(0, abs=10)  # ms
    assert dialogue[1].start == pytest.approx(250, abs=10)


def test_profanity_masked_in_text() -> None:
    subs = build_ass(WORDS, PRESETS["bold_pop"], width=1080, height=1920, time_offset_s=100.0)
    texts = " ".join(e.text for e in subs.events)
    assert "SHIT" not in texts and "shit" not in texts
    assert "S***," in texts


def test_profanity_kept_when_not_masking() -> None:
    subs = build_ass(
        WORDS,
        PRESETS["clean_lower"],
        width=1080,
        height=1920,
        time_offset_s=100.0,
        mask_profanity=False,
    )
    assert "shit," in " ".join(e.text for e in subs.events)


def test_top_text_event_spans_clip() -> None:
    subs = build_ass(
        WORDS, PRESETS["bold_pop"], width=1080, height=1920, time_offset_s=100.0, top_text="Toronto"
    )
    top = [e for e in subs.events if e.style == TOP_STYLE_NAME]
    assert len(top) == 1 and top[0].text == "Toronto"
    assert top[0].start == 0 and top[0].end >= 2600
    assert subs.styles[TOP_STYLE_NAME].alignment == 8
    assert subs.styles[TOP_STYLE_NAME].marginv == round(0.12 * 1920)


def test_style_rotation_uses_profile() -> None:
    profile = load_profile(FIXTURE)
    assert PRESETS[profile.caption_style_for(0)].font == "Anton"
    assert PRESETS[profile.caption_style_for(1)].font == "Inter"


def test_clean_lower_has_no_per_word_events() -> None:
    subs = build_ass(WORDS, PRESETS["clean_lower"], width=1080, height=1920, time_offset_s=100.0)
    assert len(subs.events) <= 2  # grupe, ne riječi
    assert "\fscx" not in " ".join(e.text for e in subs.events)


def test_bold_pop_emits_event_per_word() -> None:
    subs = build_ass(WORDS, PRESETS["bold_pop"], width=1080, height=1920, time_offset_s=100.0)
    assert len(subs.events) == len(WORDS)


def test_write_ass_scales_font_to_height(tmp_path: Path) -> None:
    out = write_ass(
        tmp_path / "t.ass", WORDS, PRESETS["bold_pop"], width=1080, height=1920, time_offset_s=100.0
    )
    text = out.read_text(encoding="utf-8")
    assert "PlayResY: 1920" in text and f",{round(1920 * 0.062)}," in text
