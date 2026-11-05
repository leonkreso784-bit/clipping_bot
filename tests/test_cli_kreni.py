"""`clipping kreni` i `clipping odobri` kroz CliRunner, s lažnim servisima i sintetičkim videom."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import pytest
import yaml
from typer.testing import CliRunner

from clipping import cli
from clipping.db import Database

FIXTURE = Path(__file__).parent / "fixtures" / "kampanja_test.yaml"


@pytest.fixture
def root(tmp_path: Path) -> Path:
    data = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    data["isjecak"]["trajanje_s"] = {"min": 1.5, "max": 4}
    (tmp_path / "kampanje").mkdir()
    (tmp_path / "kampanje" / "test.yaml").write_text(
        yaml.safe_dump(data, allow_unicode=True), encoding="utf-8"
    )
    return tmp_path


def test_kreni_refuses_platform_not_in_profile(root: Path) -> None:
    result = CliRunner().invoke(
        cli.app,
        ["kreni", "--kampanja", "test", "--platforma", "youtube", "--korijen", str(root)],
    )
    assert result.exit_code == 2
    assert "youtube nije u profilu" in result.output


def test_kreni_refuses_foreign_channel(root: Path) -> None:
    result = CliRunner().invoke(
        cli.app,
        ["kreni", "--kampanja", "test", "--izvor", "https://www.youtube.com/@drugi",
         "--korijen", str(root)],
    )  # fmt: skip
    assert result.exit_code == 2 and "nije s dopuštenog kanala" in result.output


def test_kreni_unknown_campaign(root: Path) -> None:
    result = CliRunner().invoke(cli.app, ["kreni", "--kampanja", "nema", "--korijen", str(root)])
    assert result.exit_code == 2 and "ne može pročitati" in result.output


def test_kreni_end_to_end_with_fakes(
    root: Path, synthetic_video: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from tests.test_job import Fakes

    fakes = Fakes()
    monkeypatch.setattr(cli, "make_services", fakes.services)
    source = root / "brief" / "epizoda.mp4"
    source.parent.mkdir()
    shutil.copyfile(synthetic_video, source)

    runner = CliRunner()
    result = runner.invoke(
        cli.app,
        ["kreni", "--kampanja", "test", "--izvor", str(source), "--platforma", "tiktok",
         "--korijen", str(root)],
    )  # fmt: skip
    assert result.exit_code == 0, result.output
    assert "Gotovo: 2 isječaka" in result.output
    posao = next((root / "izlaz").iterdir()).name
    assert (root / "izlaz" / posao / "PREGLED.md").is_file()

    result = runner.invoke(cli.app, ["odobri", posao, "--izbaci", "2", "--korijen", str(root)])
    assert result.exit_code == 0, result.output
    assert "Odobreno 1, izbačeno 1; 1 videa" in result.output
    files: list[Any] = sorted((root / "izlaz" / "mobitel" / "tiktok_test").iterdir())
    assert [f.name for f in files] == [f"{posao}-01.mp4", f"{posao}-01.opis.txt"]
    statuses = [r["status"] for r in Database(root / "data" / "clipping.db").isjecci(posao)]
    assert statuses == ["odobren", "izbacen"]


def test_odobri_bad_izbaci(root: Path) -> None:
    result = CliRunner().invoke(cli.app, ["odobri", "x", "--izbaci", "tri", "--korijen", str(root)])
    assert result.exit_code == 2 and "brojeve odvojene zarezom" in result.output


def test_odobri_unknown_posao(root: Path) -> None:
    result = CliRunner().invoke(cli.app, ["odobri", "nema", "--korijen", str(root)])
    assert result.exit_code == 2 and "ne postoji" in result.output
