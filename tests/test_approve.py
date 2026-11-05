from pathlib import Path

import pytest
import yaml

from clipping.approve import ApproveError, approve, build_opis
from clipping.candidates import Candidate
from clipping.db import Database
from clipping.profile import CampaignProfile, load_profile

FIXTURE = Path(__file__).parent / "fixtures" / "kampanja_test.yaml"


def _profile(tmp_path: Path, platforms: list[str]) -> CampaignProfile:
    data = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    data["platforme"] = platforms
    path = tmp_path / "kampanja.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return load_profile(path)


def _job(tmp_path: Path, profile: CampaignProfile, qa: list[bool]) -> tuple[Database, str]:
    db = Database(tmp_path / "data" / "clipping.db")
    db.migrate()
    kampanja_id = db.upsert_kampanja(profile)
    izvor_id = db.get_or_create_izvor(kampanja_id, "https://youtu.be/abc", "sha", "brief")
    posao = db.create_posao(izvor_id, list(profile.platforme))
    for redni, ok in enumerate(qa, start=1):
        clip = tmp_path / "izlaz" / posao / "isjecci" / f"{redni:02d}_bold_pop.mp4"
        clip.parent.mkdir(parents=True, exist_ok=True)
        clip.write_bytes(b"mp4" * redni)
        cand = Candidate(
            start_word_index=0, end_word_index=5, naslov=f"n{redni}", udica=f"Hook {redni}",
            ocjena=60,
        )  # fmt: skip
        clip_id = db.insert_isjecak(
            posao, redni, cand, start_word=0, end_word=5, start_s=redni * 100.0,
            end_s=redni * 100.0 + 30, path=clip, stil="bold_pop",
        )  # fmt: skip
        db.set_isjecak_qa(clip_id, ok, [] if ok else ["žig nedostaje"])
    return db, posao


def test_odobri_writes_file_and_statuses(tmp_path: Path) -> None:
    profile = _profile(tmp_path, ["tiktok", "instagram"])
    db, posao = _job(tmp_path, profile, [True, True, True])
    result = approve(posao, izbaci={2}, db=db, root=tmp_path, profile=profile)
    assert result.odobreni == [1, 3] and result.izbaceni == [2]
    assert (tmp_path / "izlaz" / posao / "ODOBRENO.txt").read_text(encoding="utf-8") == "2\n"
    assert [r["status"] for r in db.isjecci(posao)] == ["odobren", "izbacen", "odobren"]


def test_mobitel_has_file_per_platform(tmp_path: Path) -> None:
    profile = _profile(tmp_path, ["tiktok", "instagram", "x"])
    db, posao = _job(tmp_path, profile, [True, True, True])
    result = approve(posao, izbaci={3}, db=db, root=tmp_path, profile=profile)
    mobitel = tmp_path / "izlaz" / "mobitel"
    assert len(list(mobitel.rglob("*.mp4"))) == 6
    assert len(list(mobitel.rglob("*.opis.txt"))) == 6
    assert (mobitel / "tiktok_test" / f"{posao}-01.mp4").read_bytes() == b"mp4"
    assert (mobitel / "instagram_NEPOZNAT" / f"{posao}-02.mp4").is_file()
    assert any("instagram" in w for w in result.upozorenja)


def test_qa_failure_is_never_approved(tmp_path: Path) -> None:
    profile = _profile(tmp_path, ["tiktok"])
    db, posao = _job(tmp_path, profile, [True, False])
    result = approve(posao, izbaci=set(), db=db, root=tmp_path, profile=profile)
    assert result.odobreni == [1] and result.pali_qa == [2]
    assert [r["status"] for r in db.isjecci(posao)] == ["odobren", "izrezan"]
    assert not list((tmp_path / "izlaz" / "mobitel").rglob(f"{posao}-02*"))


def test_reapprove_removes_newly_excluded(tmp_path: Path) -> None:
    profile = _profile(tmp_path, ["tiktok"])
    db, posao = _job(tmp_path, profile, [True, True])
    approve(posao, izbaci=set(), db=db, root=tmp_path, profile=profile)
    approve(posao, izbaci={1}, db=db, root=tmp_path, profile=profile)
    folder = tmp_path / "izlaz" / "mobitel" / "tiktok_test"
    assert sorted(p.name for p in folder.iterdir()) == [f"{posao}-02.mp4", f"{posao}-02.opis.txt"]


def test_unknown_redni_rejected(tmp_path: Path) -> None:
    profile = _profile(tmp_path, ["tiktok"])
    db, posao = _job(tmp_path, profile, [True])
    with pytest.raises(ApproveError, match=r"\[9\]"):
        approve(posao, izbaci={9}, db=db, root=tmp_path, profile=profile)


def test_opis_contains_paid_partnership(tmp_path: Path) -> None:
    profile = _profile(tmp_path, ["tiktok"])
    text = build_opis(profile, udica="She spent $15,300", naslov="n", opis="", url_izvora="U")
    assert text.startswith("She spent $15,300")
    assert "Paid partnership with Testni Kreator" in text and "#ad" in text and "U" in text

    bare = profile.model_copy(
        update={"opis": profile.opis.model_copy(update={"predlozak": "{udica} {nepoznato}"})}
    )
    text = build_opis(bare, udica="Hook", naslov="n", opis="", url_izvora="")
    assert "Paid partnership with Testni Kreator" in text and text.rstrip().endswith("#ad")
    assert "{nepoznato}" in text
