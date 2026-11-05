"""Psovke u titlovima: zvjezdice umjesto slova, zvuk ostaje netaknut (dizajn §11a.3).

Popis je engleski jer su kampanje na engleskom. Usporedba ne gleda velika slova i pokriva
uobičajene nastavke (-ing, -ed, -s, -es, -er, -y, -ty). Prvo slovo ostaje da se riječ prepozna.
"""

from __future__ import annotations

import re

#: Korijeni psovki (mala slova). Riječ se maskira kad je točno korijen ili korijen + nastavak.
PROFANITY: frozenset[str] = frozenset(
    {
        "fuck",
        "fucker",
        "motherfuck",
        "motherfucker",
        "shit",
        "bullshit",
        "ass",
        "asshole",
        "bitch",
        "bastard",
        "damn",
        "goddamn",
        "dick",
        "dickhead",
        "cock",
        "cunt",
        "pussy",
        "piss",
        "prick",
        "slut",
        "whore",
        "twat",
        "wank",
        "wanker",
        "bollocks",
        "jackass",
        "dumbass",
        "arse",
        "arsehole",
        "crap",
        "douche",
        "douchebag",
        "nigga",
        "nigger",
        "faggot",
        "retard",
        "tit",
        "tits",
        "boob",
    }
)

#: Nastavci koje maskiramo zajedno s korijenom ("fucking", "shitty", "bitches").
_SUFFIXES = ("", "s", "es", "ing", "in", "ed", "er", "ers", "y", "ty")

_WORD = re.compile(r"[A-Za-z']+")


def _is_profane(word: str) -> bool:
    lower = word.lower().replace("'", "")
    for root in PROFANITY:
        if not lower.startswith(root):
            continue
        rest = lower[len(root) :]
        if rest in _SUFFIXES:
            return True
        # "shitty", "pissed": udvostručeni suglasnik prije nastavka.
        if root and rest[:1] == root[-1] and rest[1:] in _SUFFIXES[1:]:
            return True
    return False


def _mask_word(match: re.Match[str]) -> str:
    word = match.group(0)
    if not _is_profane(word):
        return word
    return word[0] + "*" * (len(word) - 1)


def mask(text: str) -> str:
    """Zamijeni psovke zvjezdicama: prvo slovo ostaje, interpunkcija i razmaci se čuvaju."""
    return _WORD.sub(_mask_word, text)
