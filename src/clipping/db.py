"""Baza stanja (SQLite, dizajn §8): kampanje, izvori, poslovi, koraci, isječci.

Svaki korak posla upisuje `pocet` prije i `gotov` poslije, pa se prekinut posao nastavlja od zadnjeg
dovršenog koraka. Isječak dobiva red tek kad je njegov MP4 potpun.
"""

from __future__ import annotations

import json
import secrets
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

from clipping.candidates import Candidate
from clipping.profile import CampaignProfile

SCHEMA = Path(__file__).with_name("schema.sql")

StepStatus = Literal["pocet", "gotov", "greska"]
ClipStatus = Literal[
    "izrezan", "provjeren", "odobren", "izbacen", "zakazan", "objavljen", "prijavljen", "placen"
]

#: Isječci u ovim statusima su obećani za objavu ili objavljeni; novi isječak se s njima ne smije
#: preklapati (dizajn §11a.8). `odobren` je uključen da dva posla istog izvora ne daju duplikat.
COMMITTED_STATUSES: tuple[ClipStatus, ...] = (
    "odobren",
    "zakazan",
    "objavljen",
    "prijavljen",
    "placen",
)


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


#: Isječak koji se s obećanim ili objavljenim preklapa više od ovoga je duplikat (ADR-011).
MAX_DUPLICATE_OVERLAP = 0.5


@dataclass(frozen=True)
class PublishedRange:
    izvor_id: int
    start_s: float
    end_s: float
    izvor_sha256: str = ""
    posao_id: str = ""


