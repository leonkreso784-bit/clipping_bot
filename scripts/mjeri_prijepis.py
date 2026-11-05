"""Mjerenje prijepisa na zlatnom videu (cigla C1).

Pokretanje: uv run python scripts/mjeri_prijepis.py data/izvori/JvLklMRThYs/audio.wav
Opcije: --niti 12,6,0 (0 = zadano), --motor parakeet|whisper-medium (rezerva iz plana, zadatak 6;
pokreće se s `uv run --with faster-whisper==1.2.1 ...`, nije ovisnost projekta).
Ispisuje zidno vrijeme po broju niti, sprema transcript.json uz zvuk i računa podudaranje
riječi s Whisperovom referencom (whisper_referenca.json u istoj mapi) na prvih 300 s.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import time
from pathlib import Path

from clipping.asr import transcribe
from clipping.transcript import Transcript, Word

REFERENCE_WINDOW_S = 300.0
_PUNCT = re.compile(r"[^\w\s']", re.UNICODE)


def normalise(words: list[str]) -> list[str]:
    return [w for w in (_PUNCT.sub("", x).lower().strip() for x in words) if w]


def agreement(ours: Transcript, reference: Transcript, *, window_s: float) -> float:
    a = normalise([w.text for w in ours.words if w.start < window_s])
    b = normalise([w.text for w in reference.words if w.start < window_s])
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def transcribe_whisper_medium(audio: Path, *, threads: int) -> Transcript:
    """Rezerva iz ADR-008: faster-whisper medium (int8) na CPU-u. Nije ovisnost projekta."""
    import wave  # noqa: PLC0415

    import numpy as np  # noqa: PLC0415
    from faster_whisper import WhisperModel  # noqa: PLC0415

    # WAV se čita ovdje (16 kHz mono PCM16 iz audio.extract_audio); PyAV preskačemo.
    with wave.open(str(audio)) as wav:
        assert wav.getframerate() == 16000 and wav.getnchannels() == 1 and wav.getsampwidth() == 2
        samples = np.frombuffer(wav.readframes(wav.getnframes()), dtype=np.int16)
    pcm = samples.astype(np.float32) / 32768.0
    model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=threads)
    segments, _info = model.transcribe(pcm, language="en", word_timestamps=True, vad_filter=True)
    words = [Word(w.word.strip(), w.start, w.end) for seg in segments for w in seg.words or []]
    return Transcript(words=words, language="en", model="faster-whisper-medium-int8")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows cijev je cp1252
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", type=Path)
    parser.add_argument("--niti", default="12,6,0", help="brojevi niti, 0 = zadano")
    parser.add_argument("--motor", default="parakeet", choices=["parakeet", "whisper-medium"])
    args = parser.parse_args()
    suffix = "" if args.motor == "parakeet" else "_whisper_medium"

    audio: Path = args.audio
    reference_path = audio.with_name("whisper_referenca.json")
    reference = Transcript.load(reference_path) if reference_path.exists() else None

    rows: list[tuple[int, float, int, float | None]] = []
    best: tuple[float, Transcript] | None = None
    for raw in args.niti.split(","):
        threads = int(raw)
        started = time.perf_counter()
        if args.motor == "parakeet":
            transcript = transcribe(audio, threads=threads if threads > 0 else 0)
        else:
            transcript = transcribe_whisper_medium(audio, threads=threads)
        elapsed = time.perf_counter() - started
        score = agreement(transcript, reference, window_s=REFERENCE_WINDOW_S) if reference else None
        rows.append((threads, elapsed, len(transcript.words), score))
        print(f"niti={threads or 'zadano'}: {elapsed:.0f} s, {len(transcript.words)} riječi, "
              f"podudaranje={'n/a' if score is None else f'{score:.3f}'}", flush=True)  # fmt: skip
        if best is None or elapsed < best[0]:
            best = (elapsed, transcript)

    assert best is not None
    out = audio.with_name(f"transcript{suffix}.json")
    best[1].save(out)
    summary = {
        "audio": str(audio),
        "motor": args.motor,
        "rezultati": [
            {"niti": t, "sekunde": round(e, 1), "rijeci": n, "podudaranje": s}
            for t, e, n, s in rows
        ],
        "najbolje_s": round(best[0], 1),
        "prolaz_vrijeme": best[0] < 600,
        "prolaz_podudaranje": all(s is None or s >= 0.85 for *_, s in rows),
    }
    audio.with_name(f"mjerenje_prijepisa{suffix}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["prolaz_vrijeme"] and summary["prolaz_podudaranje"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
