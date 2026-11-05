"""Prijepis: NVIDIA Parakeet TDT 0.6B v3 kroz onnx-asr na CPU-u (ADR-008).

onnx-asr vraća tokene s vremenom početka, relativnim na VAD segment, bez vremena kraja.
`tokens_to_words` ih slaže u riječi s apsolutnim početkom i krajem.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from clipping.transcript import Transcript, Word

MODEL_NAME = "nemo-parakeet-tdt-0.6b-v3"
MODEL_LABEL = "parakeet-tdt-0.6b-v3"
DEFAULT_MODEL_DIR = Path("models/parakeet-v3")

#: VAD: Parakeet najbolje radi na dijelovima do ~30 s.
VAD_MAX_SPEECH_S = 30
VAD_MIN_SILENCE_MS = 300
VAD_SPEECH_PAD_MS = 100


@dataclass(frozen=True)
class SegmentTokens:
    """Jedan VAD segment: apsolutni start/end u sekundama, tokeni i njihova relativna vremena."""

    start: float
    end: float
    tokens: list[str]
    timestamps: list[float]


def tokens_to_words(segments: list[SegmentTokens]) -> list[Word]:
    """Token koji počinje razmakom otvara novu riječ; kraj riječi je početak sljedeće.

    Token od samog razmaka (brojevi i "$" nemaju oblik s razmakom) također otvara riječ.
    Kursor je zajednički za sve segmente: VAD-ovi dijelovi se preklapaju 0,2 s, pa riječ
    iz sljedećeg dijela ne smije početi prije kraja prethodne.
    """
    words: list[Word] = []
    cursor = 0.0
    for seg in segments:
        groups: list[tuple[str, float]] = []  # (tekst, relativni start)
        new_word = True
        for token, ts in zip(seg.tokens, seg.timestamps, strict=True):
            piece = token.strip()
            if not piece:
                new_word = new_word or token != ""
                continue
            if token.startswith(" ") or new_word:
                groups.append((piece, ts))
            else:
                text, start = groups[-1]
                groups[-1] = (text + piece, start)
            new_word = False

        for i, (text, rel_start) in enumerate(groups):
            start = max(cursor, seg.start + rel_start)
            if i + 1 < len(groups):
                end = max(start, seg.start + groups[i + 1][1])
            else:
                end = max(start, seg.end)
            words.append(Word(text, start, end))
            cursor = end
    return words


def transcribe(
    audio: Path, *, model_dir: Path = DEFAULT_MODEL_DIR, threads: int = 12
) -> Transcript:
    """Prepiši 16 kHz mono WAV; prvi poziv skida model u `model_dir`."""
    import onnx_asr
    import onnxruntime

    options = onnxruntime.SessionOptions()
    options.intra_op_num_threads = threads
    base = onnx_asr.load_model(MODEL_NAME, model_dir, sess_options=options)
    model = base.with_vad(
        onnx_asr.load_vad("silero"),
        max_speech_duration_s=VAD_MAX_SPEECH_S,
        min_silence_duration_ms=VAD_MIN_SILENCE_MS,
        speech_pad_ms=VAD_SPEECH_PAD_MS,
    ).with_timestamps()

    segments: list[SegmentTokens] = []
    for res in model.recognize(str(audio)):
        segments.append(
            SegmentTokens(
                start=float(res.start),
                end=float(res.end),
                tokens=list(res.tokens or []),
                timestamps=[float(t) for t in (res.timestamps or [])],
            )
        )
    return Transcript(words=tokens_to_words(segments), language="en", model=MODEL_LABEL)
