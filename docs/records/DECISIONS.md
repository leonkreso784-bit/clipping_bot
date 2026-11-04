# DECISIONS — odluke i zašto

Oblik: kontekst, odluka, posljedice. Nova odluka dobiva sljedeći broj.

## ADR-001 — Zaseban repozitorij, odvojen od narudžbe naručitelja
**Datum:** 2026-11-04 · **Status:** ✅ Leon

**Kontekst.** Clipping je Leonov vlastiti posao. BOORA Reels bot je narudžba za naručitelja (Matteo), a
vlasništvo nad tim kodom nije pisano dogovoreno.

**Odluka.** Clipping živi u `C:\Users\leonk\Documents\Clipping`, privatno. Kod iz BOORA repozitorija se ne
kopira; gradimo nad otvorenim alatima. Istraživanja su prenesena kao snimke u `docs/istrazivanje/`.

**Posljedice.** Čisto vlasništvo. Ponovna uporaba BOORA koda tek nakon pisanog dogovora s naručiteljem.

## ADR-002 — Claude Code bira trenutke, bez plaćenog API-ja po isječku
**Datum:** 2026-11-04 · **Status:** ✅ Leon

**Kontekst.** Plaćeni API po isječku je Leonu preskup za volumen koji želi.

**Odluka.** Prva verzija je lokalni alat koji se koristi iz sesije Claude Codea. Program priprema prijepis i
kandidate, Claude Code bira, program izrađuje. Telegram dolazi kasnije, ako uopće.

**Posljedice.** Trošak je Leonova pretplata. Alat mora davati sažet, čitljiv prijepis da izbor stane u sesiju.

## ADR-003 — Objava se odobrava po seriji
**Datum:** 2026-11-04 · **Status:** ✅ Leon

**Odluka.** Ništa se ne objavljuje bez čovjeka, ali jedno odobrenje vrijedi za cijelu seriju (npr. 20 isječaka
s opisima i rasporedom), uz mogućnost izbacivanja pojedinih. Serija se zatim objavljuje po rasporedu.

## ADR-004 — Samo sadržaj na koji imamo pravo
**Datum:** 2026-11-04 · **Status:** ✅ Leon

**Kontekst.** Tuđi GTA 6 sadržaj (traileri, leakovi, cutscene, tuđi streamovi) vodi do DMCA zahtjeva i gašenja
računa; platforme ne monetiziraju ponovno objavljen tuđi sadržaj (`docs/istrazivanje/CLIPPING.md`).

**Odluka.** Ulazi su Leonove datoteke, linkovi na Leonove kanale (YouTube, Twitch) i izvorne datoteke iz
plaćenih clipping kampanja uz dopuštenje vlasnika. Svaki ulaz bilježi čiji je.

## ADR-005 — Claude bira kandidate, program određuje vremena i kadar
**Datum:** 2026-11-04 · **Status:** prijedlog, čeka Leonov OK uz PLAN_V1

**Odluka.** Program slaže kandidate iz granica rečenica, scena i glasnoće. Claude vraća samo ID kandidata,
naslov, udicu i razlog. Odabir koji pokazuje na nepostojeći kandidat se odbija.

**Posljedice.** Rez nikad ne presiječe riječ ni rečenicu; izbor je provjerljiv.

## ADR-006 — Objava samo preko službenih API-ja
**Datum:** 2026-11-04 · **Status:** ✅ Leon (iz istraživanja)

**Odluka.** YouTube Data API, Instagram i Facebook Graph API. TikTok ostaje ručna objava jer audit odbija alate
za objavu na vlastite račune. Neslužbeni alati (instagrapi, tiktok-uploader, automatizacija preglednika) ne
ulaze: krše uvjete i vode do zabrane računa.
