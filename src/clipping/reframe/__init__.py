"""Kadriranje: iz 16:9 izvora putanja kadra 9:16 koja prati govornika.

Po uzoru na artbyjazi/autoclip (MIT, Jad Ghazi), `pipeline/reframe/__init__.py`, bez diarizacije.
Za jedan isječak: kadrovi montaže → opažanja lica → tragovi → po kadru strategija TRACK, WIDE ili
GENERAL → sirova putanja → glađenje → segmenti. Mjerilo je „nikad trzaj“: bez vidljivog drhtanja,
bez odrezanih lica. Kad detekcija ne radi ili lica nema, središnji kadar; iznimka nikad.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from clipping import ffmpeg
from clipping.reframe.croppath import (
    CropKeyframe,
    CropPath,
    CropSegment,
    Strategy,
    centre_crop,
    segment_crop_filter,
    target_crop_size,
)
from clipping.reframe.faces import FaceDetectionUnavailable, FaceObservation, sample_faces
from clipping.reframe.scenes import Shot, detect_shots
from clipping.reframe.smoothing import SmoothingConfig, smooth_series
from clipping.reframe.speaker import assign_speakers
from clipping.reframe.tracker import FaceTrack, build_tracks

log = logging.getLogger(__name__)

__all__ = [
    "CropKeyframe",
    "CropPath",
    "CropSegment",
    "ReframeConfig",
    "Strategy",
    "build_crop_path",
    "segment_crop_filter",
    "track_segment",
    "wide_segment",
]

#: Gdje linija očiju sjedi u kadru (udio visine kadra): gornja trećina, bez tijesne brade.
EYE_LINE_RATIO = 0.38
#: Lice šire od ovog udjela kadra je krupni plan: zaključaj, ne prati.
LOCK_IF_FACE_WIDER_THAN = 0.55
#: Raspon lica širi od ovog udjela kadra: nijedan rez ih ne drži, uklopi cijeli kadar.
FIT_IF_SPREAD_EXCEEDS = 0.95


@dataclass
class ReframeConfig:
    aspect_w: int = 9
    aspect_h: int = 16
    sample_fps: float = 5.0
    smoothing: SmoothingConfig | None = None
    #: Preskoči detekciju lica i reži u sredini.
    centre_only: bool = False


def build_crop_path(
    video: Path, *, start_s: float, end_s: float, config: ReframeConfig | None = None
) -> CropPath:
    """Putanja kadra jednog isječka `[start_s, end_s]` izvora; vremena su od početka isječka."""
    config = config or ReframeConfig()
    duration = end_s - start_s
    info = ffmpeg.probe(video)
    if not info.has_video or not info.width or not info.height:
        raise ValueError(f"{video.name} nema videozapis za kadriranje")
    source_w, source_h = info.width, info.height
    crop_w, crop_h = target_crop_size(source_w, source_h, config.aspect_w, config.aspect_h)

    def fallback() -> CropPath:
        return centre_crop(
            source_w, source_h, duration, aspect_w=config.aspect_w, aspect_h=config.aspect_h
        )

    if config.centre_only:
        return fallback()
    try:
        observations = sample_faces(
            video, start_s=start_s, end_s=end_s, sample_fps=config.sample_fps
        )
    except FaceDetectionUnavailable as exc:
        log.warning("detekcija lica nedostupna (%s); središnji kadar", exc)
        return fallback()
    if not observations:
        log.info("nema lica u %s; središnji kadar", video.name)
        return fallback()

    tracks = build_tracks(observations)
    shots = detect_shots(video, start_s=start_s, end_s=end_s)
    segments: list[CropSegment] = []
    for shot in shots:
        segments.extend(
            _segments_for_shot(shot, tracks, source_w, source_h, crop_w, crop_h, config)
        )
    if not segments:
        return fallback()

    # Segmenti moraju točno popločati isječak; rupa ili preklop razdvoje sliku od zvuka.
    segments[0].start_s = 0.0
    segments[-1].end_s = duration
    for index in range(len(segments) - 1):
        segments[index].end_s = segments[index + 1].start_s
    segments = [s for s in segments if s.duration_s > 0.01]
    log.info(
        "%s: %d segmenata (%s)", video.name, len(segments), ", ".join(s.strategy for s in segments)
    )
    return CropPath(source_width=source_w, source_height=source_h, segments=segments)


def _segments_for_shot(
    shot: Shot,
    tracks: list[FaceTrack],
    source_w: int,
    source_h: int,
    crop_w: int,
    crop_h: int,
    config: ReframeConfig,
) -> list[CropSegment]:
    segments: list[CropSegment] = []
    for a in assign_speakers(tracks, shot_start_s=shot.start_s, shot_end_s=shot.end_s):
        visible = [t for t in tracks if t.observations_between(a.start_s, a.end_s)]
        if a.track is not None:
            segments.append(
                track_segment(
                    a.track,
                    start_s=a.start_s,
                    end_s=a.end_s,
                    source_w=source_w,
                    source_h=source_h,
                    crop_w=crop_w,
                    crop_h=crop_h,
                    config=config,
                )
            )
        elif visible:
            segments.append(
                wide_segment(
                    visible,
                    start_s=a.start_s,
                    end_s=a.end_s,
                    source_w=source_w,
                    source_h=source_h,
                    crop_w=crop_w,
                    crop_h=crop_h,
                )
            )
        else:
            segments.append(
                _general_segment(a.start_s, a.end_s, source_w, source_h, crop_w, crop_h)
            )
    return segments


def track_segment(
    track: FaceTrack,
    *,
    start_s: float,
    end_s: float,
    source_w: int,
    source_h: int,
    crop_w: int,
    crop_h: int,
    config: ReframeConfig | None = None,
) -> CropSegment:
    """Jedan subjekt: prati ga, zaključaj kadar ako se jedva miče, `fit` ako je širi od kadra."""
    config = config or ReframeConfig()
    observations = track.observations_between(start_s, end_s)
    if not observations:
        return _general_segment(start_s, end_s, source_w, source_h, crop_w, crop_h)
    mean_face_width = sum(o.width for o in observations) / len(observations)
    if mean_face_width > crop_w * FIT_IF_SPREAD_EXCEEDS:
        return _fit_segment(start_s, end_s, source_w, source_h)
    raw = [
        (
            o.t,
            _clamp(o.cx - crop_w / 2, 0, source_w - crop_w),
            _clamp(o.eye_y - EYE_LINE_RATIO * crop_h, 0, source_h - crop_h),
        )
        for o in observations
    ]
    smoothing = config.smoothing or SmoothingConfig()
    spread_x = max(x for _, x, _ in raw) - min(x for _, x, _ in raw)
    should_lock = (
        mean_face_width > crop_w * LOCK_IF_FACE_WIDER_THAN or spread_x < smoothing.dead_zone_px
    )
    if should_lock or len(raw) < 3:
        x = sum(item[1] for item in raw) / len(raw)
        y = sum(item[2] for item in raw) / len(raw)
        keyframes = [CropKeyframe(start_s, x, y)]
    else:
        xs = smooth_series([(t, x) for t, x, _ in raw], smoothing)
        ys = smooth_series([(t, y) for t, _, y in raw], smoothing)
        keyframes = [CropKeyframe(t, x, y) for (t, x), (_, y) in zip(xs, ys, strict=True)]
        if keyframes[0].t > start_s:
            keyframes.insert(0, CropKeyframe(start_s, keyframes[0].x, keyframes[0].y))
        if keyframes[-1].t < end_s:
            keyframes.append(CropKeyframe(end_s, keyframes[-1].x, keyframes[-1].y))
    return CropSegment(start_s, end_s, crop_w, crop_h, keyframes, Strategy.TRACK)


def wide_segment(
    visible: list[FaceTrack],
    *,
    start_s: float,
    end_s: float,
    source_w: int,
    source_h: int,
    crop_w: int,
    crop_h: int,
) -> CropSegment:
    """Više lica odjednom: zaključan kadar na njihovu središtu, ili `fit` ako ne stanu."""
    observations: list[FaceObservation] = [
        o for track in visible for o in track.observations_between(start_s, end_s)
    ]
    if not observations:
        return _general_segment(start_s, end_s, source_w, source_h, crop_w, crop_h)
    left = min(o.left for o in observations)
    right = max(o.right for o in observations)
    if right - left > crop_w * FIT_IF_SPREAD_EXCEEDS:
        return _fit_segment(start_s, end_s, source_w, source_h)
    centre_x = (left + right) / 2
    eye_y = sum(o.eye_y for o in observations) / len(observations)
    keyframe = CropKeyframe(
        start_s,
        _clamp(centre_x - crop_w / 2, 0, source_w - crop_w),
        _clamp(eye_y - EYE_LINE_RATIO * crop_h, 0, source_h - crop_h),
    )
    return CropSegment(start_s, end_s, crop_w, crop_h, [keyframe], Strategy.WIDE)


def _fit_segment(start_s: float, end_s: float, source_w: int, source_h: int) -> CropSegment:
    """Cijeli izvorni kadar na zamućenoj pozadini: lice ili lica šira nego što rez može držati."""
    return CropSegment(
        start_s,
        end_s,
        source_w,
        source_h,
        [CropKeyframe(start_s, 0.0, 0.0)],
        Strategy.WIDE,
        fit=True,
    )


def _general_segment(
    start_s: float, end_s: float, source_w: int, source_h: int, crop_w: int, crop_h: int
) -> CropSegment:
    """Nema upotrebljivog lica: središnji kadar."""
    keyframe = CropKeyframe(start_s, (source_w - crop_w) / 2, (source_h - crop_h) / 2)
    return CropSegment(start_s, end_s, crop_w, crop_h, [keyframe], Strategy.GENERAL)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(value, high)) if high > low else max(0.0, low)
