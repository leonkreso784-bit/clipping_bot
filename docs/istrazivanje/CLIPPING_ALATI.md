> **Snimka iz BOORA repozitorija, 4. 11. 2026.** Poveznice `../records/…` i `../architecture/…` vode u
> `C:\Users\leonk\Documents\Bot za BOORA.ai\docs\`, ne u ovaj repozitorij.

# Ideja: alati otvorenog koda za clipping i objavu

Koji javni projekti mogu pomoći da dugi video postane kratki isječak 9:16 s titlovima i da se objavi
kroz službene API-je, i koliko se uklapaju u naš stack (Python 3.14 uz `uv` i točno pinane ovisnosti,
FFmpeg 7.1, faster-whisper 1.2.1, Claude, Playwright/Chromium, Postgres, aiogram). Provjereno 2026-11-04:
zvjezdice, zadnji commit, izdanja i licence s GitHub API-ja i PyPI-ja, licence modela s Hugging Facea.

> Nije plan i nije obećanje. Pravila platformi, autorska prava, GTA 6 i monetizacija su u
> [CLIPPING.md](./CLIPPING.md) i ovdje se ne ponavljaju; Meta objava za naručitelja je u [OBJAVA.md](./OBJAVA.md).
> Ništa odavde nije instalirano ni pokrenuto: ocjena je iz koda, README-a i metapodataka.

**Preporuka:** **koristiti** (ovisnost uz ADR-014) · **ideja** (pročitati kod, napisati svoje) ·
**izbjegavati**. Licence: projekt je komercijalan i privatan, pa su MIT, Apache-2.0, BSD i Unlicense u
redu, a GPL, AGPL i nekomercijalne licence su **rizik**.

## 1. Cjeloviti „AI clipperi"

| projekt | što radi | licenca | aktivnost | zrelost | uklapanje | rizik | preporuka |
|---|---|---|---|---|---|---|---|
| [OpenShorts](https://github.com/mutonby/openshorts) | Gemini bira 3 do 15 trenutaka iz prijepisa i scena; raspored po sceni: praćenje lica, mutna pozadina, dva govornika jedan iznad drugoga, ekran iznad predavača; titlovi; objava | MIT, osim mape `cloud/` (komercijalna licenca) | 7.459 ★, commit 1. 11. 2026. | bez izdanja; oko 108 testnih datoteka | Python 3.11 u Dockeru; faster-whisper 1.2.1, scenedetect, TransNetV2, MediaPipe, **ultralytics**, torch; GPU neobavezan (CPU 5 do 8 min za 8 min videa, prema README-u); objava preko Upload-Post (SaaS) | ultralytics je **AGPL-3.0**; `yt-dlp` nepinan; LLM je Gemini | **ideja**: najbolji uzor za izbor rasporeda po sceni, `ssrf_guard.py` i `quality_probe.py` |
| [AI-Youtube-Shorts-Generator](https://github.com/Anil-matcha/AI-Youtube-Shorts-Generator) (bivši SamurAIGPT) | LLM prvo razvrsta vrstu videa, zatim boduje kandidate (udica, emocionalni vrh, otkriće, sukob, citat); OpenCV praćenje lica | MIT | 5.749 ★, commit 3. 11. 2026. | bez izdanja i testova | Python 3.10+; lokalni način: yt-dlp, faster-whisper, OpenCV, OpenAI ili Gemini; zadani način šalje sve na MuAPI | README je reklama za plaćeni API autora; ovisnosti `>=` | **ideja**: kategorije za bodovanje u uputi Claudeu |
| [ClipsAI](https://github.com/ClipsAI/clipsai) | dijeli prijepis po temama (TextTiling s ugradbama rečenica); reframe po aktivnom govorniku | MIT | 562 ★, zadnji commit 17. 1. 2024. | PyPI 0.2.1; 7 testova | WhisperX (Python < 3.14), pyannote s HF tokenom, facenet-pytorch, torch | napušten; ne radi na 3.14 | **ideja**: TextTiling kao izvor kandidata bez LLM-a |
| [FunClip](https://github.com/modelscope/FunClip) | rez po odabranom tekstu ili govorniku, Gradio sučelje, LLM prijedlozi | MIT | 6.489 ★, commit 1. 11. 2026. | 4 izdanja (v2.2.1, 1. 9. 2026.), testovi | Python 3.12, FunASR (kineski i engleski), torch, Gradio 4 | među LLM putevima je **g4f** (neovlašten pristup tuđim LLM-ovima); hrvatskog nema | **ideja**: rez po odabranim rečenicama |
| [SupoClip](https://github.com/FujiwaraChoki/supoclip) | LLM (Gemini, GPT, Claude, Ollama) bira 3 do 7 isječaka; lice u sredini; titlovi riječ po riječ; objava na YouTube, TikTok i Instagram | **AGPL-3.0** | 2.517 ★, commit 3. 11. 2026. | bez izdanja | Docker; AssemblyAI za vremena riječi | AGPL | **izbjegavati** kod; tok vrijedi pogledati |
| [Clips Kitty](https://github.com/ColinGPT9/clips-studio) | Twitch, Kick i YouTube streamovi u isječke; lokalni Ollama i faster-whisper; objava i „hands-off" za praćeni kanal | **AGPL-3.0** | 205 ★, commit 3. 11. 2026. | 8 izdanja (v2.1.0, 21. 10. 2026.), testovi | YouTube preko službenog API-ja; ostalo preko Upload-Post i WoopSocial | AGPL; autopilot je suprotan [ADR-002](../records/DECISIONS.md) | **izbjegavati** |
| [AutoClip](https://github.com/zhouxiaoka/autoclip) | desktop (Tauri); pravila trajanja i okvira po platformi; „paket za objavu" (naslov, opis, hashtagovi, naslovnica) u ZIP-u | MIT | 9.957 ★, commit 3. 11. 2026. | 19 izdanja (v1.5.8, 2. 11. 2026.) | kineski fokus (Bilibili, Douyin, Qwen); Python ≥ 3.10 | — | **ideja**: paket za ručnu objavu (TikTok) |
| [ClippyMe](https://github.com/fralapo/clippyme) | Gemini bira trenutke, praćenje govornika, uređivanje u pregledniku, zakazivanje | MIT | 62 ★, commit 13. 10. 2026. | bez izdanja | Python ≥ 3.11; objava preko Zernio (SaaS) | mali projekt | **ideja** |
| [Reelsfy](https://github.com/eddieoz/reels-clips-automator) | dugi video u Reels | MIT | 232 ★, zadnji commit 23. 9. 2023. | — | — | napušten | **izbjegavati** |

**Nije clipping:** [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) (MIT, 138 tis. ★)
i [ShortGPT](https://github.com/RayVentura/ShortGPT) (MIT, zadnji commit 2. 2025.) slažu video iz teme,
ne režu postojeći. [MoneyPrinterV2](https://github.com/FujiwaraChoki/MoneyPrinterV2) je AGPL-3.0 i
objavljuje kroz Selenium i `undetected_chromedriver`: **izbjegavati**.

**Zaključak odjeljka:** nijedan cjeloviti projekt nije dobar kao ovisnost. Svi imaju vlastiti LLM sloj
(Gemini, OpenAI), vlastiti raspored i titlove, nepinane ovisnosti ili Python ispod 3.14, a dobar dio
vuče AGPL komponentu. Vrijedni su kao **čitanje**: kako biraju trenutke i kako biraju raspored.

## 2. Gradivni blokovi

### Prijepis s vremenima riječi

| projekt | licenca | aktivnost | uklapanje | rizik | preporuka |
|---|---|---|---|---|---|
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | MIT | 26.458 ★, commit 2. 11. 2026. | **već ga imamo** (1.2.1); `word_timestamps=True`, a `vad_filter=True` koristi ugrađeni Silero VAD; bez torcha | hrvatski WER oko 34 % ([BACKLOG](../records/BACKLOG.md)) | **koristiti** |
| [WhisperX](https://github.com/m-bain/whisperX) | BSD-2 | 25.075 ★, commit 22. 10. 2026., 217 otvorenih issue-a | poravnanje wav2vec2 daje točnija vremena riječi; za hrvatski koristi `classla/wav2vec2-xls-r-parlaspeech-hr`; PyPI 3.8.6 traži **Python < 3.14** i torch 2.8 | licenca hrvatskog modela na HF stranici **nije navedena**; torch | **ideja**: samo ako vremena riječi faster-whispera ne budu dovoljna za karaoke titlove, i tad kao zaseban radnik |
| [stable-ts](https://github.com/jianfch/stable-ts) | MIT | repozitorij **arhiviran** | — | nema održavanja | **izbjegavati** |
| [whisper-timestamped](https://github.com/linto-ai/whisper-timestamped) | **AGPL-3.0** | commit 28. 9. 2026. | — | AGPL | **izbjegavati** |

Usput: postoji hrvatski fino podešen Whisper [GoranS/whisper-large-v3-turbo-hr-parla](https://huggingface.co/GoranS/whisper-large-v3-turbo-hr-parla)
(Apache-2.0, malo preuzimanja); za faster-whisper bi ga trebalo pretvoriti u CTranslate2. Pripada pitanju
hrvatskog WER-a u BACKLOG-u, ne clippingu.

### Granice kadrova i tišina

| projekt | licenca | aktivnost | uklapanje | preporuka |
|---|---|---|---|---|
| [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) | BSD-3 | 5.344 ★, commit 2. 11. 2026.; PyPI 0.7.2 (12. 10. 2026.) | Python ≥ 3.10, OpenCV ili PyAV, CPU | **koristiti** |
| [TransNetV2](https://github.com/soCzech/TransNetV2) | MIT | 1.074 ★, zadnji commit 12. 2023. | neuronska mreža, torch ili TensorFlow | **ideja**: samo ako PySceneDetect promašuje brze rezove u gameplayu |
| [auto-editor](https://github.com/WyattBlue/auto-editor) | Unlicense | 5.753 ★, commit 2. 11. 2026. | sada program u Nimu, PyPI je omotač | **ideja**: rezanje tišine po glasnoći, isto se radi FFmpegom |

### Tko govori

| projekt | licenca koda | licenca modela | uklapanje | preporuka |
|---|---|---|---|---|
| [pyannote.audio](https://github.com/pyannote/pyannote-audio) | MIT; 10.757 ★, commit 3. 11. 2026.; PyPI 4.0.7 | [community-1](https://huggingface.co/pyannote/speaker-diarization-community-1): **CC-BY-4.0** (navesti autora); [3.1](https://huggingface.co/pyannote/speaker-diarization-3.1): MIT; oba traže HF račun i prihvat uvjeta; „precision-2" je plaćeni pyannoteAI | torch, na CPU-u sporo | **ideja** za kasnije: treba samo za podcast s dva govornika; gameplay ga ne treba |

### Lice i reframe 16:9 u 9:16

| projekt | licenca | aktivnost | uklapanje | rizik | preporuka |
|---|---|---|---|---|---|
| [MediaPipe](https://github.com/google-ai-edge/mediapipe) | Apache-2.0 | 37.541 ★, commit 4. 11. 2026.; PyPI 1.2.2 kao `py3-none` kotač | Face Detector, CPU; Python 3.14 **nije isproban** | 275 otvorenih issue-a | **koristiti** |
| [pyautoflip](https://github.com/AhmedHisham1/pyautoflip) | MIT | 23 ★, commit 21. 10. 2026. | traži Python < 3.14 | mali projekt | **ideja**: glađenje putanje kadra (AutoFlip) |
| [auto-vertical-reframe](https://github.com/KazKozDev/auto-vertical-reframe) | MIT | 25 ★, commit 4. 10. 2026. | PySceneDetect i MediaPipe | mali projekt | **ideja** |
| [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) | **AGPL-3.0** (komercijalna licenca se plaća) | 63.091 ★ | torch | AGPL; ulazi i preko OpenShortsa | **izbjegavati** |
| [InsightFace](https://github.com/deepinsight/insightface) | kod MIT, **modeli samo za nekomercijalno istraživanje** | 30.133 ★ | — | licenca modela | **izbjegavati** |
| [facenet-pytorch](https://github.com/timesler/facenet-pytorch) | MIT | 5.176 ★, commit 9. 2025. | torch | licenca uvježbanih težina nije provjerena | **izbjegavati** dok se ne provjeri |

### Titlovi „karaoke" stila

| projekt | licenca | aktivnost | uklapanje | preporuka |
|---|---|---|---|---|
| [pycaps](https://github.com/francozanardi/pycaps) | MIT | 230 ★, commit 30. 9. 2026. | **isti obrazac kao naš sloj**: titlovi su HTML i CSS koje crta Playwright; klasa za riječ koja se upravo izgovara, oznake riječi pravilima ili AI-jem; testiran na 3.10 do 3.12; nije na PyPI-ju (ime `pycaps` ondje je drugi paket iz 2017.) | **ideja**: preuzeti model CSS stanja riječi u naš Chromium sloj, bez ovisnosti |
| [captacity](https://github.com/unconv/captacity) | MIT | 140 ★, zadnji commit 6. 2024. | MoviePy | **izbjegavati** (napušten) |
| [auto-subtitle](https://github.com/m1guelpf/auto-subtitle) | MIT | 2.297 ★, zadnji commit 7. 2024., 96 otvorenih issue-a | — | **izbjegavati** |
| ASS format i FFmpeg `subtitles` filtar (libass) | dio FFmpega | — | karaoke oznake `\k` po riječi | **ideja**: rezerva ako Chromium za duge videe bude prespor |

### Signali za „highlight"

| projekt | licenca | aktivnost | što daje | rizik | preporuka |
|---|---|---|---|---|---|
| FFmpeg `ebur128` i `astats` | dio FFmpega | — | glasnoća po vremenu | — | **koristiti** (već u [CLIPPING.md](./CLIPPING.md) §4) |
| [PANNs inference](https://github.com/qiuqiangkong/panns_inference) | MIT | 275 ★, zadnji commit 3. 2024. | 527 AudioSet klasa: smijeh, pljesak, eksplozija, pucnjava | torch; licenca težina zasebno nije navedena | **ideja** |
| [laughter-detection](https://github.com/jrgillick/laughter-detection) | MIT | 298 ★, zadnji commit 7. 2024. | samo smijeh | torch, napušten | **ideja** |
| [inaSpeechSegmenter](https://github.com/ina-foss/inaSpeechSegmenter) | MIT | 919 ★; PyPI 0.8.0 (9. 2025.) | govor, glazba, šum | TensorFlow | **ideja** |
| [chat-downloader](https://github.com/xenova/chat-downloader) | MIT | 1.199 ★; zadnje izdanje 9. 2023. | gustoća chata uz VOD | čita Twitch kroz **neslužbeni** `gql.twitch.tv` s Client-ID-jem web klijenta | **izbjegavati** |
| [TwitchDownloader](https://github.com/lay295/TwitchDownloader) | MIT | 4.001 ★, C#, 282 otvorena issue-a | isto | isti neslužbeni GQL | **izbjegavati** |

Za chat kao signal zakonit put je vlastiti kanal: chat se bilježi **dok stream traje** kroz službeni
Twitchov chat, a ne preuzima naknadno.

## 3. Automatska objava

### Službeni put

| platforma | alat | licenca | aktivnost | uklapanje | preporuka |
|---|---|---|---|---|---|
| YouTube | [google-api-python-client](https://github.com/googleapis/google-api-python-client) i `google-auth-oauthlib` | Apache-2.0 | 8.964 ★; PyPI 2.201.0 (30. 9. 2026.) i 1.5.0 | Python ≥ 3.10; nastavljivi upload (`MediaFileUpload(resumable=True)`) | **koristiti** |
| YouTube | [youtube-upload](https://github.com/tokland/youtube-upload) | **GPL-3.0** | zadnji commit 4. 2024., 114 otvorenih issue-a | — | **izbjegavati** |
| Instagram i Facebook | službenog Python SDK-a za objavu Reelsa nema; [facebook-business](https://github.com/meta/facebook-python-business-sdk) je za Marketing API i ima Metinu licencu (samo uz Facebookove API-je, pod Platform Policy) | — | — | objava su tri do četiri HTTP poziva (spremnik, stanje, objava) | **graditi**: tanki vlastiti klijent nad HTTP-om |
| Instagram i Facebook | [python-facebook](https://github.com/sns-sdks/python-facebook) | Apache-2.0 | 381 ★, zadnji commit 2. 2026. | omotač Graph API-ja | **ideja** |
| TikTok | službenog Python SDK-a za Content Posting API nema; [tiktok-business-api-sdk](https://github.com/tiktok/tiktok-business-api-sdk) (MIT) je za oglase | — | — | vlastiti HTTP klijent; uvjeti audita u [CLIPPING.md](./CLIPPING.md) §5 | **graditi** ili ručno |
| sve | [Postiz](https://github.com/gitroomhq/postiz-app), samostalno hostan raspored kroz službeni OAuth | **AGPL-3.0**, TypeScript | 40.822 ★, commit 3. 11. 2026. | zaseban servis; za TikTok i dalje treba vlastiti auditirani klijent | **izbjegavati** kao dio sustava; može se pogledati kao uzor |
| sve | [Mixpost](https://github.com/inovector/mixpost) Lite | MIT, PHP i Laravel | 3.902 ★, commit 3. 2026. | Lite je okrnjena verzija komercijalnog proizvoda; koje mreže podržava nije provjereno | **izbjegavati** (drugi stack) |
| sve | SaaS posrednici: Upload-Post (koriste ga OpenShorts i Clips Kitty; besplatno 10 objava mjesečno), Zernio, WoopSocial | zatvoreni | — | jedan API za sve mreže | **otvoreno**: koriste li službene API-je i auditiran TikTok klijent, nije potvrđeno |

### Neslužbeni put: samo kao upozorenje

Ovi alati glume preglednik ili mobilnu aplikaciju. Krše uvjete platformi o automatiziranom pristupu
([CLIPPING.md](./CLIPPING.md), odjeljak b), traže kolačiće ili lozinku računa i vode do zabrane računa.
Ne ulaze u sustav ni za probu.

| projekt | licenca | aktivnost | metoda |
|---|---|---|---|
| [instagrapi](https://github.com/subzeroid/instagrapi) | MIT | 7.060 ★ | privatni Instagram API; sam README kaže da je krhko i preporučuje službene API-je |
| [tiktok-uploader](https://github.com/wkaisertexas/tiktok-uploader) | MIT | 781 ★ | Playwright s kolačićima prijave |
| [TiktokAutoUploader](https://github.com/makiisthenes/TiktokAutoUploader) | **AGPL-3.0** | 1.218 ★ | privatni API, potpisi zahtjeva iz headless Chromiuma, proxy po računu |
| [social-auto-upload](https://github.com/dreammis/social-auto-upload) | MIT | 16.092 ★ | Playwright i kolačići (Douyin, TikTok, YouTube i drugi) |
| [youtube_uploader_selenium](https://github.com/linouk23/youtube_uploader_selenium) | MIT | 667 ★, zadnji commit 2. 2023. | Selenium |

## 4. Preuzimanje

| projekt | licenca | aktivnost | napomena |
|---|---|---|---|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Unlicense; gotovi izvršni paketi uključuju GPLv3+ kod | 205.025 ★, izdanje 2026.10.26, 2.760 otvorenih issue-a | Python ≥ 3.11 (3.14 u redu); verzija mora biti pinana i nadograđivana uz gate (ADR-014); uvjeti i sigurnost u [CLIPPING.md](./CLIPPING.md) |
| [gallery-dl](https://github.com/mikf/gallery-dl) | **GPL-2.0** | 20.363 ★ | licenca: **izbjegavati** |
| [Instaloader](https://github.com/instaloader/instaloader) | MIT | 13.771 ★ | neslužbeni pristup Instagramu; isti uvjeti kao gore |

## 5. Preporučeni sklop

Nad postojećim stackom, bez novog jezika i bez torcha u prvom koraku:

```text
datoteka ili dopušteni izvor
  → prijepis: faster-whisper 1.2.1, word_timestamps + vad_filter            (imamo)
  → signali: PySceneDetect kadrovi + FFmpeg ebur128 glasnoća                  (novo: scenedetect)
  → kandidati: program reže na rečenice i kadrove, numerira ih                (gradimo)
  → odabir: Claude vraća ID-eve kandidata i razlog, nikad vremena ni piksele  (ADR-005)
  → rez i reframe: FFmpeg + MediaPipe lice + glađenje putanje,                (novo: mediapipe)
                   ili predložak za gameplay u Chromium sloju
  → titlovi: naš Chromium sloj, CSS stanje riječi po uzoru na pycaps          (gradimo)
  → naša provjera izlaza → odobrenje u Telegramu                              (imamo)
  → objava: YouTube google-api-python-client; Meta vlastiti HTTP klijent;     (novo: google-api-python-client)
            TikTok ručno ili posrednik
