"""`clipping odobri`: Leonova odluka o seriji i mapa `mobitel/` za ručnu objavu (ADR-003, ADR-010).

Odobrenje vrijedi za cijelu seriju; Leon izbacuje pojedine isječke rednim brojem. Isječak koji nije
prošao automatsku provjeru (npr. bez žiga) se ne odobrava nikad. Za svaki odobreni isječak i svaku
platformu posla nastaje `izlaz/mobitel/<platforma>_<racun>/<posao>-<redni>.mp4` i `.opis.txt`.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from clipping.db import Database
from clipping.profile import CampaignProfile, load_profile

#: Statusi koje `odobri` smije mijenjati; zakazani i objavljeni isječci su izvan njegova dosega.
_EDITABLE = ("izrezan", "provjeren", "odobren", "izbacen")
UNKNOWN_ACCOUNT = "NEPOZNAT"


class ApproveError(ValueError):
    """Odobrenje se ne može provesti (nepoznat posao ili redni broj)."""


@dataclass
class ApproveResult:
    odobreni: list[int] = field(default_factory=list)
    izbaceni: list[int] = field(default_factory=list)
    pali_qa: list[int] = field(default_factory=list)
    datoteke: list[Path] = field(default_factory=list)
    upozorenja: list[str] = field(default_factory=list)


class _Keep(dict[str, str]):
    """Nepoznato polje predloška ostaje kako je napisano, umjesto da sruši odobrenje."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def build_opis(
    profile: CampaignProfile, *, udica: str, naslov: str, opis: str, url_izvora: str
) -> str:
    """Opis objave iz `opis.predlozak`; oznaka plaćene suradnje se dodaje ako je predložak nema."""
    hashtags = list(profile.grafika.hashtagovi)
    text = profile.opis.predlozak.format_map(
        _Keep(
            udica=udica,
            naslov=naslov,
            opis=opis,
            url_izvora=url_izvora,
            kreator=profile.kreator,
            hashtagovi=" ".join(hashtags),
        )
    ).strip()
    if profile.opis.oznaka_placene_suradnje:
        partnership = f"Paid partnership with {profile.kreator}"
        if partnership.lower() not in text.lower():
            text = f"{partnership}\n\n{text}"
        if "#ad" not in text.lower().split():
            text += "\n#ad"
    return text + "\n"


def mobile_dir(root: Path, profile: CampaignProfile, platform: str) -> tuple[Path, bool]:
    """Mapa za platformu i račun; drugi dio kaže je li račun poznat."""
    account = profile.racuni.get(platform, "").strip().lstrip("@")
    known = bool(account)
    return root / "izlaz" / "mobitel" / f"{platform}_{account or UNKNOWN_ACCOUNT}", known


def approve(
    posao_id: str, *, izbaci: set[int], db: Database, root: Path, profile: CampaignProfile | None
) -> ApproveResult:
    db.migrate()
    try:
        posao = db.posao(posao_id)
    except KeyError as exc:
        raise ApproveError(f"posao {posao_id} ne postoji u bazi") from exc
    izvor = db.izvor(int(posao["izvor_id"]))
    if profile is None:
        slug = db.kampanja_slug(int(izvor["kampanja_id"]))
        profile = load_profile(root / "kampanje" / f"{slug}.yaml")
    rows = db.isjecci(posao_id)
    known = {int(r["redni"]) for r in rows}
    unknown = sorted(izbaci - known)
    if unknown:
        raise ApproveError(f"posao {posao_id} nema isječke {unknown}; postoje {sorted(known)}")
    if not rows:
        raise ApproveError(f"posao {posao_id} nema izrezanih isječaka")

    platforms: list[str] = json.loads(posao["platforme_json"])
    url = str(izvor["url"])
    url_izvora = url if url.startswith("http") else ""
    result = ApproveResult()
    for platform in platforms:
        if not mobile_dir(root, profile, platform)[1]:
            result.upozorenja.append(
                f"račun za {platform} nije upisan u profil; mapa {platform}_{UNKNOWN_ACCOUNT}"
            )

    for row in rows:
        redni = int(row["redni"])
        if row["status"] not in _EDITABLE:
            result.upozorenja.append(f"isječak {redni} je već {row['status']}; ne mijenja se")
            continue
        targets = [
            mobile_dir(root, profile, p)[0] / f"{posao_id}-{redni:02d}.mp4" for p in platforms
        ]
        if redni in izbaci or row["qa_ok"] != 1:
            if redni in izbaci:
                result.izbaceni.append(redni)
                db.set_isjecak_status(int(row["id"]), "izbacen")
            else:
                result.pali_qa.append(redni)
                db.set_isjecak_status(int(row["id"]), "izrezan")
            for target in targets:
                target.unlink(missing_ok=True)
                target.with_suffix(".opis.txt").unlink(missing_ok=True)
            continue

        source = Path(row["putanja"])
        if not source.is_file():
            raise ApproveError(f"isječak {redni} nema datoteke {source}")
        opis = build_opis(
            profile,
            udica=str(row["udica"]),
            naslov=str(row["naslov"]),
            opis=str(row["opis"]),
            url_izvora=url_izvora,
        )
        for target in targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            target.with_suffix(".opis.txt").write_text(opis, encoding="utf-8")
            result.datoteke.append(target)
        db.set_isjecak_status(int(row["id"]), "odobren")
        result.odobreni.append(redni)

    for redni in result.pali_qa:
        result.upozorenja.append(f"isječak {redni} nije prošao automatsku provjeru; nije odobren")
    posao_dir = root / "izlaz" / posao_id
    posao_dir.mkdir(parents=True, exist_ok=True)
    (posao_dir / "ODOBRENO.txt").write_text(
        "".join(f"{r}\n" for r in sorted(result.izbaceni)), encoding="utf-8"
    )
    db.log_dogadjaj(
        posao_id,
        "info",
        f"odobri: odobreno {result.odobreni}, izbačeno {result.izbaceni}, pao QA {result.pali_qa}",
    )
    return result
