"""Granice kadrova montaže (PySceneDetect); kadar se nikad ne interpolira preko reza.

Po uzoru na artbyjazi/autoclip (MIT, Jad Ghazi), `pipeline/reframe/scenes.py`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)

DEFAULT_THRESHOLD = 27.0
MIN_SHOT_S = 0.8


@dataclass
class Shot:
    start_s: float
    end_s: float

    @property
    def duration_s(self) -> float:
        return self.end_s - self.start_s


def detect_shots(
    video: Path,
    *,
    start_s: float,
    end_s: float,
    threshold: float = DEFAULT_THRESHOLD,
    min_shot_s: float = MIN_SHOT_S,
) -> list[Shot]:
    """Kadrovi u `[start_s, end_s)` s vremenima od početka isječka; uvijek bar jedan."""
    duration = end_s - start_s
    try:
        shots = _detect_with_scenedetect(video, start_s, end_s, threshold)
    except Exception as exc:  # noqa: BLE001 — bilo koji pad detekcije = jedan kadar
        log.warning("detekcija kadrova nije uspjela (%s); isječak je jedan kadar", exc)
        shots = []
    if not shots:
        return [Shot(0.0, duration)]
    return _merge_short_shots(shots, min_shot_s)


def _detect_with_scenedetect(
    video: Path, start_s: float, end_s: float, threshold: float
) -> list[Shot]:
    from scenedetect import ContentDetector, SceneManager, open_video

    stream = open_video(str(video))
    manager = SceneManager()
    manager.add_detector(ContentDetector(threshold=threshold))
    if start_s > 0:
        stream.seek(start_s)
    manager.detect_scenes(video=stream, end_time=end_s, show_progress=False)
    shots: list[Shot] = []
    for scene_start, scene_end in manager.get_scene_list():
        relative_start = max(0.0, float(scene_start.get_seconds()) - start_s)
        relative_end = min(float(scene_end.get_seconds()) - start_s, end_s - start_s)
        if relative_end > relative_start:
            shots.append(Shot(relative_start, relative_end))
    return shots


def _merge_short_shots(shots: list[Shot], min_shot_s: float) -> list[Shot]:
    if len(shots) <= 1:
        return shots
    merged: list[Shot] = [shots[0]]
    for shot in shots[1:]:
        if shot.duration_s < min_shot_s or merged[-1].duration_s < min_shot_s:
            merged[-1] = Shot(merged[-1].start_s, shot.end_s)
        else:
            merged.append(shot)
    return merged
