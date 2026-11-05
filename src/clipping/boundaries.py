"""Granice rezova: iz raspona riječi (Claudeov izbor) u sekunde za rezanje.

Po uzoru na artbyjazi/autoclip (MIT, Jad Ghazi), `pipeline/boundaries.py`. Tri koraka:
1. snap na rečenicu (rez nikad ne otvara ni zatvara misao napola),
2. stezanje trajanja na profil kampanje, uvijek na granici rečenice,
3. poravnanje na izmjerenu tišinu (udah prije prve riječi, pauza nakon zadnje).

Kandidat koji se ne može složiti unutar trajanja bez rezanja usred rečenice vraća `None`:
bolje ga ispustiti nego isporučiti ružan rez (ADR-005, pravilo 4).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from clipping.audio import Silence
from clipping.transcript import Transcript

#: Koliko riječi oko predložene granice tražimo kraj rečenice.
SENTENCE_SEARCH_WORDS = 12
#: Jastuk kad nema izmjerene tišine uz granicu.
FALLBACK_LEAD_S = 0.25
FALLBACK_TAIL_S = 0.35
#: Koliko daleko od granice tražimo tišinu.
SILENCE_SEARCH_RADIUS_S = 0.75
#: Koliko u tišinu prije prve riječi ulazimo (udah bez mrtvog takta).
SILENCE_LEAD_S = 0.12
#: Koliko držimo nakon zadnje riječi.
SILENCE_TAIL_S = 0.28
#: Rub tišine ima histerezu; ne režemo bliže od ovoga.
SILENCE_MARGIN_S = 0.04


@dataclass(frozen=True)
class Boundary:
    start_s: float
    end_s: float
    start_word: int
    end_word: int

    @property
    def duration_s(self) -> float:
        return self.end_s - self.start_s


def refine(
    transcript: Transcript,
    start_word: int,
    end_word: int,
    *,
    silences: list[Silence],
    min_duration_s: float,
    max_duration_s: float,
) -> Boundary | None:
    """Pretvori raspon riječi u granicu za rez ili `None` ako se ne može složiti u profil."""
    if not transcript.words:
        return None
    last_index = len(transcript.words) - 1
    start_word = max(0, min(start_word, last_index))
    end_word = max(start_word, min(end_word, last_index))

    start_word = snap_start_to_sentence(transcript, start_word)
    end_word = snap_end_to_sentence(transcript, end_word)
    if end_word <= start_word:
        return None

    clamped = _clamp_duration(transcript, start_word, end_word, min_duration_s, max_duration_s)
    if clamped is None:
        return None
    end_word = clamped

    first_word_start, last_word_end = transcript.time_range(start_word, end_word)
    start_s = align_start(first_word_start, silences)
    end_s = align_end(last_word_end, silences)
    # Poravnanje samo širi. Preko stropa prvo skrati vodeću tišinu (nikad preko prve riječi),
    # pa tek onda rep iza zadnje riječi; zadnja riječ ostaje cijela jer _clamp_duration to jamči.
    over = end_s - start_s - max_duration_s
    if over > 0:
        start_s = min(start_s + over, first_word_start)
    if end_s - start_s > max_duration_s:
        end_s = max(start_s + max_duration_s, last_word_end)
    return Boundary(max(0.0, start_s), end_s, start_word, end_word)


def snap_start_to_sentence(transcript: Transcript, index: int) -> int:
    """Prva riječ najbliže rečenice; pri izjednačenju radije ranije (udica se ne smije odrezati)."""
    if index <= 0:
        return 0
    for offset in range(SENTENCE_SEARCH_WORDS + 1):
        for candidate in (index - offset, index + offset):
            if candidate <= 0:
                return 0
            if candidate >= len(transcript.words):
                continue
            if transcript.words[candidate - 1].ends_sentence:
                return candidate
    return index


def snap_end_to_sentence(transcript: Transcript, index: int) -> int:
    """Zadnja riječ najbliže rečenice; pri izjednačenju radije kasnije (cijela misao)."""
    last_index = len(transcript.words) - 1
    if index >= last_index:
        return last_index
    for offset in range(SENTENCE_SEARCH_WORDS + 1):
        for candidate in (index + offset, index - offset):
            if candidate >= last_index:
                return last_index
            if candidate < 0:
                continue
            if transcript.words[candidate].ends_sentence:
                return candidate
    return index


def _clamp_duration(
    transcript: Transcript,
    start_word: int,
    end_word: int,
    min_duration_s: float,
    max_duration_s: float,
) -> int | None:
    """Pomakni kraj da trajanje stane u profil, samo na granici rečenice; inače `None`."""
    words = transcript.words
    start_s = words[start_word].start

    def duration_at(index: int) -> float:
        return words[index].end - start_s

    if duration_at(end_word) > max_duration_s:
        for candidate in range(end_word, start_word, -1):
            if duration_at(candidate) <= max_duration_s and words[candidate].ends_sentence:
                end_word = candidate
                break
        else:
            return None

    if duration_at(end_word) < min_duration_s:
        for candidate in range(end_word + 1, len(words)):
            if duration_at(candidate) > max_duration_s:
                break
            if words[candidate].ends_sentence:
                end_word = candidate
                if duration_at(end_word) >= min_duration_s:
                    break

    duration = duration_at(end_word)
    if duration < min_duration_s or duration > max_duration_s:
        return None
    return end_word


def align_start(start_s: float, silences: list[Silence]) -> float:
    """Povuci početak u tišinu ispred prve riječi; nikad iza početka prve riječi.

    Tišina može završiti iza početka riječi (detektor tišine i vremena riječi se ne slažu na
    nekoliko stotinki): tada bi `earliest` pao usred riječi i rez bi je odsjekao (dokaz C3, 5. 11.).
    """
    silence = _closest(silences, start_s, key=lambda s: s.end)
    if silence is None:
        return max(0.0, start_s - FALLBACK_LEAD_S)
    earliest = min(silence.start + SILENCE_MARGIN_S, silence.end)
    preferred = silence.end - SILENCE_LEAD_S
    return max(0.0, min(start_s, max(earliest, min(preferred, start_s))))


def align_end(end_s: float, silences: list[Silence]) -> float:
    """Gurni kraj u tišinu iza zadnje riječi."""
    silence = _closest(silences, end_s, key=lambda s: s.start)
    if silence is None:
        return end_s + FALLBACK_TAIL_S
    latest = max(silence.end - SILENCE_MARGIN_S, silence.start)
    preferred = silence.start + SILENCE_TAIL_S
    return max(end_s, min(preferred, latest))


def _closest(
    silences: list[Silence], t: float, *, key: Callable[[Silence], float]
) -> Silence | None:
    best: Silence | None = None
    best_distance = SILENCE_SEARCH_RADIUS_S
    for silence in silences:
        distance = abs(key(silence) - t)
        if distance <= best_distance:
            best_distance = distance
            best = silence
    return best
