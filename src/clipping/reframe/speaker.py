"""Tko drži kadar: samo po aktivnosti usta (`mar`), bez diarizacije.

Po uzoru na artbyjazi/autoclip (MIT, Jad Ghazi), `pipeline/reframe/speaker.py`, bez dijela
koji koristi diarizirane govornike (naš prijepis ih nema).
"""

from __future__ import annotations

from dataclasses import dataclass

from clipping.reframe.tracker import FaceTrack

#: Varijanca otvorenosti usta ispod koje su usta mirna.
SILENT_MAR_VARIANCE = 0.0004
#: Pobjednik mora biti toliko puta aktivniji od drugoga, inače kadar ne skače među licima.
DOMINANCE_MARGIN = 1.6


@dataclass
class SpeakerAssignment:
    start_s: float
    end_s: float
    track: FaceTrack | None
    ambiguous: bool = False


def assign_speakers(
    tracks: list[FaceTrack], *, shot_start_s: float, shot_end_s: float
) -> list[SpeakerAssignment]:
    """Jedna dodjela po kadru: jedino lice, najaktivnija usta, ili nitko (široki kadar)."""
    visible = [t for t in tracks if t.observations_between(shot_start_s, shot_end_s)]
    if not visible:
        return [SpeakerAssignment(shot_start_s, shot_end_s, None)]
    if len(visible) == 1:
        return [SpeakerAssignment(shot_start_s, shot_end_s, visible[0])]
    activity = [(track, track.mouth_activity(shot_start_s, shot_end_s)) for track in visible]
    activity.sort(key=lambda pair: pair[1], reverse=True)
    best_track, best_score = activity[0]
    runner_up = activity[1][1]
    if best_score < SILENT_MAR_VARIANCE or (
        runner_up > 0 and best_score < runner_up * DOMINANCE_MARGIN
    ):
        return [SpeakerAssignment(shot_start_s, shot_end_s, None, ambiguous=True)]
    return [SpeakerAssignment(shot_start_s, shot_end_s, best_track)]
