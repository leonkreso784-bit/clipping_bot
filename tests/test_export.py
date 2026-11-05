from pathlib import Path

import pytest

from clipping import ffmpeg
from clipping.captions import PRESETS
from clipping.export import (
    ExportRequest,
    build_filtergraph,
    export_clip,
    watermark_position,
    watermark_render_size,
)
from clipping.profile import Watermark
from clipping.reframe.croppath import centre_crop
from clipping.transcript import Word

ZIG = Path("tests/fixtures/zig_test.png")
WORDS = [Word("Hello", 1.0, 1.4), Word("there.", 1.5, 1.9), Word("Shit", 2.0, 2.4)]


def _request(
    synthetic_video: Path, tmp_path: Path, *, watermark: Watermark | None
) -> ExportRequest:
    return ExportRequest(
        source=synthetic_video,
        destination=tmp_path / "out" / "isjecak.mp4",
        start_s=1.0,
        end_s=3.0,
        crop_path=centre_crop(1280, 720, 2.0),
        words=WORDS,
        style=PRESETS["bold_pop"],
        watermark=watermark,
        top_text="Toronto",
        mask_profanity=True,
    )


def test_watermark_position_expressions() -> None:
    assert watermark_position("centar") == "(W-w)/2:(H-h)/2"
    assert watermark_position("dolje_desno") == "W-w-40:H-h-40"
    assert watermark_position("gore_lijevo") == "40:40"


def test_watermark_render_size_never_upscales() -> None:
    assert watermark_render_size(64, 64, 1080) == (64, 64)
    assert watermark_render_size(2000, 1000, 1080) == (324, 162)


def test_filtergraph_contains_overlay_and_ass(synthetic_video: Path, tmp_path: Path) -> None:
    req = _request(synthetic_video, tmp_path, watermark=Watermark(datoteka=ZIG, polozaj="centar"))
    graph = build_filtergraph(
        req, subtitle_name="captions.ass", fonts_name="fonts", watermark_input_index=1
    )
    assert "[1:v]format=rgba,colorchannelmixer=aa=0.85" in graph
    assert "overlay=(W-w)/2:(H-h)/2" in graph
    assert graph.index("overlay=") < graph.index("ass=filename=captions.ass:fontsdir=fonts")
    assert graph.endswith("[vout]")


def test_filtergraph_without_watermark_has_no_overlay(
    synthetic_video: Path, tmp_path: Path
) -> None:
    req = _request(synthetic_video, tmp_path, watermark=None)
    graph = build_filtergraph(
        req, subtitle_name="captions.ass", fonts_name="fonts", watermark_input_index=None
    )
    assert "overlay" not in graph and "ass=filename=captions.ass" in graph


def test_export_synthetic_clip_properties(synthetic_video: Path, tmp_path: Path) -> None:
    req = _request(synthetic_video, tmp_path, watermark=Watermark(datoteka=ZIG, polozaj="centar"))
    out = export_clip(req, work_dir=tmp_path / "radno")
    info = ffmpeg.probe(out)
    assert (info.width, info.height) == (1080, 1920)
    assert info.fps == pytest.approx(30, abs=0.01)
    assert info.has_audio
    assert info.duration_s == pytest.approx(2.0, abs=0.1)
    ass = (tmp_path / "radno" / "isjecak" / "captions.ass").read_text(encoding="utf-8")
    assert "S***" in ass and "Toronto" in ass


def test_export_without_watermark_has_no_overlay(synthetic_video: Path, tmp_path: Path) -> None:
    req = _request(synthetic_video, tmp_path, watermark=None)
    out = export_clip(req, work_dir=tmp_path / "radno")
    assert out.is_file() and out.stat().st_size > 0
