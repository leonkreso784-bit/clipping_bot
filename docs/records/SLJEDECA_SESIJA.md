# Predaja za sljedeću sesiju

**Napisano:** 2026-11-04 (navečer). Kad se sesija odradi, sadržaj se zamjenjuje novom predajom.

## Stanje

- Smjer projekta promijenjen: **plaćene clipping kampanje za druge kreatore** (Clipping.net), engleski, globalno.
  Vlastiti kanal i GTA 6 su parkirani (ADR-007).
- Odrađena proba s autoclipom na Caleb Hammer videu: `docs/istrazivanje/PROBA_AUTOCLIP.md`. Isječci u
  `izlaz/proba-2026-11-04-caleb-hammer/` (izvan gita). Leon: trenuci u redu, titlovi odlični, skakanje kadra ne smeta.
- Dizajn napisan: `docs/superpowers/specs/2026-11-04-clipping-alat-design.md`. Prošao neovisni pregled graditelja.
  **Leon odobrio 4. 11. 2026.** Psovke: zvjezdice u titlovima, zvuk netaknut.
- Plan izvedbe C0 do C3 odobren: `docs/superpowers/plans/2026-11-04-clipping-cjevovod-c0-c3.md`.
- **C0 gotova** na grani `feature/c0` (kostur paketa, preflight, ffmpeg omotač). Čeka Leonov OK za spajanje u `main` i početak C1.
- Scratchpad probe (autoclip venv, izvorni video, audio.wav, Whisperov transcript.json) ostaje: C1 ga kopira u `data/izvori/JvLklMRThYs/`.

## Redoslijed na početku sesije

1. `git status` i `git log --oneline -5`.
2. Pročitaj dizajn i `docs/records/BACKLOG.md` (odjeljak „Čeka Leona").
3. Ako je `feature/c0` još nespojena: pitaj Leona za OK, spoji u `main` (bez pusha).
4. Zatim `/brick C1` (zadaci 3 do 6 iz plana; prvo kopirati probu u `data/izvori/JvLklMRThYs/`).
5. Jedna cigla odjednom, dokaz prije tvrdnje, stani za OK.

## Prompt za početak

> Pročitaj `docs/records/SLJEDECA_SESIJA.md` i nastavi od tamo. Prvo mi reci stanje i što trebaš od mene.
