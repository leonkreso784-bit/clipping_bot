"""Preuzimanje modela koji nisu Python paketi (MediaPipe `face_landmarker.task`, Apache-2.0)."""

from __future__ import annotations

import logging
import urllib.request
from pathlib import Path

log = logging.getLogger(__name__)

#: Korijen repozitorija; `models/` je izvan gita.
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODELS_DIR = REPO_ROOT / "models"

FACE_LANDMARKER_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/"
    "face_landmarker.task"
)
FACE_LANDMARKER_SIZE = 3_758_596


def ensure_face_landmarker(models_dir: Path = DEFAULT_MODELS_DIR) -> Path:
    """Vrati putanju do `face_landmarker.task`; skine ga ako nedostaje ili je krive veličine."""
    target = models_dir / "face_landmarker.task"
    if target.is_file() and target.stat().st_size == FACE_LANDMARKER_SIZE:
        return target
    models_dir.mkdir(parents=True, exist_ok=True)
    log.info("skidam %s u %s", FACE_LANDMARKER_URL, target)
    tmp = target.with_suffix(".part")
    urllib.request.urlretrieve(FACE_LANDMARKER_URL, tmp)  # noqa: S310 — fiksni https URL
    size = tmp.stat().st_size
    if size != FACE_LANDMARKER_SIZE:
        tmp.unlink(missing_ok=True)
        raise OSError(f"face_landmarker.task ima {size} bajtova, očekivano {FACE_LANDMARKER_SIZE}")
    tmp.replace(target)
    return target
