"""Profil kampanje: `kampanje/<slug>.yaml` → pydantic model (dizajn §5).

Ključevi YAML-a su na hrvatskom jer ih Leon piše iz briefa; identifikatori koda su na engleskom.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

#: Korijen repozitorija; `zig.datoteka` je relativan na njega.
REPO_ROOT = Path(__file__).resolve().parents[2]

Platform = Literal["tiktok", "instagram", "x", "youtube"]
WatermarkPosition = Literal["centar", "gore_lijevo", "gore_desno", "dolje_lijevo", "dolje_desno"]

#: Do cigle C2 zadatka 11 (captions.PRESETS) popis stilova živi ovdje.
CAPTION_STYLE_NAMES: frozenset[str] = frozenset({"bold_pop", "clean_lower", "boxed"})


class ProfileError(Exception):
    """Profil nije ispravan; poruka je na hrvatskom i namijenjena Leonu."""


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Range(_Strict):
    min: float = Field(gt=0)
    max: float = Field(gt=0)

    @model_validator(mode="after")
    def _ordered(self) -> Range:
        if self.max < self.min:
            raise ValueError("trajanje_s.max mora biti veći ili jednak min")
        return self


class Sources(_Strict):
    dopusteni_kanali: list[str] = Field(min_length=1)
    zapis_prava: str


class ClipRules(_Strict):
    trajanje_s: Range
    jezik: str = "en"


class Watermark(_Strict):
    datoteka: Path
    polozaj: WatermarkPosition = "centar"
    neprozirnost: float = Field(default=0.85, ge=0.0, le=1.0)

    @property
    def path(self) -> Path:
        """Apsolutna putanja žiga (relativne se gledaju od korijena repozitorija)."""
        return self.datoteka if self.datoteka.is_absolute() else REPO_ROOT / self.datoteka


class Graphics(_Strict):
    zig: Watermark | None = None
    obvezni_tekst: str | None = None
    obvezni_zvuk: str | None = None
    hashtagovi: list[str] = Field(default_factory=list)


class Description(_Strict):
    oznaka_placene_suradnje: bool = True
    predlozak: str


class Profanity(_Strict):
    titlovi: Literal["zvjezdice", "puno"] = "zvjezdice"
    zvuk: Literal["nista"] = "nista"


class ContentRules(_Strict):
    zabranjeno: list[str] = Field(default_factory=list)
    stil_titlova: list[str] = Field(min_length=1)
    psovke: Profanity = Field(default_factory=Profanity)


class Schedule(_Strict):
    objava_dnevno_po_racunu: int = Field(ge=1)
    zagrijavanje_dana: int = Field(ge=0)


class CampaignProfile(_Strict):
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    kreator: str
    platforma_kampanje: str
    url_kampanje: str
    cijena_po_100k_usd: float = Field(ge=0)
    prag_kvalifikacije_pregleda: int = Field(ge=0)
    platforme: list[Platform] = Field(min_length=1)
    racuni: dict[str, str] = Field(default_factory=dict)
    izvori: Sources
    isjecak: ClipRules
    grafika: Graphics
    opis: Description
    pravila_sadrzaja: ContentRules
    raspored: Schedule

    @model_validator(mode="after")
    def _cross_checks(self) -> CampaignProfile:
        extra = set(self.racuni) - set(self.platforme)
        if extra:
            raise ValueError(f"racuni za {sorted(extra)} nisu u platforme {self.platforme}")
        unknown = [s for s in self.pravila_sadrzaja.stil_titlova if s not in CAPTION_STYLE_NAMES]
        if unknown:
            raise ValueError(
                f"stil_titlova {unknown} ne postoji; dopušteno: {sorted(CAPTION_STYLE_NAMES)}"
            )
        zig = self.grafika.zig
        if zig is not None and not zig.path.is_file():
            raise ValueError(f"žig ne postoji: {zig.datoteka} (gledano od {REPO_ROOT})")
        return self

    def caption_style_for(self, index: int) -> str:
        """Stil titlova za isječak `index` (rotacija po redu iz profila)."""
        styles = self.pravila_sadrzaja.stil_titlova
        return styles[index % len(styles)]


def _beep_message(raw: object) -> str | None:
    if not isinstance(raw, dict):
        return None
    rules = raw.get("pravila_sadrzaja")
    if not isinstance(rules, dict):
        return None
    profanity = rules.get("psovke")
    if isinstance(profanity, dict) and profanity.get("zvuk") == "beep":
        return "psovke.zvuk: beep se ne gradi u V1 (dizajn §11a.3); dopušteno je samo 'nista'"
    return None


def load_profile(path: Path) -> CampaignProfile:
    """Učitaj i provjeri profil; svaka greška je `ProfileError` s porukom na hrvatskom."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ProfileError(f"profil {path} se ne može pročitati: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ProfileError(f"profil {path} nije ispravan YAML: {exc}") from exc
    if (msg := _beep_message(raw)) is not None:
        raise ProfileError(f"profil {path}: {msg}")
    if not isinstance(raw, dict):
        raise ProfileError(f"profil {path} mora biti YAML mapa s ključevima iz dizajna §5")
    try:
        return CampaignProfile.model_validate(raw)
    except ValidationError as exc:
        lines = [
            f"{'.'.join(str(p) for p in e['loc']) or '(korijen)'}: {e['msg']}"
            + (f" (dobiveno: {e['input']!r})" if "input" in e and e["type"] != "missing" else "")
            for e in exc.errors()
        ]
        raise ProfileError(f"profil {path} nije ispravan:\n  " + "\n  ".join(lines)) from exc
