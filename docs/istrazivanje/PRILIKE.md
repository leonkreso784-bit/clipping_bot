> **Snimka iz BOORA repozitorija, 4. 11. 2026.** Poveznice `../records/…` i `../architecture/…` vode u
> `C:\Users\leonk\Documents\Bot za BOORA.ai\docs\`, ne u ovaj repozitorij.

# Ideja: prilike za bolje, brže i utjecajnije Reelove

Popis alata i mogućnosti koje bi Reelove naručitelja (poslovni profil, nekretnine i poslovni sadržaj)
učinile boljima, bržima ili utjecajnijima. Provjereno 2026-11-04, osim gdje piše drukčije.

> Nije plan i nije obećanje. Svaka stavka čeka vlastiti plan i Leonov OK. Objava ostaje na naredbu
> čovjeka ([ADR-002](../records/DECISIONS.md)), a AI i dalje piše samo tekst, raspored slaže program (ADR-005).
> Ovo nije pravni savjet. „Nije potvrđeno" znači da službeni izvor nije pročitan ili nije odgovorio.

Ne ponavlja [IZVORI.md](./IZVORI.md) (trendovi i vijesti) ni [OBJAVA.md](./OBJAVA.md) (objava i zakazivanje).

**Oznake:** vrijednost i trud su **V** visoka · **S** srednja · **N** niska; trud **M** mali · **S** srednji ·
**V** velik, s obzirom na postojeći stack. `worker-media` nema internet ([ARCHITECTURE.md](../architecture/ARCHITECTURE.md)),
pa sve što dohvaća s mreže ide kroz drugi servis ili unaprijed spremljenu knjižnicu na disku.

## Odmah, bez koda

| što | zašto | izvor |
|---|---|---|
| Glazbu za Reel urednik dodaje **u Instagram aplikaciji** iz Meta Sound Collection | Poslovni računi nemaju puni glazbeni katalog Instagrama; Sound Collection je besplatan i dopušten za komercijalnu uporabu, ali samo na Metinim platformama | [Instagram pomoć](https://help.instagram.com/402084904469945) (sažetak pretrage; stranica se nije dala dohvatiti) |
| Na poslovnom TikToku samo **Commercial Music Library** | Poslovni račun ne smije komercijalno koristiti opću knjižnicu | [TikTok CML](https://ads.tiktok.com/help/article/commercial-music-library) |
| Opis objave s **najviše 5 hashtagova** | Instagram je u prosincu 2025. ograničio hashtagove na 5 po objavi i Reelu (prije 30), uvodi se postupno | [Business Today](https://www.businesstoday.in/technology/news/story/no-more-hashtag-stuffing-instagram-limits-hashtag-usage-to-just-5-per-reel-and-post-507444-2025-12-19) (sekundarno) |

## 1. Zvuk i glazba

Ključna činjenica: kad bot jednom objavljuje preko API-ja, glazbu iz aplikacije ne može dodati
(dokumentacija o tome šuti, [OBJAVA.md](./OBJAVA.md)), pa mora biti **upečena u MP4** i licencirana za sve
platforme na koje ide. Isti MP4 s pjesmom iz Sound Collectiona ne smije na TikTok.

| ideja | što je | vrijednost | trud | trošak | pravni rizik | od naručitelja |
|---|---|---|---|---|---|---|
| **Kurirana lokalna knjižnica glazbe** | 20 do 40 pjesama na disku s oznakom raspoloženja; Claude predloži raspoloženje riječju, program bira pjesmu, FFmpeg spušta glazbu ispod govora (`sidechaincompress`) | **S**: fotografija danas daje Reel bez zvuka; vrijedi tek uz objavu preko API-ja | **M** | ovisi o izvoru, vidi ispod | srednji: licenca ≠ zaštita od Content ID zahtjeva | stil glazbe, pitanje 8 |
| Pixabay Music | besplatno, bez navođenja autora, prerada dopuštena; zabranjena samostalna redistribucija | izvor za knjižnicu | — | 0 € | Content ID zahtjevi mogući jer dio skladatelja registrira pjesme; Pixabay nudi potvrdu o licenci za osporavanje ([sažetak licence](https://pixabay.com/service/license-summary/), [HeyGen pomoć](https://help.heygen.com/en/articles/8986144-content-id-claims-on-youtube), sekundarno) | — |
| Epidemic Sound | pretplata s API-jem za razvojne programere | izvor za knjižnicu, čišći od Pixabaya | — | Pro oko 16,99 $/mj uz godišnje plaćanje, Business oko 30 $/mj ([photutorial](https://photutorial.com/epidemic-sound-pricing), sekundarno; [cjenik](https://www.epidemicsound.com/pricing/) iznose nije prikazao) | oglasne kampanje traže Pro ili Enterprise; Pro nije za tvrtke s prihodom iznad 10 mil. $ ([poslovna pretplata](https://www.epidemicsound.com/business-subscription/)) | tko plaća pretplatu |
| Artlist | pretplata | — | — | nije potvrđeno (stranica cjenika vraća 403) | nije potvrđeno | — |
| ~~YouTube Audio Library~~ | — | — | — | — | **odbačeno**: standardna licenca je vezana uz YouTube, uporaba drugdje nije službeno potvrđena ([Lickd](https://lickd.co/youtube-audio-library/), sekundarno) | — |
| Hrvatski sintetički glas (TTS) | glas čita tekst Reela, npr. za Reel od fotografija | **N**: profil živi od stvarnih snimki i izvornog zvuka; sintetički glas lako zvuči „automatski" (anti-cilj PRD-a) | **S** | vidi ispod; tekst od 170 znakova stoji manje od 0,02 $ | srednji: AI zvuk podliježe označavanju (vidi upozorenja); kloniranje stvarnog glasa traži pisani pristanak | presuda na sluh, pristanak |
| ElevenLabs | hrvatski podržan u Multilingual v2, Flash v2.5, v3 i v4 ([modeli](https://elevenlabs.io/docs/overview/models)) | najprirodniji kandidat | — | 0,08 $ na 1.000 znakova (v2, v3), Flash 0,04 $; Starter 6 $/mj ([API cjenik](https://elevenlabs.io/pricing/api)) | komercijalna licenca po planu nije potvrđena na stranici cjenika | — |
| Azure Speech | dva glasa, `hr-HR-GabrijelaNeural` i `hr-HR-SreckoNeural`, bez HD i višejezičnih glasova ([jezici](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts)) | najslabiji izbor za hrvatski | — | 0,5 mil. znakova mjesečno besplatno; iznad oko 15 $ na milijun (službena stranica cijenu nije prikazala, [sekundarno](https://www.beri.net/article/elevenlabs-vs-cartesia-vs-azure-tts-latency-pricing-voice-cloning-2026)) | nizak | — |
| Google Chirp 3 HD | `hr-HR` podržan ([dokumentacija](https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd)) | dobar kandidat za usporedbu | — | 30 $ na milijun znakova, prvi milijun mjesečno besplatno ([cjenik](https://cloud.google.com/text-to-speech/pricing)); imena hrvatskih glasova nisu potvrđena | nizak | — |

## 2. Titlovi i pristupačnost

| ideja | što je | vrijednost | trud | trošak | pravni rizik | od naručitelja |
|---|---|---|---|---|---|---|
| **Titlovi iz Whisper prijepisa** | `faster-whisper` već prepisuje govor lokalno; s vremenom po riječi program slaže titl u sigurnu zonu predloška, Chromium ga crta kao i ostatak sloja | **V**: Reelovi se često gledaju bez zvuka, a govor je bez titla izgubljen | **S** | 0 € | nizak | izgled titla, mjesto u predlošku, pitanje 5 |
| Potvrda prijepisa u Telegramu | prije izrade bot pošalje prijepis, urednik ispravi jednom porukom | **V**: nužno, jer je hrvatski WER `large-v3-turbo` oko 34 % ([BACKLOG](../records/BACKLOG.md)); titl s greškom gori je od nijednog | **M** | 0 € | — | — |
| ~~Claude ispravlja prijepis sam~~ | — | — | — | — | **odbačeno** kao jedini korak: popravak bez izvora krši činjenično pravilo (PRD §4); smije samo predložiti, čovjek potvrđuje | — |

## 3. Vizualno

| ideja | što je | vrijednost | trud | trošak | pravni rizik | od naručitelja |
|---|---|---|---|---|---|---|
| **Stabilizacija i čišćenje po potrebi** | program izmjeri trešnju (`vidstabdetect`) i samo tada primijeni `vidstabtransform`, uz blagi `hqdn3d` za šum; dva prolaza | **S**: snimke s mobitela; spada u „wow" sitnice iz [KVALITETA.md](../product/KVALITETA.md) | **M** | 0 €, više procesora | nizak | — |
| **Pokret na fotografiji** | spor zum ili pomak kadra (`zoompan` ili Chromium) da Reel od fotografije ne stoji | **S**: statična fotografija od 10 s djeluje mrtvo | **M** | 0 € | nizak | PRD isključuje animacije bez izričitog zahtjeva, pitanje 5 |
| **Automatski izbor najboljeg isječka** | iz dugog videa program predloži dio: granice kadrova (PySceneDetect, BSD-3, [GitHub](https://github.com/Breakthrough/PySceneDetect)) i rečenice iz prijepisa; Claude bira raspon riječima, program reže | **V** ako naručitelj šalje duge snimke | **S** | 0 € | nizak | pitanje 7 (polazno je bez rezanja) |
| Naslovna slika | izabrani kadar s naslovom; API prima `cover_url` ili `thumb_offset` ([IG media](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)) | **S**: mreža profila izgleda uredno | **M** | 0 € | nizak | već parkirano u BACKLOG-u |
| Stock video i foto: Pexels | besplatno; API 200 upita na sat i 20.000 mjesečno, vidljiva poveznica na Pexels u aplikaciji, zasluga fotografu kad je moguće ([API](https://www.pexels.com/api/documentation/)) | **N** za nekretnine (vjerodostojnost traži stvaran materijal); **S** za Reelove s podacima i vijestima | **S** | 0 € | nizak; prepoznatljive osobe i zaštitni znakovi traže oprez | — |
| Stock: Pixabay API | 100 upita u 60 s, obavezno spremanje 24 h, zabranjeno trajno povezivanje i masovno preuzimanje ([API](https://pixabay.com/api/docs/)) | kao Pexels | **S** | 0 € | nizak | — |
| ~~Unsplash API~~ | — | — | — | — | **odbačeno**: uvjeti traže prikaz preko njihovih URL-ova i zaslugu pri svakom prikazu, što se ne slaže s upečenim MP4 ([API uvjeti](https://unsplash.com/api-terms)) | — |
| ~~Storyblocks API~~ | — | — | — | samo Enterprise, cijena po ponudi ([API](https://www.storyblocks.com/api)) | **odbačeno**: preskupo za jedan profil | — |
| ~~Uklanjanje pozadine~~ | — | **N** za nekretnine | — | — | **odbačeno**: RMBG-2.0 je CC BY-NC ([GitHub](https://github.com/Bria-AI/RMBG-2.0)); BiRefNet kod je MIT ([GitHub](https://github.com/ZhengPeng7/BiRefNet)), ali licenca težina nije potvrđena, a CPU je spor | — |
| ~~AI povećanje rezolucije~~ | — | — | — | — | **odbačeno**: na poslužitelju bez GPU-a predugo za cilj od 120 s | — |
| **Canva Connect API** | Autofill brand predložaka radi i na Canva Pro i Teams od 21. 9. 2026., autofill videa je općedostupan od 23. 9. 2026., izvoz u MP4 postoji ([changelog](https://www.canva.dev/docs/connect/changelog/), [izvoz](https://www.canva.dev/docs/connect/api-reference/exports/)) | **S** kao provjera: izvoz naručiteljeva predloška kao referenca za branu V1 | **S** | Canva plan naručitelja | nizak | OAuth pristup Canva računu |
| ~~Canva kao motor izrade~~ | — | — | — | — | **odbačeno**: PRD traži rad bez Canve; autofill ne slaže tekst po hrvatskim pravilima, a svaka izrada ovisi o tuđem servisu i redu čekanja | — |

## 4. Rast i mjerenje

Sve ovdje traži istu Meta aplikaciju kao objava ([OBJAVA.md](./OBJAVA.md)), pa ima smisla tek uz nju.

| ideja | što je | vrijednost | trud | trošak | pravni rizik | od naručitelja |
|---|---|---|---|---|---|---|
| **Insights po Reelu** | `views`, `reach`, `saved`, `shares`, `ig_reels_avg_watch_time`, `ig_reels_video_view_total_time`, `reels_skip_rate` (procjena, u razvoju); kašnjenje do 48 h, čuva se 2 godine ([media insights](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights)) | **V**: prvi put se vidi što radi | **S** | 0 € | nizak, službeni API | Meta aplikacija, dozvola `instagram_manage_insights` |
| **Koji pristup teksta radi** | `text_variants` već bilježi prijedloge ([DATA_MODEL](../architecture/DATA_MODEL.md)); spojiti izbor A, B ili C i izmjene s gledanošću | **V**: temelj za „učenje stila" uz potvrdu čovjeka (BACKLOG, parkirano) | **M** nakon Insightsa | 0 € | nizak | — |
| Trial Reels preko API-ja | `trial_params` s `MANUAL` ili `SS_PERFORMANCE`: Reel prvo vide samo oni koji ne prate profil ([IG media](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)); prelazak na pratitelje kod `MANUAL` ide ručno u aplikaciji ([Ayrshare](https://www.ayrshare.com/apis/post/social-networks/instagram), sekundarno) | **S**: pravo A/B testiranje dvaju tekstova bez štete za pratitelje | **M** uz objavu | 0 € | nizak | Meta aplikacija |
| Najbolje vrijeme objave | `online_followers` po satu, samo zadnjih 30 dana i od 100 pratitelja ([user insights](https://developers.facebook.com/docs/instagram-platform/api-reference/instagram-user/insights)) | **S** | **M** | 0 € | nizak | — |
| Praćenje konkurencije | Business Discovery: tuđi poslovni računi, `followers_count`, `media_count`, `like_count`, `comments_count`, `view_count` ([Business Discovery](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-facebook-login/business-discovery)) | **S**: tjedni pregled što kod sličnih profila radi | **M** | 0 € | nizak; scraperi su **odbačeni** ([IZVORI.md](./IZVORI.md)) | popis profila koje prati |
| Prijedlog hashtagova | Claude predloži do 5 iz teksta; bez alata za „trending" hashtagove | **N**: hashtagovi su nakon ograničenja manje važni | **M** | 0 € | nizak | — |

## 5. Nekretnine

| ideja | što je | vrijednost | trud | trošak | pravni rizik | od naručitelja |
|---|---|---|---|---|---|---|
| **Reel iz vlastitog oglasa** | urednik pošalje poveznicu na **svoj** oglas ili izvoz (XML, CSV); bot uzme fotografije, cijenu, kvadraturu i lokaciju | **V** ako naručitelj prodaje ili posreduje | **S** | 0 € | nizak za vlastiti sadržaj; tuđi portali su **odbačeni** (Njuškalo, [IZVORI.md](./IZVORI.md)) | ima li vlastite oglase i u kojem obliku; ADR-007 vrijedi za Instagram poveznice |
| Provjera obaveznih podataka oglasa | za Reel koji oglašava prodaju ili najam bot upozori ako nedostaje energetski razred | **S**: smanjuje rizik kazne | **M** | 0 € | europska direktiva traži energetski razred u oglasu; hrvatske odredbe i kazne **nisu potvrđene** ([Novi list](https://www.novilist.hr/?p=286687), sekundarno) | potvrda pravnika |
| Karta lokacije | mala karta u predlošku iz vlastitih OSM pločica (Protomaps PMTiles izvadak za Hrvatsku, ODbL uz vidljivu atribuciju, [Protomaps](https://docs.protomaps.com/basemaps/downloads)) | **S** | **S** | 0 € | nizak uz atribuciju | treba li karta uopće |
| ~~Google Maps Static~~ | — | — | — | — | **odbačeno**: promotivni video s Google kartom (izričito i primjer agencije za nekretnine) traži odobrenje Googlea ([smjernice](https://about.google/brand-resource-center/products-and-services/geo-guidelines/)) | — |
| ~~Pločice `tile.openstreetmap.org`~~ | — | — | — | — | **odbačeno**: masovno i unaprijed preuzimanje zabranjeno ([pravila](https://operations.osmfoundation.org/policies/tiles/)) | — |
| Grafikon cijena stanova | Reel s podatkom DZS-a ili HNB-a; program crta graf, Claude piše rečenicu | **S** za poslovni sadržaj | **S** | 0 € | nizak; tablica HNB-a na data.gov.hr ima Otvorenu dozvolu ([data.gov.hr](https://data.gov.hr/ckan/en/dataset/nefinancijske-statistike/resource/7b5449d3-b1f1-404a-b98e-fcf49f1ae9cc)); indeks kasni oko 100 dana | izvori su u [IZVORI.md](./IZVORI.md) |
| ~~Katastar i zemljišne knjige~~ | — | — | — | — | **odbačeno**: javni API OSS-a nije potvrđen, a ZK sadrži osobne podatke vlasnika (GDPR) | — |
| ~~Virtualne šetnje~~ | — | — | — | — | **odbačeno**: traže posebnu opremu i nisu oblik Reela | — |

## 6. Rad i pouzdanost

| ideja | što je | vrijednost | trud | trošak | pravni rizik | od naručitelja |
|---|---|---|---|---|---|---|
| **Tjedni izvještaj u Telegramu** | ponedjeljkom: broj Reelova, koliko je teksta prošlo bez izmjene (mjera iz KVALITETA), trošak API-ja, procjena uštede vremena; kasnije i gledanost | **V**: naručitelj vidi vrijednost, Leon vidi kvalitetu | **M** bez Meta, **S** s Insightsima | 0 € | nizak | — |
| Odobravanje u dva koraka | urednik pripremi, vlasnik profila odobri gumbom; `users.role` već postoji | **S** ako je urednika više | **M** | 0 € | nizak | pitanje 15 |
| Red objava | zakazivanje iz [OBJAVA.md](./OBJAVA.md); API ne nudi zakazanu objavu za Instagram (nije spomenuto u dokumentaciji), pa vrijeme drži vlastiti red u Postgresu | **S** | **S** | 0 € | nizak | — |
| Album fotografija u jedan Reel | Telegram album od više fotografija postaje jedan Reel | **S** | **V** | 0 € | nizak | pitanje 9 |

## Upozorenja

1. **Glazba nije prenosiva.** Meta Sound Collection vrijedi samo na Metinim platformama, TikTokov CML samo
   na TikToku. Za upečenu glazbu treba vlastita licenca koja pokriva obje mreže, a ni ona ne sprječava
   automatski Content ID zahtjev.
2. **AI akt, članak 50, vrijedi od 2. 8. 2026.:** označavanje deepfake sadržaja, AI zvuka i slike te AI
   teksta o pitanjima od javnog interesa ([Heuking](https://www.heuking.de/en/news-events/newsletter-articles/detail/the-european-commission-specifies-labelling-requirements-for-ai-generated-content-and-deepfakes.html),
   sekundarno). Tiče se sintetičkog glasa i načina „vijesti". Izuzeće za tekst koji je urednički pregledao
   čovjek nije provjereno u službenom tekstu.
3. **Instagram kažnjava neoriginalan sadržaj:** od travnja 2026. računi koji uglavnom ponovno objavljuju
   tuđe gube preporuke ([Tubefilter](https://tubefilter.com/2026/04/30/instagram-removes-algorithm-recommendations-repost-content-aggregator)).
   Učvršćuje pravilo iz [IZVORI.md](./IZVORI.md): tuđe je signal, Reel je vlastiti.

## TOP 5 po omjeru vrijednosti i truda

Predloženi redoslijed. Prve tri ne trebaju Meta aplikaciju ni novac.

| # | ideja | zašto prva |
|---|---|---|
| 1 | **Tjedni izvještaj u Telegramu** | Podaci su već u bazi, trud mali, a naručitelj svaki tjedan vidi što dobiva. Kasnije samo dobiva stupac gledanosti. |
| 2 | **Stabilizacija i čišćenje po potrebi** | Samo FFmpeg, nula troška, vidljivo bolji video s mobitela. Prije koda provjeriti ima li pinani FFmpeg `libvidstab`. |
| 3 | **Titlovi s potvrdom prijepisa** | Najveći dobitak gledanosti, ali srednji trud i ovisi o izgledu titla u predlošku. Potvrda u Telegramu je dio iste cigle, ne dodatak. |
| 4 | **Insights i učenje koji pristup teksta radi** | Tek uz Meta aplikaciju za objavu, ali tada je skoro besplatno: pretvara „vrhunski" iz osjećaja u brojku. Uključuje Trial Reels. |
| 5 | **Automatski izbor najboljeg isječka** | Velika ušteda vremena za duge snimke; čeka odgovor na pitanje 7 i stvarne materijale. |

Odmah i bez koda: uputa uredniku o glazbi iz aplikacije i opis s najviše 5 hashtagova (prvi odjeljak).

## Otvoreno

1. Prodaje li ili posreduje naručitelj nekretnine i ima li vlastite oglase u izvozivom obliku?
2. Koliko snimki ima govor, i žele li titlove? Kakav izgled (pitanje 5)?
3. Šalju li duge snimke iz kojih treba izrezati najbolji dio (pitanje 7)?
4. Dodaju li danas glazbu u Canvi ili u aplikaciji, i plaćaju li neku glazbenu pretplatu?
5. Ima li profil više od 100 pratitelja i poslovni račun povezan s Facebook stranicom (Insights)?
6. Koje profile konkurencije žele pratiti?
7. Žele li ikad sintetički glas? Ako da, presuda na sluh za ElevenLabs i Google Chirp 3 HD prije odluke.
8. Tko potvrđuje pravna pitanja: energetski razred u oglasu i članak 50 AI akta?
