# BACKLOG — otvoreno i parkirano

## Čeka Leona

| pitanje | zašto je važno |
|---|---|
| Licence izvan pravila 8 u ovisnostima: `pathspec` 1.1.1 (MPL-2.0, samo dev kroz mypy), `tqdm` 4.70.1 (MPL-2.0 AND MIT, posredno kroz huggingface-hub za traku skidanja), `certifi` (MPL-2.0, CA certifikati za HTTPS) | ostaju ili se mijenja alat / skidanje modela |
| `pyproject.toml` deklarira `license = "MIT"` za Leonov projekt | privatni alat; jedan redak ako treba drukčije |
| Računi: Gmail + Caleb Hammer (TikTok, Instagram poslovni + Facebook stranica, X), ClubWPT Gold (Instagram, YouTube); povezati na Clipping.net; PayPal; pridružiti se kampanjama | C4 i prva stvarna serija |
| Prvi tjedan ručno 1 do 2 objave dnevno s mobitela (zagrijavanje računa) | API objava tek na računima s poviješću |
| Vrijeme za pregled serije dnevno | određuje veličinu serije i raspored |
| Razgovor s računovođom prije prve veće isplate (PayPal iz inozemstva) | Leonova odgovornost; nije porezni savjet |
| Pisani dogovor s naručiteljem BOORA o vlasništvu koda | smije li se BOORA kod ikad koristiti ovdje |
| Whop i druge platforme kampanja | parkirano dok Clipping.net ne donese prvu isplatu |

## Provjeriti tehnički

| što | gdje |
|---|---|
| Parakeet 22 min za 90 min zvuka, broj niti ne mijenja vrijeme: profilirati (VAD, enkoder, TDT dekoder, onnxruntime int8/fp16 inačica modela) | C1 mjerenje, ADR-008 |
| Zadnja riječ VAD segmenta traje do kraja segmenta; token „▁-" postaje samostalna riječ; putanje modela i zlatnog zvuka relativne na radni direktorij | pregled C1, `asr.py` |
| Obvezni tekst (`top_text`) završava na kraju zadnje riječi, ne isječka (rep ~0,3 s); QA ne provjerava obvezni tekst | pregled C2, `captions.py`, `qa.py` |
| Psovke maskiraju i „cocky“, „booby“, „titter“ (korijen + nastavak): popis iznimaka | pregled C2, `profanity.py` |
| `opencv-python` (kroz scenedetect) i `opencv-contrib-python` oba instalirani; `[tool.uv]` override da contrib pokrije oba | pregled C2, `pyproject.toml` |
| `models_dl` skida model bez timeouta; rotacija mobitelskih izvora se ne čita (`probe`), kadar bi bio krivo orijentiran; QA čita ASS a ne spaljeni video | pregled C2 |
| Memorija: s otvorenim VS Codeom, Dockerom/WSL-om i više Claude sesija RAM je pun (0,45 GB slobodno, 7 200 stranica/s) i prijepis ide 2 do 4× sporije; Parakeet drži 3,5 GB. Probati int8 inačicu modela (manje memorije) ili zatvarati alate prije `kreni` | dokaz C3, ADR-012 |
| Neovisni pregled (dokaz C3, ocjene 52–68): `clean_lower` je tanak i slabo čitljiv; isječci počinju bez konteksta (udica ne objašnjava tko govori); pregledač ne zna da je žig testni krug | `captions.py`, `select/prompt.md` |
| Opis za X: predložak + udica može prijeći 280 znakova; nema provjere duljine po platformi | `approve.py` |
| Isječci zlatnog posla `20261105-caleb-hammer-df0e` su u bazi `odobren`; novi posao istog videa odbit će te trenutke kao duplikate (namjerno, ADR-012) | `data/clipping.db` |

| stavka | cigla |
|---|---|
| Rezerva ako Parakeet padne: faster-whisper `medium` s 12 niti (autoclip je koristio 1 do 4) | C1 |
| MediaPipe na Pythonu 3.12 na Windowsu (proba: radi u autoclip venvu na 3.11) | C2 |
| Instagram `paid partnership` oznaka kroz Graph API: koje polje, za koje račune | C4 |
| YouTube upload neprovjerenog projekta: ostaje li javan | C4 |
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
