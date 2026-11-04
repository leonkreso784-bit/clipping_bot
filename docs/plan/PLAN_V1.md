# PLAN_V1 — lokalni alat za clipping

**Status:** nacrt, 4. 11. 2026. **Čeka Leonov OK** prije prve cigle.

**Cilj:** jedan Leonov dugi video daje 3 do 5 dobrih isječaka 9:16 s titlovima, na Leonovu računalu, uz
izmjereno trajanje svakog koraka.

**Tehnologija:** Python 3.12 (uv), FFmpeg 9, faster-whisper (MIT), PySceneDetect (BSD-3), MediaPipe
(Apache-2.0), yt-dlp (samo za Leonove kanale). Izbor i licence: `docs/istrazivanje/CLIPPING_ALATI.md`.

## Tok

| korak | naredba | tko | izlaz |
|---|---|---|---|
| 1. Ulaz | `clip ingest <datoteka ili link>` | program | izvor u `data/<id>/`, zapis prava (čiji je video) |
| 2. Analiza | `clip analyze <id>` | program | prijepis s vremenom riječi, rezovi scena, vrhovi glasnoće, `kandidati.json`, sažet `prijepis.md` |
| 3. Izbor | — | **Claude Code** | `odabir.json`: ID kandidata, naslov, udica, razlog |
| 4. Izrada | `clip render <id>` | program | rez, 9:16, karaoke titlovi, −14 LUFS, provjera izlaza |
| 5. Pregled | — | Leon | mapa `izlaz/<id>/` s MP4 i opisom po mreži |
| 6. Objava (kasnije) | `clip publish` | program | serija uz jedno odobrenje; YouTube, zatim Instagram i Facebook; TikTok ručno |

Kandidate (moguće početke i krajeve) slaže program iz granica rečenica, rezova scena i glasnoće. Claude bira
među njima i ne izmišlja vremena (ADR-005).

## Predlošci kadriranja

| predložak | kada | kako |
|---|---|---|
| glava koja priča | podcast, govor u kameru | MediaPipe prati lice, kadar 9:16 oko lica |
| gameplay | GTA 6 i druge igre | igra u sredini, zamućena pozadina; facecam gore ako postoji |

## Cigle

| cigla | sadržaj | dokaz |
|---|---|---|
| K0 | repozitorij, uv, pinovi, preflight (ruff, mypy, pytest) | preflight završava s 0 |
| K1 | `ingest` za datoteku i link (yt-dlp, samo Leonovi kanali), zapis prava | test s lokalnom datotekom; link na Leonov video |
| K2 | `analyze`: prijepis s vremenom riječi, scene, glasnoća, kandidati | izmjereno trajanje na Leonovu videu; kandidati poštuju granice rečenica |
| K3 | format `odabir.json`, provjera da Claude bira samo postojeće kandidate | neispravan odabir pada |
| K4 | `render`: rez, 9:16 (oba predloška), titlovi, glasnoća, provjera | isječak prolazi provjeru; titlovi u sinkronu ±100 ms |
| K5 | prvi stvarni prolaz: Leonov video → 3 do 5 isječaka | Leon ocjenjuje svaki isječak; tablica trajanja |
| K6 | objava: YouTube službeni API, serija uz jedno odobrenje | testni upload na Leonov kanal kao privatan |

## Otvorena pitanja

Popis je u `docs/records/BACKLOG.md`.
