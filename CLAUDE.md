# CLAUDE.md — Clipping (ključni kontekst)

> Učitava se svaku sesiju. **Drži ga sažetim: trenutno stanje, pravila i pointeri.**
> Ulaz u dokumentaciju: `docs/README.md` · odluke: `docs/records/DECISIONS.md` · plan: `docs/plan/PLAN_V1.md`.

## Što je projekt

Leonov vlastiti posao (Leon Kreso, jedini programer): **clipping za druge kreatore kroz plaćene kampanje**
(Clipping.net; plaća se po 100.000 pregleda na Leonovim računima). Lokalni alat na Leonovu računalu od dugog
videa iz kampanje napravi isječke 9:16 s titlovima, žigom i tekstom po briefu, na engleskom, i objavi ih kroz
službene API-je (Instagram, YouTube) ili pripremi za ručnu objavu (TikTok, X). **Claude Code bira trenutke** iz
prijepisa umjesto plaćenog API poziva po isječku. Kad Leon kaže "kreni", alat radi sam do mape za pregled.
Nije za Leonov vlastiti kanal ni GTA 6 (ADR-007).

Odvojen je od narudžbe za naručitelja (Matteo, BOORA Reels bot, `C:\Users\leonk\Documents\Bot za BOORA.ai`).
Iz tog repozitorija **ne kopiramo kod** dok vlasništvo nije pisano dogovoreno (ADR-001).

## Stanje

**C0 i C1 spojene u `main`; C2 gotova na grani `feature/c2`** (čeka Leonov OK za spajanje, pa C3). Dizajn `docs/superpowers/specs/2026-11-04-clipping-alat-design.md` je odobren (4. 11. 2026.); plan cigli
`docs/plan/PLAN_V1.md` i `docs/superpowers/plans/` se razrađuju iz njega. Proba s autoclipom: `docs/istrazivanje/PROBA_AUTOCLIP.md`.
**Svaku sesiju počni od `docs/records/SLJEDECA_SESIJA.md`.**

## Kritična pravila

1. **Bez koda prije odobrenog plana.** Leon odlučuje kad cigla počinje.
2. **Jedna cigla odjednom** (`/brick`): plan, grana, testovi, dokumenti, pa STANI za OK.
3. **Dokaz, ne tvrdnja.** Gotovo je ono što je izmjereno i što bi palo na starom kodu.
4. **Claude bira, program reže.** Claude vraća indekse prve i zadnje riječi i tekst (naslov, udica, opis);
   vremena rezova, kadriranje i piksele određuje program (ADR-005).
5. **Ništa se ne objavljuje bez čovjeka.** Odobrenje vrijedi za cijelu seriju, ne za svaki video (ADR-003).
6. **Samo sadržaj iz kampanje** (brief daje poveznicu ili datoteku), sa zapisom prava. Ništa tuđe izvan
   kampanje (ADR-004, ADR-007).
7. **Samo službeni API-ji za objavu.** Nikad instagrapi, tiktok-uploader ili automatizacija preglednika (ADR-006).
   TikTok i X idu ručno iz pripremljene mape (ADR-010). Jedan račun po kreatoru, oznaka plaćene suradnje uvijek (ADR-011).
8. **Ovisnosti se pinaju točno**, samo permisivne licence (MIT, Apache-2.0, BSD); GPL/AGPL ne ulaze. Težine
   modela i fontovi moraju dopuštati komercijalnu uporabu (CC-BY, OFL prolaze;
   nekomercijalni i "research only" ne).
9. **Tajne, izvorni mediji i izlazni videi ne ulaze u git.** Push traži Leonov izričit OK.
10. **Jedna činjenica, jedno mjesto.** Duplikat se briše, ne sinkronizira.

## Preflight

`uv run python scripts/preflight.py` (ruff check, ruff format --check, mypy src, pytest bez `golden`). Mora završiti
s `PREFLIGHT 0` prije svakog commita. Okruženje: `uv sync` (Python 3.12, pinovi u `pyproject.toml` i `uv.lock`).

## Računalo

Intel s 12 jezgri, 16 GB RAM, **bez NVIDIA grafičke** (Whisper na CPU-u), 124 GB slobodno na C:.
Instalirani su FFmpeg 9.0.2 i uv; yt-dlp nije.

## Gdje što piše

| pitanje | dokument |
|---|---|
| što gradimo i zašto (dizajn) | `docs/superpowers/specs/2026-11-04-clipping-alat-design.md` |
| cigle | `docs/plan/PLAN_V1.md` |
| zašto je nešto tako | `docs/records/DECISIONS.md` |
| što nije riješeno | `docs/records/BACKLOG.md` |
| s čim početi sesiju | `docs/records/SLJEDECA_SESIJA.md` |
| istraživanja (pravila platformi, zarada, alati) i proba | `docs/istrazivanje/` |

## Komande

`/next` (preporuka sljedeće cigle) · `/brick <opis>` (jedna cigla od kraja do kraja). Leži u
`.claude/commands/`, namjerno izvan gita (Leonov globalni gitignore).

## Rad s agentima

Model se bira po kvaliteti: `opus` za kod, pregled i istraživanje; `sonnet` za mehaničke izmjene. Jedan zadatak,
jedan agent, kratak izvještaj (najviše 15 redaka). Svaka cigla dobiva jedan neovisan pregled (`opus`).
