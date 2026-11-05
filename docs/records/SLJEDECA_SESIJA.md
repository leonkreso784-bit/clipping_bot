# Predaja za sljedeću sesiju

**Napisano:** 2026-11-05. Kad se sesija odradi, sadržaj se zamjenjuje novom predajom.

## Stanje

- Dizajn i plan C0 do C3 odobreni (4. 11.). C0 spojena u `main` (91a2b63).
- **C1 gotova na grani `feature/c1`**: `transcript.py`, `audio.py`, `asr.py` (Parakeet kroz onnx-asr), skripta
  `scripts/mjeri_prijepis.py`, zlatni video u `data/izvori/JvLklMRThYs/` (izvan gita). Pregled opusom odrađen,
  dva popravka ugrađena (token razmaka otvara riječ, zajednički kursor vremena).
- **Čeka Leona:** ADR-008 — Parakeet treba 22 min za 90 min videa (cilj je bio 10), rezerva Whisper medium 2 sata.
  Licenca CC-BY-4.0 prolazi. Odluka: prihvatiti 22 min ili tražiti ubrzanje (BACKLOG). Plus licence `tqdm` i
  `pathspec` (MPL-2.0) i `license = "MIT"` u pyproject (BACKLOG „Čeka Leona").
- Ništa nije pushano.

## Redoslijed na početku sesije

1. `git status` i `git log --oneline -5`.
2. Ako `feature/c1` još nije spojena: Leonov OK na ADR-008, spoji u `main` (bez pusha).
3. Zatim `/brick C2` (zadaci 7 do 14 iz `docs/superpowers/plans/2026-11-04-clipping-cjevovod-c0-c3.md`).
4. Jedna cigla odjednom, dokaz prije tvrdnje, stani za OK.

## Prompt za početak

> Pročitaj `docs/records/SLJEDECA_SESIJA.md` i nastavi od tamo. Prvo mi reci stanje i što trebaš od mene.
