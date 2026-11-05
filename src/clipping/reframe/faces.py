"""Opažanja lica kroz MediaPipe FaceLandmarker (Tasks API, `face_landmarker.task`).

Po uzoru na artbyjazi/autoclip (MIT, Jad Ghazi), `pipeline/reframe/faces.py`.
Oznake umjesto okvira: oči daju liniju za visinu kadra, usne daju otvorenost usta (`mar`) kao
jeftin znak tko govori.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clipping.models_dl import ensure_face_landmarker

log = logging.getLogger(__name__)

DEFAULT_SAMPLE_FPS = 5.0
MAX_FACES = 4

_UPPER_INNER_LIP = 13
_LOWER_INNER_LIP = 14
_LEFT_MOUTH_CORNER = 61
_RIGHT_MOUTH_CORNER = 291
_EYE_LANDMARKS = (33, 133, 362, 263)


@dataclass
class FaceObservation:
    """Jedno lice u jednom trenutku, u pikselima izvora; `t` je od početka isječka."""

    t: float
    cx: float
    cy: float
    width: float
    height: float
    eye_y: float
    mar: float

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def left(self) -> float:
        return self.cx - self.width / 2

    @property
    def right(self) -> float:
        return self.cx + self.width / 2

    @property
    def top(self) -> float:
        return self.cy - self.height / 2

    @property
    def bottom(self) -> float:
        return self.cy + self.height / 2

    def iou(self, other: FaceObservation) -> float:
        overlap_w = max(0.0, min(self.right, other.right) - max(self.left, other.left))
        overlap_h = max(0.0, min(self.bottom, other.bottom) - max(self.top, other.top))
        intersection = overlap_w * overlap_h
        if intersection <= 0:
            return 0.0
        union = self.area + other.area - intersection
        return intersection / union if union else 0.0


class FaceDetectionUnavailable(RuntimeError):
    """Detekcija lica ne radi; pozivatelj pada na središnji kadar."""


def sample_faces(
    video: Path,
    *,
    start_s: float,
    end_s: float,
    sample_fps: float = DEFAULT_SAMPLE_FPS,
    max_faces: int = MAX_FACES,
) -> list[FaceObservation]:
    """Uzorkuj video i vrati sva opažena lica, s vremenom od početka isječka."""
    try:
        import cv2
        import mediapipe as mp
        from mediapipe.tasks.python import BaseOptions
        from mediapipe.tasks.python.vision import (
            FaceLandmarker,
            FaceLandmarkerOptions,
            RunningMode,
        )
    except ImportError as exc:
        raise FaceDetectionUnavailable(f"MediaPipe ili OpenCV nedostaje: {exc}") from exc

    try:
        model_file = ensure_face_landmarker()
    except OSError as exc:
        raise FaceDetectionUnavailable(f"model lica nije dostupan: {exc}") from exc

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(model_file)),
        running_mode=RunningMode.VIDEO,
        num_faces=max_faces,
        min_face_detection_confidence=0.4,
        min_tracking_confidence=0.4,
    )
    observations: list[FaceObservation] = []
    with FaceLandmarker.create_from_options(options) as landmarker:
        for timestamp, frame, width, height in _iter_frames(cv2, video, start_s, end_s, sample_fps):
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            result = landmarker.detect_for_video(image, int(timestamp * 1000))
            for landmarks in result.face_landmarks or []:
                observation = _to_observation(landmarks, timestamp, width, height)
                if observation is not None:
                    observations.append(observation)
    log.info("%d opažanja lica u %s", len(observations), video.name)
    return observations


def _iter_frames(
    cv2: Any, video: Path, start_s: float, end_s: float, sample_fps: float
) -> Iterator[tuple[float, Any, int, int]]:
    """Daje `(t_od_početka, rgb_kadar, širina, visina)` na zadanoj frekvenciji uzorkovanja."""
    capture = cv2.VideoCapture(str(video))
    if not capture.isOpened():
        raise FaceDetectionUnavailable(f"OpenCV ne može otvoriti {video}")
    try:
        source_fps = float(capture.get(cv2.CAP_PROP_FPS) or 30.0)
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if width <= 0 or height <= 0:
            raise FaceDetectionUnavailable(f"{video} nema dimenzije kadra")
        step = max(1, round(source_fps / sample_fps))
        start_frame = int(start_s * source_fps)
        end_frame = int(end_s * source_fps)
        capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        frame_index = start_frame
        while True:
            ok, frame = capture.read()
            if not ok or frame_index >= end_frame:
                break
            if (frame_index - start_frame) % step == 0:
                timestamp = frame_index / source_fps - start_s
                yield timestamp, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), width, height
            frame_index += 1
    finally:
        capture.release()


def _to_observation(
    landmarks: Any, timestamp: float, width: int, height: int
) -> FaceObservation | None:
    if not landmarks:
        return None
    xs = [lm.x * width for lm in landmarks]
    ys = [lm.y * height for lm in landmarks]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    face_width = max_x - min_x
    face_height = max_y - min_y
    if face_width <= 1 or face_height <= 1:
        return None
    eye_y = sum(ys[i] for i in _EYE_LANDMARKS) / len(_EYE_LANDMARKS)
    return FaceObservation(
        t=timestamp,
        cx=(min_x + max_x) / 2,
        cy=(min_y + max_y) / 2,
        width=face_width,
        height=face_height,
        eye_y=eye_y,
        mar=_mouth_aspect_ratio(xs, ys),
    )


def _mouth_aspect_ratio(xs: list[float], ys: list[float]) -> float:
    try:
        opening = abs(ys[_LOWER_INNER_LIP] - ys[_UPPER_INNER_LIP])
        mouth_width = abs(xs[_RIGHT_MOUTH_CORNER] - xs[_LEFT_MOUTH_CORNER])
    except IndexError:
        return 0.0
    return opening / mouth_width if mouth_width > 1 else 0.0
