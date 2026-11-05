from pathlib import Path

import pysubs2
import pytest

from clipping.captions import PRESETS
from clipping.export import ExportRequest, export_clip
from clipping.profile import Watermark
from clipping.qa import ClipExpectation, check_clip
from clipping.reframe.croppath import centre_crop
from clipping.transcript import Word

ZIG = Path("tests/fixtures/zig_test.png")
WORDS = [Word("Hello", 1.0, 1.4), Word("there.", 1.5, 1.9), Word("Again", 2.0, 2.4)]
START_S = 1.0


@pytest.fixture(scope="module")
def exports(synthetic_video: Path, tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    base = tmp_path_factory.mktemp("qa")
    out: dict[str, Path] = {}
    for name, wm in [("sa_zigom", Watermark(datoteka=ZIG, polozaj="centar")), ("bez_ziga", None)]:
        req = ExportRequest(
            source=synthetic_video,
            destination=base / f"{name}.mp4",
            start_s=START_S,
            end_s=3.0,
            crop_path=centre_crop(1280, 720, 2.0),
            words=WORDS,
            style=PRESETS["bold_pop"],
            watermark=wm,
        )
        out[name] = export_clip(req, work_dir=base / "radno")
        out[name + "_ass"] = base / "radno" / name / "captions.ass"
    return out


def _expect(
    exports: dict[str, Path], *, watermark: bool, ass: Path | None = None, min_s: float = 1.0
) -> ClipExpectation:
    return ClipExpectation(
        min_s=min_s,
        max_s=3.0,
        watermark=Watermark(datoteka=ZIG, polozaj="centar") if watermark else None,
        ass_path=ass or exports["sa_zigom_ass"],
        words=WORDS,
        start_s=START_S,
    )


def test_qa_passes_on_good_clip(exports: dict[str, Path]) -> None:
    report = check_clip(exports["sa_zigom"], expected=_expect(exports, watermark=True))
    assert report.ok, report.nalazi


def test_qa_fails_when_watermark_missing(exports: dict[str, Path]) -> None:
    report = check_clip(
        exports["bez_ziga"], expected=_expect(exports, watermark=True, ass=exports["bez_ziga_ass"])
    )
    assert not report.ok and any("žig" in n for n in report.nalazi)


def test_qa_fails_on_duration(exports: dict[str, Path]) -> None:
    report = check_clip(exports["sa_zigom"], expected=_expect(exports, watermark=True, min_s=5.0))
    assert not report.ok and any("trajanje" in n for n in report.nalazi)


def test_qa_fails_when_caption_shifted(exports: dict[str, Path], tmp_path: Path) -> None:
    subs = pysubs2.load(str(exports["sa_zigom_ass"]), encoding="utf-8")
    subs.shift(ms=500)
    shifted = tmp_path / "pomaknuto.ass"
    subs.save(str(shifted), encoding="utf-8")
    report = check_clip(exports["sa_zigom"], expected=_expect(exports, watermark=True, ass=shifted))
    assert not report.ok and any("titl" in n for n in report.nalazi)


def test_qa_finds_dark_watermark(synthetic_video: Path, tmp_path: Path) -> None:
    # Crni krug na prozirnom: korelacija svjetline s alfom je negativna, QA gleda |r|.
    wm = Watermark(datoteka=Path("tests/fixtures/zig_tamni_test.png"), polozaj="dolje_desno")
    req = ExportRequest(
        source=synthetic_video,
        destination=tmp_path / "tamni.mp4",
        start_s=START_S,
        end_s=3.0,
        crop_path=centre_crop(1280, 720, 2.0),
        words=WORDS,
        style=PRESETS["bold_pop"],
        watermark=wm,
    )
    out = export_clip(req, work_dir=tmp_path / "radno")
    expectation = ClipExpectation(
        min_s=1.0,
        max_s=3.0,
        watermark=wm,
        ass_path=tmp_path / "radno" / "tamni" / "captions.ass",
        words=WORDS,
        start_s=START_S,
    )
    report = check_clip(out, expected=expectation)
    assert report.ok, report.nalazi
