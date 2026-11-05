"""Titlovi: riječi s vremenima → ASS datoteka za libass (karaoke isticanje, stilovi, psovke).

Po uzoru na artbyjazi/autoclip (MIT, Jad Ghazi), `pipeline/captions.py`. Stilovi se pišu za
referentnu visinu 1920 i skaliraju na stvarni izlaz. Isticanje riječi je jedan Dialogue event po
riječi s cijelom grupom i istaknutom aktivnom riječi: libass nema vremensku crtu po slovu.
Obvezni tekst kampanje (`top_text`) je vlastiti stil `Gore` pri vrhu, jedan event kroz cijeli
isječak.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pysubs2

from clipping.profanity import mask
from clipping.transcript import Word

FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"

DEFAULT_MAX_WORDS = 4
#: Pauza duža od ovoga zatvara grupu titla bez obzira na broj riječi.
DEFAULT_MAX_GAP_S = 0.4
REFERENCE_HEIGHT = 1920

STYLE_NAME = "Titl"
TOP_STYLE_NAME = "Gore"
TOP_SIZE_RATIO = 0.045
TOP_MARGIN_V_RATIO = 0.12


def _rgb(colour: str) -> tuple[int, int, int]:
    value = colour.lstrip("#")
    if len(value) != 6:
        raise ValueError(f"očekujem #RRGGBB, dobio {colour!r}")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def hex_to_ass(colour: str, alpha: int = 0) -> pysubs2.Color:
    r, g, b = _rgb(colour)
    return pysubs2.Color(r, g, b, alpha)


def ass_colour_override(colour: str) -> str:
    """`#RRGGBB` kao vrijednost za `\\c` oznaku: `&HBBGGRR&`."""
    r, g, b = _rgb(colour)
    return f"&H{b:02X}{g:02X}{r:02X}&"


@dataclass(frozen=True)
class CaptionStyle:
    key: str
    font: str
    font_file: str
    #: Veličina fonta kao udio visine kadra.
    size_ratio: float
    primary: str = "#FFFFFF"
    #: Boja izgovorene riječi; `None` gasi isticanje po riječi.
    accent: str | None = "#FFE500"
    outline: str = "#000000"
    outline_width: float = 4.0
    shadow: float = 0.0
    bold: bool = True
    all_caps: bool = True
    #: Udaljenost od dna kadra kao udio visine.
    margin_v_ratio: float = 0.24
    max_words: int = DEFAULT_MAX_WORDS
    #: "none" ili "scale" (aktivna riječ raste i mijenja boju).
    animation: str = "scale"
    scale_percent: int = 118
    boxed: bool = False
    box_colour: str = "#000000"
    box_alpha: int = 40

    @property
    def font_path(self) -> Path:
        return FONT_DIR / self.font_file


PRESETS: dict[str, CaptionStyle] = {
    "bold_pop": CaptionStyle(
        key="bold_pop",
        font="Anton",
        font_file="Anton-Regular.ttf",
        size_ratio=0.062,
        accent="#FFE500",
        outline_width=5.0,
        animation="scale",
        scale_percent=118,
        max_words=4,
    ),
    "clean_lower": CaptionStyle(
        key="clean_lower",
        font="Inter",
        font_file="Inter-Variable.ttf",
        size_ratio=0.034,
        accent=None,
        outline_width=2.0,
        shadow=1.0,
        bold=False,
        all_caps=False,
        margin_v_ratio=0.10,
        animation="none",
        max_words=8,
    ),
    "boxed": CaptionStyle(
        key="boxed",
        font="Anton",
        font_file="Anton-Regular.ttf",
        size_ratio=0.052,
        accent="#FF4D4D",
        outline_width=0.0,
        animation="scale",
        scale_percent=112,
        max_words=4,
        boxed=True,
        box_alpha=30,
    ),
}


@dataclass
class CaptionGroup:
    words: list[Word] = field(default_factory=list)

    @property
    def start(self) -> float:
        return self.words[0].start if self.words else 0.0

    @property
    def end(self) -> float:
        return self.words[-1].end if self.words else 0.0


def group_words(
    words: list[Word], *, max_words: int = DEFAULT_MAX_WORDS, max_gap_s: float = DEFAULT_MAX_GAP_S
) -> list[CaptionGroup]:
    """Podijeli riječi u grupe titla: kraj rečenice, pauza, pa strop broja riječi."""
    groups: list[CaptionGroup] = []
    current: list[Word] = []
    for index, word in enumerate(words):
        if current:
            gap = word.start - current[-1].end
            if gap > max_gap_s or len(current) >= max_words:
                groups.append(CaptionGroup(current))
                current = []
        current.append(word)
        if word.ends_sentence and index != len(words) - 1:
            groups.append(CaptionGroup(current))
            current = []
    if current:
        groups.append(CaptionGroup(current))
    return [g for g in groups if g.words]


def build_ass(
    words: list[Word],
    style: CaptionStyle,
    *,
    width: int,
    height: int,
    time_offset_s: float,
    mask_profanity: bool = True,
    top_text: str | None = None,
) -> pysubs2.SSAFile:
    """ASS datoteka isječka; `time_offset_s` se oduzima od svih vremena (apsolutna → isječak)."""
    subs = pysubs2.SSAFile()
    subs.info["PlayResX"] = str(width)
    subs.info["PlayResY"] = str(height)
    subs.info["ScaledBorderAndShadow"] = "yes"
    subs.info["WrapStyle"] = "0"
    scale = height / REFERENCE_HEIGHT
    subs.styles[STYLE_NAME] = _build_ass_style(style, height=height, scale=scale)

    texts = [_display_text(w, style, mask_profanity) for w in words]
    for group in group_words(words, max_words=style.max_words):
        group_texts = [texts[words.index(w)] for w in group.words]
        if style.animation == "scale" and style.accent:
            subs.events.extend(_per_word_events(group, group_texts, style, time_offset_s))
        else:
            subs.events.append(_event(group.start, group.end, " ".join(group_texts), time_offset_s))

    if top_text:
        subs.styles[TOP_STYLE_NAME] = _top_style(height=height, scale=scale)
        clip_end = max((w.end for w in words), default=time_offset_s) - time_offset_s
        subs.events.append(
            pysubs2.SSAEvent(
                start=0,
                end=pysubs2.make_time(s=max(clip_end, 0.0)),
                text=top_text,
                style=TOP_STYLE_NAME,
            )
        )
    return subs


def _build_ass_style(style: CaptionStyle, *, height: int, scale: float) -> pysubs2.SSAStyle:
    s = pysubs2.SSAStyle()
    s.fontname = style.font
    s.fontsize = round(height * style.size_ratio)
    s.primarycolor = hex_to_ass(style.primary)
    s.secondarycolor = hex_to_ass(style.accent or style.primary)
    s.outlinecolor = hex_to_ass(style.outline)
    s.backcolor = hex_to_ass(style.box_colour, alpha=style.box_alpha)
    s.bold = style.bold
    s.outline = style.outline_width * scale
    s.shadow = style.shadow * scale
    s.borderstyle = 3 if style.boxed else 1
    s.alignment = pysubs2.Alignment.BOTTOM_CENTER
    s.marginv = round(height * style.margin_v_ratio)
    s.marginl = s.marginr = round(height * 0.03)
    return s


def _top_style(*, height: int, scale: float) -> pysubs2.SSAStyle:
    s = pysubs2.SSAStyle()
    s.fontname = "Anton"
    s.fontsize = round(height * TOP_SIZE_RATIO)
    s.primarycolor = hex_to_ass("#FFFFFF")
    s.outlinecolor = hex_to_ass("#000000")
    s.bold = True
    s.outline = 4.0 * scale
    s.alignment = pysubs2.Alignment.TOP_CENTER  # \an8
    s.marginv = round(height * TOP_MARGIN_V_RATIO)
    s.marginl = s.marginr = round(height * 0.03)
    return s


def _display_text(word: Word, style: CaptionStyle, mask_profanity: bool) -> str:
    text = word.text.strip()
    if mask_profanity:
        text = mask(text)
    return text.upper() if style.all_caps else text


def _event(start_s: float, end_s: float, text: str, offset: float) -> pysubs2.SSAEvent:
    return pysubs2.SSAEvent(
        start=pysubs2.make_time(s=max(0.0, start_s - offset)),
        end=pysubs2.make_time(s=max(0.0, end_s - offset)),
        text=text,
        style=STYLE_NAME,
    )


def _per_word_events(
    group: CaptionGroup, texts: list[str], style: CaptionStyle, offset: float
) -> list[pysubs2.SSAEvent]:
    """Jedan event po riječi; svaki prikazuje cijelu grupu, mijenja se samo istaknuta riječ."""
    accent_tag = f"\\c{ass_colour_override(style.accent or style.primary)}"
    scale = style.scale_percent
    events: list[pysubs2.SSAEvent] = []
    for active, word in enumerate(group.words):
        rendered = [
            f"{{{accent_tag}\\fscx{scale}\\fscy{scale}}}{text}{{\\r}}" if i == active else text
            for i, text in enumerate(texts)
        ]
        # Zadnja riječ drži do kraja grupe da titl ne nestane prerano.
        end = word.end if active + 1 < len(group.words) else group.end
        next_start = group.words[active + 1].start if active + 1 < len(group.words) else end
        events.append(_event(word.start, max(end, next_start), " ".join(rendered), offset))
    return events


def write_ass(
    path: Path,
    words: list[Word],
    style: CaptionStyle,
    *,
    width: int,
    height: int,
    time_offset_s: float,
    mask_profanity: bool = True,
    top_text: str | None = None,
) -> Path:
    """Zapiši titlove u `.ass` i vrati putanju."""
    subs = build_ass(
        words,
        style,
        width=width,
        height=height,
        time_offset_s=time_offset_s,
        mask_profanity=mask_profanity,
        top_text=top_text,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    subs.save(str(path), encoding="utf-8")
    return path
