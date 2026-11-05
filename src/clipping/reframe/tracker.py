"""Povezivanje opažanja lica u tragove po osobi.

Po uzoru na artbyjazi/autoclip (MIT, Jad Ghazi), `pipeline/reframe/tracker.py`.
IoU plus rezerva po udaljenosti središta: pri 5 uzoraka u sekundi osoba se često pomakne više
od širine vlastitog lica, što samo IoU ne bi povezalo.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field

from clipping.reframe.faces import FaceObservation

IOU_THRESHOLD = 0.25
CENTRE_DISTANCE_FACTOR = 1.2
MAX_GAP_S = 0.8
MIN_TRACK_DURATION_S = 0.5


@dataclass
class FaceTrack:
    id: int
    observations: list[FaceObservation] = field(default_factory=list)

    @property
    def start_s(self) -> float:
        return self.observations[0].t if self.observations else 0.0

    @property
    def end_s(self) -> float:
        return self.observations[-1].t if self.observations else 0.0

    @property
    def duration_s(self) -> float:
        return self.end_s - self.start_s

    @property
    def mean_area(self) -> float:
        return statistics.fmean(o.area for o in self.observations) if self.observations else 0.0

    @property
    def last(self) -> FaceObservation | None:
        return self.observations[-1] if self.observations else None

    def observations_between(self, start_s: float, end_s: float) -> list[FaceObservation]:
        return [o for o in self.observations if start_s <= o.t < end_s]

    def mouth_activity(self, start_s: float, end_s: float) -> float:
        """Varijanca otvorenosti usta u prozoru: usta koja govore se miču, koja slušaju ne."""
        window = [o.mar for o in self.observations_between(start_s, end_s)]
        if len(window) < 3:
            return 0.0
        return statistics.pvariance(window)


def build_tracks(
    observations: list[FaceObservation],
    *,
    max_gap_s: float = MAX_GAP_S,
    min_duration_s: float = MIN_TRACK_DURATION_S,
) -> list[FaceTrack]:
    """Poveži opažanja u tragove, sortirane po istaknutosti (površina × trajanje)."""
    if not observations:
        return []
    by_time: dict[float, list[FaceObservation]] = {}
    for observation in observations:
        by_time.setdefault(observation.t, []).append(observation)

    tracks: list[FaceTrack] = []
    open_tracks: list[FaceTrack] = []
    next_id = 0
    for timestamp in sorted(by_time):
        frame_observations = by_time[timestamp]
        open_tracks = [t for t in open_tracks if timestamp - t.end_s <= max_gap_s]
        pairs: list[tuple[float, FaceTrack, FaceObservation]] = []
        for track in open_tracks:
            for observation in frame_observations:
                score = _match_score(track, observation)
                if score > 0:
                    pairs.append((score, track, observation))
        pairs.sort(key=lambda p: p[0], reverse=True)
        claimed_tracks: set[int] = set()
        claimed_observations: set[int] = set()
        for _, track, observation in pairs:
            if track.id in claimed_tracks or id(observation) in claimed_observations:
                continue
            track.observations.append(observation)
            claimed_tracks.add(track.id)
            claimed_observations.add(id(observation))
        for observation in frame_observations:
            if id(observation) in claimed_observations:
                continue
            track = FaceTrack(id=next_id, observations=[observation])
            next_id += 1
            tracks.append(track)
            open_tracks.append(track)

    surviving = [t for t in tracks if t.duration_s >= min_duration_s or len(t.observations) >= 3]
    surviving.sort(key=lambda t: t.mean_area * t.duration_s, reverse=True)
    return surviving


def _match_score(track: FaceTrack, observation: FaceObservation) -> float:
    last = track.last
    if last is None:
        return 0.0
    iou = last.iou(observation)
    if iou >= IOU_THRESHOLD:
        return 1.0 + iou
    distance: float = ((last.cx - observation.cx) ** 2 + (last.cy - observation.cy) ** 2) ** 0.5
    tolerance = max(last.width, observation.width) * CENTRE_DISTANCE_FACTOR
    if distance <= tolerance:
        return 1.0 - distance / tolerance
    return 0.0