```

| blok | alat | nova ovisnost | licenca | GPU |
|---|---|---|---|---|
| prijepis | faster-whisper | ne | MIT | ne |
| kadrovi | PySceneDetect (+ `opencv-python-headless`) | da | BSD-3, Apache-2.0 | ne |
| glasnoća | FFmpeg | ne | — | ne |
| odabir | Claude | ne | — | ne |
| lice | MediaPipe | da | Apache-2.0 | ne |
| titlovi | Chromium sloj | ne | — | ne |
| YouTube | google-api-python-client, google-auth-oauthlib | da | Apache-2.0 | ne |
| Meta, TikTok | vlastiti klijent | ne | — | ne |

Kasnije, samo ako mjerenje pokaže potrebu: pyannote za dva govornika, PANNs za smijeh i eksplozije,
WhisperX poravnanje za hrvatski. Sva tri vuku torch i zato idu u zaseban radnik s vlastitim Pythonom.

## 6. Graditi ili koristiti

| graditi sami | koristiti gotovo | ne koristiti |
|---|---|---|
| rezač kandidata, uputu za ocjenu, glađenje putanje kadra, karaoke titlove u Chromium sloju, tanke klijente za Meta i TikTok, red objave s limitima u Postgresu | faster-whisper, PySceneDetect, MediaPipe, FFmpeg, google-api-python-client | cjelovite clippere kao ovisnost, ultralytics, InsightFace modele, whisper-timestamped, g4f, neslužbene uploadere, Twitch GQL alate |

Zašto ne fork OpenShortsa: Gemini u središtu, Python 3.11, AGPL ultralytics u ovisnostima, nepinan
yt-dlp i vlastiti raspored. Fork bi značio prepisati upravo dijelove koji su kod nas već odluke
(ADR-005, ADR-014, ADR-019).

## Otvoreno

1. Jesu li vremena riječi iz faster-whispera dovoljno točna za hrvatske karaoke titlove, ili treba
   poravnanje? Mjeri se na zlatnom skupu prije bilo kakvog WhisperX-a.
2. Licenca hrvatskog wav2vec2 modela (`classla`) nije navedena: pitati autore prije uporabe.
3. Radi li MediaPipe 1.2.2 na Pythonu 3.14 u našoj Docker slici? Isprobati u privremenoj mapi.
4. Upload-Post, Zernio i slični: službeni API-ji, auditiran TikTok klijent, cijena i što rade s videom.
5. Treba li uopće diarizacija, ili je za podcast dovoljno praćenje lica?
6. Treba li Leonu chat kao signal, tj. hoće li clipati vlastiti Twitch kanal?
