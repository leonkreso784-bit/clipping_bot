# Predaja za sljedeću sesiju

**Napisano:** 2026-11-05. Kad se sesija odradi, sadržaj se zamjenjuje novom predajom.

## Stanje

- Dizajn i plan C0 do C3 odobreni (4. 11.). C0 spojena u `main` (91a2b63).
- **C1 gotova i spojena**: `transcript.py`, `audio.py`, `asr.py` (Parakeet kroz onnx-asr), skripta
  `scripts/mjeri_prijepis.py`, zlatni video u `data/izvori/JvLklMRThYs/` (izvan gita). Pregled opusom odrađen,
  dva popravka ugrađena (token razmaka otvara riječ, zajednički kursor vremena).
- Leon 5. 11.: OK na C1, 22 min prijepisa prihvaćeno (ADR-008 ✅). C1 spojena u `main`. Otvoreno u BACKLOG-u
  „Čeka Leona": licence `tqdm` i `pathspec` (MPL-2.0), `license = "MIT"` u pyproject.
- Ništa nije pushano.

## Redoslijed na početku sesije

1. `git status` i `git log --oneline -5`.
2. `/brick C2` (zadaci 7 do 14 iz `docs/superpowers/plans/2026-11-04-clipping-cjevovod-c0-c3.md`).
3. Jedna cigla odjednom, dokaz prije tvrdnje, stani za OK.

## Prompt za početak

> Pročitaj `docs/records/SLJEDECA_SESIJA.md` i nastavi od tamo. Prvo mi reci stanje i što trebaš od mene.
