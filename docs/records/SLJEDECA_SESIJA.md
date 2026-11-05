# Predaja za sljedeću sesiju

**Napisano:** 2026-11-05. Kad se sesija odradi, sadržaj se zamjenjuje novom predajom.

## Stanje

- Dizajn i plan C0 do C3 odobreni (4. 11.). C0 i C1 spojene u `main` (ADR-008: 22 min prijepisa prihvaćeno).
- **C2 gotova na grani `feature/c2`** (zadaci 7 do 14): `profile.py`, `candidates.py`, `boundaries.py`,
  `profanity.py`, `reframe/*`, `captions.py` (+ fontovi Anton/Inter, OFL), `export.py`, `qa.py`,
  `scripts/izrezi_probu.py`. Dokaz: 9 isječaka u `izlaz/proba-c2/` (izvan gita), svi QA OK, prosjek 107 s.
- **Čeka Leona:** OK za spajanje C2; pravi žig kampanje u `kampanje/caleb-hammer/zig.png` (sad je testni
  bijeli krug); licence `tqdm`, `certifi`, `pathspec` (MPL-2.0) i `license = "MIT"` (BACKLOG „Čeka Leona").
- Ništa nije pushano.

## Redoslijed na početku sesije

1. `git status` i `git log --oneline -5`.
2. Ako `feature/c2` još nije spojena: Leonov OK, spoji u `main` (bez pusha).
3. Zatim `/brick C3` (zadaci 15 do 21 iz `docs/superpowers/plans/2026-11-04-clipping-cjevovod-c0-c3.md`:
   baza stanja, `kreni`, izbor kroz `claude -p`, pregled, mapa za mobitel).
4. Jedna cigla odjednom, dokaz prije tvrdnje, stani za OK.

## Prompt za početak

> Pročitaj `docs/records/SLJEDECA_SESIJA.md` i nastavi od tamo. Prvo mi reci stanje i što trebaš od mene.
