import sqlite3
from pathlib import Path

import pytest

from clipping.candidates import Candidate
from clipping.db import Database
from clipping.profile import load_profile

FIXTURE = Path(__file__).parent / "fixtures" / "kampanja_test.yaml"


def _db(tmp_path: Path) -> Database:
    db = Database(tmp_path / "clipping.db")
    db.migrate()
    return db


def _posao(db: Database) -> tuple[int, int, str]:
    kampanja_id = db.upsert_kampanja(load_profile(FIXTURE))
    izvor_id = db.get_or_create_izvor(kampanja_id, "https://youtu.be/x", "abc", "brief")
    return kampanja_id, izvor_id, db.create_posao(izvor_id, ["tiktok"])


def _cand(start: int = 0, end: int = 10) -> Candidate:
    return Candidate(start_word_index=start, end_word_index=end, naslov="n", udica="u", ocjena=50)


def _add_clip(db: Database, posao: str, redni: int, start_s: float, end_s: float) -> int:
    return db.insert_isjecak(
        posao,
        redni,
        _cand(),
        start_word=0,
        end_word=10,
        start_s=start_s,
        end_s=end_s,
        path=Path(f"{redni}.mp4"),
        stil="bold_pop",
    )


def test_migrate_idempotent(tmp_path: Path) -> None:
    db = _db(tmp_path)
    db.migrate()
    with db.connect() as conn:
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        versions = conn.execute("SELECT COUNT(*) FROM migracija").fetchone()[0]
    expected = {"kampanja", "izvor", "posao", "korak", "isjecak", "objava", "pregledi"}
    assert expected | {"isplata", "dogadjaj"} <= tables
    assert versions == 1


def test_posao_id_format_and_same_izvor(tmp_path: Path) -> None:
    db = _db(tmp_path)
    kampanja_id, izvor_id, posao = _posao(db)
    assert posao.split("-")[1] == "test" and len(posao.split("-")[-1]) == 4
    again = db.get_or_create_izvor(kampanja_id, "https://youtu.be/x", "def", "brief")
    assert again == izvor_id
    assert db.izvor(izvor_id)["sha256"] == "def"


def test_posao_korak_resume(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _, izvor_id, posao = _posao(db)
    assert db.last_done_korak(posao) is None
    db.set_korak(posao, "prijepis", "pocet")
    assert db.last_done_korak(posao) is None
    db.set_korak(posao, "prijepis", "gotov")
    assert db.last_done_korak(posao) == "prijepis"
    assert db.korak_status(posao, "prijepis") == "gotov"
    assert db.unfinished_posao(izvor_id) == posao
    db.finish_posao(posao)
    assert db.unfinished_posao(izvor_id) is None


def test_isjecak_status_check_rejects_unknown(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _, _, posao = _posao(db)
    clip = _add_clip(db, posao, 1, 0.0, 30.0)
    with pytest.raises(sqlite3.IntegrityError):
        db.set_isjecak_status(clip, "nepoznat")  # type: ignore[arg-type]


def test_qa_ok_moves_to_provjeren_only_when_ok(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _, _, posao = _posao(db)
    good = _add_clip(db, posao, 1, 0.0, 30.0)
    bad = _add_clip(db, posao, 2, 40.0, 70.0)
    db.set_isjecak_qa(good, True, [])
    db.set_isjecak_qa(bad, False, ["žig nedostaje"])
    rows = {r["id"]: r for r in db.isjecci(posao)}
    assert rows[good]["status"] == "provjeren"
    assert rows[bad]["status"] == "izrezan" and "žig" in rows[bad]["qa_nalazi_json"]


def test_published_ranges_only_published(tmp_path: Path) -> None:
    db = _db(tmp_path)
    kampanja_id, izvor_id, posao = _posao(db)
    cut = _add_clip(db, posao, 1, 0.0, 30.0)
    approved = _add_clip(db, posao, 2, 100.0, 130.0)
    published = _add_clip(db, posao, 3, 200.0, 230.0)
    dropped = _add_clip(db, posao, 4, 300.0, 330.0)
    db.set_isjecak_status(approved, "odobren")
    db.set_isjecak_status(published, "objavljen")
    db.set_isjecak_status(dropped, "izbacen")
    assert cut
    ranges = {(r.izvor_id, r.start_s) for r in db.published_ranges(kampanja_id)}
    assert ranges == {(izvor_id, 100.0), (izvor_id, 200.0)}
