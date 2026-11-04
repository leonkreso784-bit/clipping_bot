# BACKLOG — otvoreno i parkirano

## Čeka Leona

| pitanje | zašto je važno |
|---|---|
| OK za dizajn `docs/superpowers/specs/2026-11-04-clipping-alat-design.md` | bez toga nema plana cigli ni koda |
| Računi: Gmail + Caleb Hammer (TikTok, Instagram poslovni + Facebook stranica, X), ClubWPT Gold (Instagram, YouTube); povezati na Clipping.net; PayPal; pridružiti se kampanjama | C4 i prva stvarna serija |
| Prvi tjedan ručno 1 do 2 objave dnevno s mobitela (zagrijavanje računa) | API objava tek na računima s poviješću |
| Vrijeme za pregled serije dnevno | određuje veličinu serije i raspored |
| Razgovor s računovođom prije prve veće isplate (PayPal iz inozemstva) | Leonova odgovornost; nije porezni savjet |
| Pisani dogovor s naručiteljem BOORA o vlasništvu koda | smije li se BOORA kod ikad koristiti ovdje |
| Whop i druge platforme kampanja | parkirano dok Clipping.net ne donese prvu isplatu |

## Provjeriti tehnički

| stavka | cigla |
|---|---|
| Parakeet TDT 0.6B v3: licenca (NVIDIA Open Model License) dopušta komercijalnu uporabu; onnx-asr daje vremena riječi; brzina na Leonovu CPU-u | C1 |
| Rezerva ako Parakeet padne: faster-whisper `medium` s 12 niti (autoclip je koristio 1 do 4) | C1 |
| MediaPipe na Pythonu 3.12 na Windowsu (proba: radi u autoclip venvu na 3.11) | C2 |
| Instagram `paid partnership` oznaka kroz Graph API: koje polje, za koje račune | C4 |
| YouTube upload neprovjerenog projekta: ostaje li javan | C4 |
| yt-dlp za YouTube poveznice iz briefa: treba li JavaScript runtime i PO token (proba: radilo bez) | C3 |
| Clipping.net: ima li API za clippere (pitati podršku) | C5 |

## Parkirano

| ideja | napomena |
|---|---|
| Desktop app za statistiku i zaradu (Tauri) | čita istu SQLite bazu; nakon C5 |
| Vlastiti GTA 6 kanal | Leon je 4. 11. odlučio da projekt radi clipping za druge; vidi ADR-007 |
| Plaćeni posrednik za TikTok (Upload-Post, Ayrshare) | samo ako ručna objava postane usko grlo; provjeriti da koriste auditiran službeni klijent |
| OpusClip kao mjerilo | Leon ne plaća; mjerilo su isječci iz probe i stvarni pregledi |
| Telegram sučelje | nije potrebno; pregled ide kroz mapu i `PREGLED.md` |
| Hrvatski jezik | nije cilj; kampanje su engleske |
