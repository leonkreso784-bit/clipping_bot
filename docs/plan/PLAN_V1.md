# PLAN_V1 — alat za plaćene clipping kampanje

**Status:** nacrt, 4. 11. 2026. Dizajn je u `docs/superpowers/specs/2026-11-04-clipping-alat-design.md` i **čeka Leonov OK**.
Nakon OK-a dizajna ovaj plan se razrađuje u cigle (`superpowers:writing-plans`) i tek onda kreće kod.

**Cilj:** jedan dugi video iz kampanje (60 do 120 min) → 6 do 10 isječaka 9:16 s titlovima, žigom i tekstom po
briefu, u manje od 30 minuta na Leonovu CPU-u, bez ručnih koraka između "kreni" i mape za pregled; nakon odobrenja
serije objava na Instagram i YouTube kroz službene API-je, TikTok i X ručno iz pripremljene mape.

**Prve kampanje:** Caleb Hammer (75 $/100K, TikTok + Instagram + X) i ClubWPT Gold (250 $/100K, Instagram + YouTube).

**Tehnologija (prijedlog, potvrđuje se po cigli):** Python 3.12 (uv, pinano), FFmpeg 9 (libass), Parakeet TDT 0.6B v3
kroz onnx-asr (CPU), MediaPipe (Apache-2.0) za lice, pysubs2 za ASS titlove, yt-dlp samo za poveznice iz briefa,
SQLite za stanje, google-api-python-client za YouTube, tanki HTTP klijent za Instagram Graph API.
artbyjazi/autoclip (MIT) je uzor za kadriranje i titlove, ne ovisnost. Proba: `docs/istrazivanje/PROBA_AUTOCLIP.md`.

## Tok

| korak | tko | izlaz |
|---|---|---|
| 1. ulaz iz briefa (poveznica ili datoteka) + zapis prava | program | `data/<izvor>/source.mp4`, zapis u bazi |
| 2. zvuk, sličice, prijepis s vremenima riječi, tišine | program | `transcript.json`, `window.txt` s `[i]riječ` |
| 3. izbor kandidata | **Claude Code** (`claude -p`) | `candidates.json`: indeksi riječi, naslov, udica, ocjena, opis po platformi |
| 4. rezanje po profilu kampanje: kadar po licu, karaoke titlovi, žig, obvezni tekst, −14 LUFS | program | `izlaz/<posao>/*.mp4` |
| 5. provjera: automatska + neovisni Claude pregled po briefu | program | `PREGLED.md` s nalazima |
| 6. pregled serije | **Leon** | `ODOBRENO` ili izbačeni isječci |
| 7. objava: Instagram i YouTube iz reda s limitima; TikTok i X mapa za mobitel | program / Leon | poveznice u bazi |
| 8. prijava poveznica na Clipping.net, praćenje pregleda i isplata | Leon / program | tablice `objava`, `pregledi`, `isplata` |

## Cigle (prijedlog redoslijeda; detalji nakon OK-a dizajna)

| cigla | sadržaj | dokaz |
|---|---|---|
| C0 | repozitorij, uv, pinovi, preflight (ruff, mypy, pytest), `.env` i `data/`/`izlaz/` izvan gita | preflight 0 |
| C1 | prijepis: Parakeet kroz onnx-asr na CPU-u, VAD u dijelovima, vremena riječi; provjera licence | zlatni video (90 min) ispod 10 min; isti oblik izlaza kao proba |
| C2 | rezanje po profilu kampanje: YAML profil, kadar po licu, ASS titlovi, žig, obvezni tekst, glasnoća; automatska provjera | 9 isječaka iz probe reproducirani s žigom; provjera pada kad žig nedostaje |
| C3 | baza stanja (SQLite), `clipping kreni` od kraja do kraja do mape za pregled, `claude -p` izbor, nastavak nakon prekida | prekid usred posla i nastavak bez ponavljanja prijepisa |
| C4 | objava: Instagram Graph API i YouTube Data API iz reda s limitima; mapa za TikTok/X; oznaka plaćene suradnje | testna objava na Leonov račun; duplikat se odbija |
| C5 | praćenje pregleda, prijava poveznica, isplate; `clipping prati` u Task Scheduleru | dnevne brojke u bazi za jednu stvarnu seriju |

## Otvorena pitanja

Popis je u `docs/records/BACKLOG.md`.
