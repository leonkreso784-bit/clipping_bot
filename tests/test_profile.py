from pathlib import Path
from typing import Any

import pytest
import yaml

from clipping.profile import ProfileError, load_profile

FIXTURE = Path(__file__).parent / "fixtures" / "kampanja_test.yaml"


def _variant(tmp_path: Path, mutate: Any) -> Path:
    data = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    mutate(data)
    out = tmp_path / "kampanja.yaml"
    out.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return out


def test_loads_fixture() -> None:
    p = load_profile(FIXTURE)
    assert p.slug == "test"
    assert p.platforme == ["tiktok", "instagram"]
    assert p.grafika.zig is not None and p.grafika.zig.polozaj == "centar"
    assert p.isjecak.trajanje_s.min == 20 and p.isjecak.trajanje_s.max == 90
    assert p.pravila_sadrzaja.psovke.titlovi == "zvjezdice"


def test_profile_requires_watermark_file(tmp_path: Path) -> None:
    def mutate(d: dict[str, Any]) -> None:
        d["grafika"]["zig"]["datoteka"] = "tests/fixtures/nema.png"

    with pytest.raises(ProfileError, match="nema.png"):
        load_profile(_variant(tmp_path, mutate))


def test_rejects_unknown_platform(tmp_path: Path) -> None:
    def mutate(d: dict[str, Any]) -> None:
        d["platforme"] = ["facebook"]

    with pytest.raises(ProfileError, match="facebook"):
        load_profile(_variant(tmp_path, mutate))


def test_rejects_account_for_platform_not_in_list(tmp_path: Path) -> None:
    def mutate(d: dict[str, Any]) -> None:
        d["racuni"] = {"x": "@test"}

    with pytest.raises(ProfileError, match="platforme"):
        load_profile(_variant(tmp_path, mutate))


def test_style_rotation() -> None:
    p = load_profile(FIXTURE)  # [bold_pop, clean_lower]
    assert p.caption_style_for(0) == "bold_pop"
    assert p.caption_style_for(1) == "clean_lower"
    assert p.caption_style_for(2) == "bold_pop"


def test_rejects_unknown_caption_style(tmp_path: Path) -> None:
    def mutate(d: dict[str, Any]) -> None:
        d["pravila_sadrzaja"]["stil_titlova"] = ["a", "b"]

    with pytest.raises(ProfileError, match="stil_titlova"):
        load_profile(_variant(tmp_path, mutate))


def test_rejects_beep(tmp_path: Path) -> None:
    def mutate(d: dict[str, Any]) -> None:
        d["pravila_sadrzaja"]["psovke"]["zvuk"] = "beep"

    with pytest.raises(ProfileError, match="beep se ne gradi u V1"):
        load_profile(_variant(tmp_path, mutate))


def test_missing_file_is_profile_error(tmp_path: Path) -> None:
    with pytest.raises(ProfileError):
        load_profile(tmp_path / "nema.yaml")
