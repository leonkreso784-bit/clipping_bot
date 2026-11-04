# CLAUDE.md — Clipping (ključni kontekst)

> Učitava se svaku sesiju. **Drži ga sažetim: trenutno stanje, pravila i pointeri.**
> Ulaz u dokumentaciju: `docs/README.md` · odluke: `docs/records/DECISIONS.md` · plan: `docs/plan/PLAN_V1.md`.

## Što je projekt

Leonov vlastiti posao (Leon Kreso, jedini programer): lokalni alat koji od dugog videa napravi najbolje kratke
isječke 9:16 s titlovima, spremne za objavu na YouTube, Instagram, Facebook i TikTok. Alat radi na Leonovu
računalu, a **Claude Code bira trenutke** iz prijepisa, umjesto plaćenog API poziva po isječku.

Odvojen je od narudžbe za naručitelja (Matteo, BOORA Reels bot, `C:\Users\leonk\Documents\Bot za BOORA.ai`).
Iz tog repozitorija **ne kopiramo kod** dok vlasništvo nije pisano dogovoreno (ADR-001).

## Stanje

**Nema koda.** Plan prve verzije je nacrt i čeka Leonov OK: `docs/plan/PLAN_V1.md`.
**Svaku sesiju počni od `docs/records/SLJEDECA_SESIJA.md`.**

## Kritična pravila

1. **Bez koda prije odobrenog plana.** Leon odlučuje kad cigla počinje.
2. **Jedna cigla odjednom** (`/brick`): plan, grana, testovi, dokumenti, pa STANI za OK.
3. **Dokaz, ne tvrdnja.** Gotovo je ono što je izmjereno i što bi palo na starom kodu.
4. **Claude bira, program reže.** Claude vraća samo ID-eve kandidata i tekst (naslov, opis); vremena rezova,
   kadriranje i piksele određuje program (ADR-005).
5. **Ništa se ne objavljuje bez čovjeka.** Odobrenje vrijedi za cijelu seriju, ne za svaki video (ADR-003).
6. **Samo sadržaj na koji imamo pravo:** Leonov vlastiti, ili izvorne datoteke iz kampanje uz dopuštenje
   vlasnika. Tuđi GTA 6 sadržaj (traileri, leakovi, tuđi streamovi) ne obrađujemo (ADR-004).
7. **Samo službeni API-ji za objavu.** Nikad instagrapi, tiktok-uploader ili automatizacija preglednika (ADR-006).
8. **Ovisnosti se pinaju točno**, samo permisivne licence (MIT, Apache-2.0, BSD); GPL/AGPL i nekomercijalni
   modeli ne ulaze.
9. **Tajne, izvorni mediji i izlazni videi ne ulaze u git.** Push traži Leonov izričit OK.
10. **Jedna činjenica, jedno mjesto.** Duplikat se briše, ne sinkronizira.

## Računalo

Intel s 12 jezgri, 16 GB RAM, **bez NVIDIA grafičke** (Whisper na CPU-u), 124 GB slobodno na C:.
Instalirani su FFmpeg 9.0.2 i uv; yt-dlp nije.

## Gdje što piše

| pitanje | dokument |
|---|---|
| što gradimo sada | `docs/plan/PLAN_V1.md` |
| zašto je nešto tako | `docs/records/DECISIONS.md` |
| što nije riješeno | `docs/records/BACKLOG.md` |
| s čim početi sesiju | `docs/records/SLJEDECA_SESIJA.md` |
| istraživanja (pravila platformi, GTA 6, zarada, alati) | `docs/istrazivanje/` |

## Komande

`/next` (preporuka sljedeće cigle) · `/brick <opis>` (jedna cigla od kraja do kraja). Leži u
`.claude/commands/`, namjerno izvan gita (Leonov globalni gitignore).

## Rad s agentima

Model se bira po kvaliteti: `opus` za kod, pregled i istraživanje; `sonnet` za mehaničke izmjene. Jedan zadatak,
jedan agent, kratak izvještaj (najviše 15 redaka). Svaka cigla dobiva jedan neovisan pregled (`opus`).
