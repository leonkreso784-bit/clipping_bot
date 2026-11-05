"""Putanja kadra i njezin prijevod u FFmpeg `crop` izraze.

Po uzoru na artbyjazi/autoclip (MIT, Jad Ghazi), `pipeline/reframe/croppath.py`.
Putanja je popis segmenata (jedan po kadru montaže); unutar segmenta prozor ima stalnu veličinu i
smije se pomicati, među segmentima veličina smije biti različita jer se svaki skalira na isti izlaz.
Pomak je dio-po-dio linearan izraz po `t`, ne `sendcmd`: sve ostaje u jednom filtergrafu.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

#: Više ključnih kadrova po segmentu ne donosi vidljivu razliku, a izraz postaje nezgrapan.
MAX_KEYFRAMES_PER_SEGMENT = 48
#: Pomak manji od ovoga (px) se odbacuje pri prorjeđivanju.
KEYFRAME_EPSILON_PX = 1.0


class Strategy(StrEnum):
    """Kako je kadar uokviren; bilježi se po segmentu radi pregleda i testova."""

    TRACK = "track"
    WIDE = "wide"
    GENERAL = "general"


@dataclass
class CropKeyframe:
    """Gornji lijevi kut prozora u trenutku `t` (sekunde od početka isječka)."""

    t: float
    x: float
    y: float


@dataclass
class CropSegment:
    start_s: float
    end_s: float
    width: int
    height: int
    keyframes: list[CropKeyframe] = field(default_factory=list)
    strategy: Strategy = Strategy.GENERAL
    #: Umjesto rezanja uklopi cijeli izvorni kadar na zamućenu pozadinu (lica preširoko za kadar).
    fit: bool = False

    @property
    def duration_s(self) -> float:
        return self.end_s - self.start_s

    @property
    def is_static(self) -> bool:
        if len(self.keyframes) <= 1:
            return True
        first = self.keyframes[0]
        return all(
            abs(k.x - first.x) < KEYFRAME_EPSILON_PX and abs(k.y - first.y) < KEYFRAME_EPSILON_PX
            for k in self.keyframes
        )


@dataclass
class CropPath:
    """Cijeli plan kadriranja jednog isječka."""

    source_width: int
    source_height: int
    segments: list[CropSegment] = field(default_factory=list)

    @property
    def duration_s(self) -> float:
        return self.segments[-1].end_s if self.segments else 0.0


def target_crop_size(
    source_width: int, source_height: int, aspect_w: int = 9, aspect_h: int = 16
) -> tuple[int, int]:
    """Najveći prozor ciljanog omjera koji stane u izvor; dimenzije parne (yuv420p)."""
    target_ratio = aspect_w / aspect_h
    source_ratio = source_width / source_height
    if source_ratio > target_ratio:
        height = source_height
        width = round(height * target_ratio)
    else:
        width = source_width
        height = round(width / target_ratio)
    width = min(source_width, width - (width % 2))
    height = min(source_height, height - (height % 2))
    return max(2, width), max(2, height)


def centre_crop(
    source_width: int,
    source_height: int,
    duration_s: float,
    *,
    aspect_w: int = 9,
    aspect_h: int = 16,
) -> CropPath:
    """Statični središnji kadar: rezerva kad lica nema ili detekcija ne radi."""
    width, height = target_crop_size(source_width, source_height, aspect_w, aspect_h)
    x = (source_width - width) / 2
    y = (source_height - height) / 2
    return CropPath(
        source_width=source_width,
        source_height=source_height,
        segments=[
            CropSegment(0.0, duration_s, width, height, [CropKeyframe(0.0, x, y)], Strategy.GENERAL)
        ],
    )


def decimate(
    keyframes: list[CropKeyframe], *, limit: int = MAX_KEYFRAMES_PER_SEGMENT
) -> list[CropKeyframe]:
    """Svedi ključne kadrove na najviše `limit`, čuvajući one koji nose pomak i oba kraja."""
    if len(keyframes) <= 2:
        return list(keyframes)
    kept: list[CropKeyframe] = [keyframes[0]]
    for previous, current, following in zip(keyframes, keyframes[1:], keyframes[2:], strict=False):
        span = following.t - previous.t
        if span <= 0:
            continue
        ratio = (current.t - previous.t) / span
        predicted_x = previous.x + (following.x - previous.x) * ratio
        predicted_y = previous.y + (following.y - previous.y) * ratio
        if (
            abs(current.x - predicted_x) > KEYFRAME_EPSILON_PX
            or abs(current.y - predicted_y) > KEYFRAME_EPSILON_PX
        ):
            kept.append(current)
    kept.append(keyframes[-1])
    if len(kept) <= limit:
        return kept
    step = len(kept) / (limit - 1)
    thinned = [kept[min(len(kept) - 1, round(i * step))] for i in range(limit - 1)]
    thinned.append(kept[-1])
    deduped: list[CropKeyframe] = []
    for frame in thinned:
        if not deduped or frame.t > deduped[-1].t:
            deduped.append(frame)
    return deduped


def axis_expression(keyframes: list[CropKeyframe], axis: str, *, offset_s: float = 0.0) -> str:
    """Dio-po-dio linearan FFmpeg izraz za jednu os; `offset_s` se oduzima od vremena."""
    if not keyframes:
        return "0"
    values = [(round(k.t - offset_s, 4), round(getattr(k, axis), 2)) for k in keyframes]
    if len(values) == 1:
        return str(values[0][1])
    expression = str(values[-1][1])
    for (t0, v0), (t1, v1) in zip(reversed(values[:-1]), reversed(values[1:]), strict=True):
        span = t1 - t0
        if span <= 0:
            continue
        slope = round((v1 - v0) / span, 6)
        expression = f"if(lt(t,{t1}),({v0}+{slope}*(t-{t0})),{expression})"
    return expression


def segment_crop_filter(segment: CropSegment, *, relative: bool = True) -> str:
    """`crop` filter jednog segmenta; `relative` kad je PTS resetiran prethodnim `trim`-om."""
    offset = segment.start_s if relative else 0.0
    if segment.is_static or len(segment.keyframes) <= 1:
        first = segment.keyframes[0] if segment.keyframes else CropKeyframe(0.0, 0.0, 0.0)
        x_expr, y_expr = str(round(first.x, 2)), str(round(first.y, 2))
    else:
        frames = decimate(segment.keyframes)
        x_expr = axis_expression(frames, "x", offset_s=offset)
        y_expr = axis_expression(frames, "y", offset_s=offset)
    x_expr = x_expr.replace(",", "\\,")
    y_expr = y_expr.replace(",", "\\,")
    return f"crop=w={segment.width}:h={segment.height}:x='{x_expr}':y='{y_expr}'"
