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

## ADR-005 — Claude bira riječima, program određuje vremena i kadar
**Datum:** 2026-11-04 · **Status:** ✅ Leon, potvrđeno probom (`docs/istrazivanje/PROBA_AUTOCLIP.md`)

**Odluka.** Program daje Claudeu cijeli prijepis s indeksom uz svaku riječ. Claude vraća indeks prve i zadnje
riječi, naslov, udicu, ocjenu i razlog; nikad sekunde ni piksele. Program pomiče rezove na granicu rečenice ili
tišine, odbija indekse izvan prijepisa i trajanja izvan profila kampanje, i sam kadrira.

**Posljedice.** Rez nikad ne presiječe riječ; izbor je provjerljiv; nema plaćenog API-ja (Claude Code u sesiji ili
`claude -p`). Raniji oblik (program unaprijed slaže kandidate) je napušten jer je proba pokazala da Claude dobro
bira iz cijelog prijepisa od 17.000 riječi.

## ADR-006 — Objava samo preko službenih API-ja
**Datum:** 2026-11-04 · **Status:** ✅ Leon (iz istraživanja)

**Odluka.** YouTube Data API, Instagram i Facebook Graph API. TikTok ostaje ručna objava jer audit odbija alate
za objavu na vlastite račune. Neslužbeni alati (instagrapi, tiktok-uploader, automatizacija preglednika) ne
ulaze: krše uvjete i vode do zabrane računa.

## ADR-007 — Projekt radi plaćene clipping kampanje za druge kreatore, na engleskom
**Datum:** 2026-11-04 · **Status:** ✅ Leon

**Kontekst.** Prvi nacrt plana ciljao je Leonov vlastiti video i GTA 6 kanal. Leon je to odbio: posao je clipping
za druge kreatore kroz plaćene kampanje (Clipping.net, kasnije možda Whop), gdje se plaća po 100.000 provjerenih
pregleda na clipperovim vlastitim računima.

**Odluka.** Ulazi su isključivo videi iz kampanja (brief daje poveznicu ili datoteku). Jezik je engleski, publika
globalna, cilj najviša kvaliteta. Prve kampanje: Caleb Hammer i ClubWPT Gold. Vlastiti kanal, GTA 6 i hrvatski su
parkirani (BACKLOG).

**Posljedice.** Profil kampanje (YAML) nosi pravila briefa: platforme, žig, obvezni tekst, računi. Alat ne
objavljuje na platformi koju kampanja ne plaća. Zapis prava = kampanja + brief + datum (ADR-004).

## ADR-008 — Prijepis: Parakeet TDT na CPU-u umjesto Whispera
**Datum:** 2026-11-04 · **Status:** ⚠️ izmjereno u C1 5. 11. 2026.: licenca prolazi, vrijeme ne (22 min umjesto 10); Leon odlučuje je li 22 min prihvatljivo

**Kontekst.** Proba: faster-whisper `large-v3-turbo` na Leonovu CPU-u (12 jezgri, bez grafičke) trajao je 103 minute
za 90 minuta videa i koristio 1 do 4 jezgre.

**Odluka.** Prijepis radi NVIDIA Parakeet TDT 0.6B v3 kroz `onnx-asr` (bez torcha), s VAD-om u dijelovima.
Uvjet: ispod 10 minuta za zlatni video i licenca dopušta komercijalnu uporabu.
**Licenca (C1, 5. 11. 2026.):** kartica `nvidia/parakeet-tdt-0.6b-v3` i ONNX pretvorba `istupakov/parakeet-tdt-0.6b-v3-onnx`
obje kažu CC-BY-4.0 („GOVERNING TERMS: Use of this model is governed by the CC-BY-4.0 license“, „ready for
commercial/non-commercial use“). Prolazi pravilo 8; navođenje autora je u `THIRD_PARTY_LICENSES.md`.
**Mjerenje (C1, 5. 11. 2026., zlatni video 90 min, `scripts/mjeri_prijepis.py`):**

| motor | niti | vrijeme | riječi | podudaranje s Whisper turbo referencom (prvih 300 s) |
|---|---|---|---|---|
| Parakeet TDT 0.6B v3 (onnx-asr) | 12 | 1452 s | 16853 | 0.908 |
| Parakeet TDT 0.6B v3 (onnx-asr) | 6 | 1409 s | 16853 | 0.908 |
| Parakeet TDT 0.6B v3 (onnx-asr) | zadano | **1322 s** | 16853 | 0.908 |
| rezerva: faster-whisper medium int8 | 12 | 7197 s | 16702 | 0.962 |

Ni jedan motor ne ulazi u 10 minuta. Parakeet je 5,4 puta brži od rezerve i 4,7 puta brži od turba iz probe
(103 min); broj niti ne mijenja vrijeme, pa je usko grlo nešto drugo (BACKLOG). Podudaranje rezerve je više
jer je referenca također Whisper. **Parakeet ostaje**; rezerva se ne ugrađuje (faster-whisper vuče PyAV s
FFmpeg binarnim datotekama i nije potreban). Prag od 10 minuta nije ispunjen: Leon odlučuje prihvaća li
22 minute po videu od 90 minuta ili se traži ubrzanje (BACKLOG).

**Posljedice.** Isti oblik izlaza kao u probi (riječi s vremenima). Cenzura psovki više ne dolazi besplatno iz
modela; program ima popis riječi.

## ADR-009 — autoclip (MIT) je uzor, ne ovisnost
**Datum:** 2026-11-04 · **Status:** ✅ Leon (kvaliteta probe prihvaćena)

**Odluka.** Kadriranje po licu (MediaPipe, glatka putanja kadra, jedan FFmpeg prolaz) i karaoke ASS titlovi
(pysubs2, libass) grade se po uzoru na artbyjazi/autoclip, uz navođenje izvora i MIT napomenu. autoclip se ne
uzima kao ovisnost jer nosi vlastiti LLM sloj, bazu, Whisper i web sučelje. Graditelj smije vendorati pojedine
module uz zapis ovdje.

## ADR-010 — Instagram i YouTube kroz API, TikTok i X ručno iz pripremljene mape
**Datum:** 2026-11-04 · **Status:** ✅ Leon

**Odluka.** Instagram (Graph API) i YouTube (Data API) objavljuju se iz reda s limitima po računu. TikTok (API bez
audita objavljuje samo privatno) i X (API za video je plaćen) objavljuje Leon s mobitela iz mape
`mobitel/<racun>/` s MP4 i opisom; alat čeka poveznicu. Dok računi nemaju tjedan ručne povijesti, sve platforme
idu ručno (zagrijavanje). Dopunjuje ADR-006.

## ADR-011 — Jedan račun po kreatoru i platformi; oznaka plaćene suradnje uvijek
**Datum:** 2026-11-04 · **Status:** ✅ Leon

**Odluka.** Svaka kampanja ima vlastite račune (npr. Caleb Hammer: TikTok, Instagram, X). Računi se ne dijele
među kampanjama. Svaka objava nosi oznaku plaćene suradnje (platformina oznaka gdje API dopušta, i "#ad" /
"Paid partnership with <kreator>" u opisu). Isti isječak se nikad ne objavljuje dvaput na istoj platformi, a
isječci koji se preklapaju više od 50 % s već objavljenima u istoj kampanji se odbijaju.

**Posljedice.** Kazna za spam ili prava pogađa jedan račun, ne sve. Objave ostaju javne do isplate (pravilo Clipping.neta).