def overlap_ratio(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    """Zajedničko trajanje kao udio kraćeg od dva raspona."""
    shared = min(a_end, b_end) - max(a_start, b_start)
    if shared <= 0:
        return 0.0
    return shared / max(1e-6, min(a_end - a_start, b_end - b_start))


def find_duplicate(
    ranges: list[PublishedRange],
    sha256: str,
    start_s: float,
    end_s: float,
    *,
    exclude_posao: str | None = None,
) -> PublishedRange | None:
    """Prvi obećani raspon istog sadržaja izvora (po hashu) koji se preklapa više od praga."""
    for r in ranges:
        if r.izvor_sha256 != sha256 or (exclude_posao is not None and r.posao_id == exclude_posao):
            continue
        if overlap_ratio(start_s, end_s, r.start_s, r.end_s) > MAX_DUPLICATE_OVERLAP:
            return r
    return None


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def migrate(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA.read_text(encoding="utf-8"))

    # --- kampanja i izvor -------------------------------------------------------------------

    def upsert_kampanja(self, profile: CampaignProfile) -> int:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO kampanja (slug, kreator, profil_json, azurirano) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(slug) DO UPDATE SET kreator = excluded.kreator, "
                "profil_json = excluded.profil_json, azurirano = excluded.azurirano",
                (profile.slug, profile.kreator, profile.model_dump_json(), _now()),
            )
            row = conn.execute("SELECT id FROM kampanja WHERE slug = ?", (profile.slug,)).fetchone()
        return int(row["id"])

    def kampanja_slug(self, kampanja_id: int) -> str:
        with self.connect() as conn:
            row = conn.execute("SELECT slug FROM kampanja WHERE id = ?", (kampanja_id,)).fetchone()
        if row is None:
            raise KeyError(f"kampanja {kampanja_id} ne postoji")
        return str(row["slug"])

    def get_or_create_izvor(
        self, kampanja_id: int, url: str, sha256: str, zapis_prava: str, putanja: str = ""
    ) -> int:
        """Isti URL u istoj kampanji je isti izvor; promijenjen sadržaj ažurira hash i putanju."""
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO izvor (kampanja_id, url, sha256, putanja, zapis_prava, dodano) "
                "VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(kampanja_id, url) DO UPDATE SET "
                "sha256 = excluded.sha256, putanja = excluded.putanja",
                (kampanja_id, url, sha256, putanja, zapis_prava, _now()),
            )
            row = conn.execute(
                "SELECT id FROM izvor WHERE kampanja_id = ? AND url = ?", (kampanja_id, url)
            ).fetchone()
        return int(row["id"])

    def izvor(self, izvor_id: int) -> sqlite3.Row:
        with self.connect() as conn:
            row: sqlite3.Row | None = conn.execute(
                "SELECT * FROM izvor WHERE id = ?", (izvor_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"izvor {izvor_id} ne postoji")
        return row

    def known_source_urls(self, kampanja_id: int) -> set[str]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT url FROM izvor WHERE kampanja_id = ?", (kampanja_id,)
            ).fetchall()
        return {str(r["url"]) for r in rows}

    # --- posao i koraci ---------------------------------------------------------------------

    def create_posao(self, izvor_id: int, platforme: list[str]) -> str:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT k.slug, i.sha256 FROM izvor i JOIN kampanja k ON k.id = i.kampanja_id "
                "WHERE i.id = ?",
                (izvor_id,),
            ).fetchone()
            if row is None:
                raise KeyError(f"izvor {izvor_id} ne postoji")
            posao_id = f"{datetime.now():%Y%m%d}-{row['slug']}-{secrets.token_hex(2)}"
            conn.execute(
                "INSERT INTO posao (id, izvor_id, izvor_sha256, platforme_json, stvoreno) "
                "VALUES (?, ?, ?, ?, ?)",
                (posao_id, izvor_id, row["sha256"], json.dumps(platforme), _now()),
            )
        return posao_id

    def posao(self, posao_id: str) -> sqlite3.Row:
        with self.connect() as conn:
            row: sqlite3.Row | None = conn.execute(
                "SELECT * FROM posao WHERE id = ?", (posao_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"posao {posao_id} ne postoji")
        return row

    def unfinished_posao(self, izvor_id: int) -> str | None:
        """Zadnji nedovršeni posao za izvor (za nastavak nakon prekida).

        Posao je vezan uz hash izvora iz trenutka nastanka; ako se sadržaj izvora promijenio,
        njegovi indeksi riječi više ne vrijede i nastavka nema.
        """
        with self.connect() as conn:
            row = conn.execute(
                "SELECT p.id FROM posao p JOIN izvor i ON i.id = p.izvor_id "
                "WHERE p.izvor_id = ? AND p.zavrseno IS NULL AND p.izvor_sha256 = i.sha256 "
                "ORDER BY p.stvoreno DESC, p.rowid DESC LIMIT 1",
                (izvor_id,),
            ).fetchone()
        return None if row is None else str(row["id"])

    def finish_posao(self, posao_id: str) -> None:
        with self.connect() as conn:
            conn.execute("UPDATE posao SET zavrseno = ? WHERE id = ?", (_now(), posao_id))

    def set_korak(self, posao_id: str, korak: str, status: StepStatus, poruka: str = "") -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO korak (posao_id, korak, status, poruka, vrijeme) "
                "VALUES (?, ?, ?, ?, ?) ON CONFLICT(posao_id, korak) DO UPDATE SET "
                "status = excluded.status, poruka = excluded.poruka, vrijeme = excluded.vrijeme",
                (posao_id, korak, status, poruka, _now()),
            )

    def korak_status(self, posao_id: str, korak: str) -> StepStatus | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT status FROM korak WHERE posao_id = ? AND korak = ?", (posao_id, korak)
            ).fetchone()
        return None if row is None else row["status"]

    def last_done_korak(self, posao_id: str) -> str | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT korak FROM korak WHERE posao_id = ? AND status = 'gotov' "
                "ORDER BY vrijeme DESC, rowid DESC LIMIT 1",
                (posao_id,),
            ).fetchone()
        return None if row is None else str(row["korak"])

    # --- isječci ----------------------------------------------------------------------------

    def insert_isjecak(
        self,
        posao_id: str,
        redni: int,
        candidate: Candidate,
        *,
        start_word: int,
        end_word: int,
        start_s: float,
        end_s: float,
        path: Path,
        stil: str,
    ) -> int:
        """Upiši (ili zamijeni) izrezan isječak; zove se tek kad je MP4 potpun."""
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO isjecak (posao_id, redni, start_word, end_word, start_s, end_s, "
                "naslov, udica, ocjena, razlog, opis, stil, putanja, status) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'izrezan') "
                "ON CONFLICT(posao_id, redni) DO UPDATE SET start_word = excluded.start_word, "
                "end_word = excluded.end_word, start_s = excluded.start_s, end_s = excluded.end_s, "
                "putanja = excluded.putanja, stil = excluded.stil, naslov = excluded.naslov, "
                "udica = excluded.udica, ocjena = excluded.ocjena, razlog = excluded.razlog, "
                "opis = excluded.opis, status = 'izrezan', qa_ok = NULL, qa_nalazi_json = '[]', "
                "pregled_ocjena = NULL, pregled_problemi_json = '[]'",
                (
                    posao_id,
                    redni,
                    start_word,
                    end_word,
                    start_s,
                    end_s,
                    candidate.naslov,
                    candidate.udica,
                    candidate.ocjena,
                    candidate.razlog,
                    candidate.opis,
                    stil,
                    str(path),
                ),
            )
            row = conn.execute(
                "SELECT id FROM isjecak WHERE posao_id = ? AND redni = ?", (posao_id, redni)
            ).fetchone()
        return int(row["id"])

    def set_isjecak_status(self, isjecak_id: int, status: ClipStatus) -> None:
        with self.connect() as conn:
            conn.execute("UPDATE isjecak SET status = ? WHERE id = ?", (status, isjecak_id))

    def set_isjecak_qa(self, isjecak_id: int, ok: bool, nalazi: list[str]) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE isjecak SET qa_ok = ?, qa_nalazi_json = ?, "
                "status = CASE WHEN ? THEN 'provjeren' ELSE status END WHERE id = ?",
                (int(ok), json.dumps(nalazi, ensure_ascii=False), int(ok), isjecak_id),
            )

    def set_isjecak_pregled(self, isjecak_id: int, ocjena: int | None, problemi: list[str]) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE isjecak SET pregled_ocjena = ?, pregled_problemi_json = ? WHERE id = ?",
                (ocjena, json.dumps(problemi, ensure_ascii=False), isjecak_id),
            )

    def isjecci(self, posao_id: str) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM isjecak WHERE posao_id = ? ORDER BY redni", (posao_id,)
            ).fetchall()

    def published_ranges(self, kampanja_id: int) -> list[PublishedRange]:
        """Rasponi izvora koji su odobreni ili objavljeni u kampanji (za odbijanje duplikata)."""
        marks = ",".join("?" for _ in COMMITTED_STATUSES)
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT p.izvor_id, s.start_s, s.end_s, p.izvor_sha256, p.id FROM isjecak s "
                "JOIN posao p ON p.id = s.posao_id JOIN izvor i ON i.id = p.izvor_id "
                f"WHERE i.kampanja_id = ? AND s.status IN ({marks})",
                (kampanja_id, *COMMITTED_STATUSES),
            ).fetchall()
        return [
            PublishedRange(int(r[0]), float(r[1]), float(r[2]), str(r[3]), str(r[4])) for r in rows
        ]

    # --- dnevnik ----------------------------------------------------------------------------

    def log_dogadjaj(self, posao_id: str | None, razina: str, poruka: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO dogadjaj (posao_id, vrijeme, razina, poruka) VALUES (?, ?, ?, ?)",
                (posao_id, _now(), razina, poruka),
            )
