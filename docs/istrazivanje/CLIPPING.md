> **Snimka iz BOORA repozitorija, 4. 11. 2026.** Poveznice `../records/…` i `../architecture/…` vode u
> `C:\Users\leonk\Documents\Bot za BOORA.ai\docs\`, ne u ovaj repozitorij.

# Ideja: clipping i automatska objava (Leonov vlastiti posao)

Može li isti stack (FFmpeg, faster-whisper, Claude, Chromium, Postgres, Telegram) iz dugih videa sam
rezati najbolje kratke isječke, objavljivati ih na TikTok, Instagram, Facebook i YouTube i od toga
zarađivati. Primjer: GTA 6 sadržaj na veliko. Provjereno 2026-11-04, osim gdje piše drukčije.

> Nije plan i nije obećanje. Objava ostaje na naredbu čovjeka ([ADR-002](../records/DECISIONS.md)).
> **Ovo nije narudžba naručitelja**, nego Leonov vlastiti posao: ne ulazi u pilot ni u cigle C0 do C8.
> Ovo nije pravni ni porezni savjet. **Sekundarno** znači članak ili agregator, ne službeni izvor;
> „nije potvrđeno" znači da službeni izvor nije pročitan ili nije odgovorio.

Ne ponavlja [ZARADA.md](./ZARADA.md) (modeli zarade za cijeli sustav), [OBJAVA.md](./OBJAVA.md) (Meta
objava za naručitelja) ni [IZVORI.md](./IZVORI.md) (trendovi i uvjeti preuzimanja s mreža).

## Odvajanje od narudžbe

| što | preporuka | zašto |
|---|---|---|
| repozitorij | zaseban privatni repozitorij; zajednički dijelovi tek kad je s naručiteljem dogovoreno čiji je kod | miješanje stvara spor o vlasništvu i curenje naručiteljevih podataka |
| računi platformi | vlastiti Google Cloud projekt, Meta aplikacija i TikTok klijent, nikad naručiteljevi | kazna za spam ili autorska prava na jednom računu ne smije pogoditi naručitelja |
| API ključevi i troškovi | zaseban Anthropic radni prostor i ključ, zaseban račun za poslužitelj | trošak se mora moći pripisati poslu koji ga je napravio |
| podaci i mediji | zasebna baza i disk; ništa naručiteljevo u clipping cjevovodu | [SECURITY.md](../architecture/SECURITY.md) uređuje privatnost i zadržavanje naručiteljevih podataka; tuđi posao nije njihova svrha |
| prihod | obrt ili tvrtka i poslovni račun prije prve isplate | vidi odjeljak 6 |

## 1. Autorska prava i GTA 6

Rockstarova stranica politike nije odgovorila 4. 11. (istek veze); sažetak je iz pretrage
([Rockstar Support](https://support.rockstargames.com/articles/200153756/Policy-on-posting-copyrighted-Rockstar-Games-material),
datirana 10. 1. 2025. prema sažetku).

| vrsta sadržaja | Rockstar / Take-Two | platforma | izvor |
|---|---|---|---|
| vlastiti gameplay, Let's Play s naracijom | tolerira **nekomercijalnu** uporabu; „nekomercijalno" znači da ne zarađuješ od snimke. Popis od šest razloga za uklanjanje ne spominje monetizaciju i hvali Let's Play s naracijom: **siva zona**, ne dopuštenje | dopušteno; YouTube je u rujnu 2026. ublažio pravila o nasilju u igrama za oglase | Rockstar (sažetak); [Prepublish](https://prepublish.ai/blog/gta-6-youtube-copyright-monetization), [Dexerto](https://www.dexerto.com/gta/youtube-updates-gaming-violence-monetization-rules-ahead-of-gta-6-launch-3405945/), sekundarno |
| procurene snimke prije izlaska | uklanja se bez obzira kako je igra nabavljena, i „early unboxing" | Content ID, uklanjanje, suspenzija | Rockstar (sažetak) |
| izolirane cutscene, kraj igre, velika otkrića, TV emisije iz igre | označava se za uklanjanje | — | Rockstar (sažetak) |
| ponovna objava cijelog trailera | Take-Two je prijavio i reakciju koja je sadržavala cijeli trailer | Content ID; „reused content" | [SVG](https://svg.com/1463343/gta-6-trailer-takedown-controversy), sekundarno |
| tuđi stream ili video | dvostruka prava: streamer i Rockstar | YouTube: dopuštenje autora **ne izuzima** od pravila o ponovno korištenom sadržaju | [YouTube](https://support.google.com/youtube/answer/1311392) |
| AI „lažni" GTA 6 sadržaj | Take-Two cilja lažne AI leakove; AI fan videi nestaju s YouTubea | obmanjujući sadržaj | [Notebookcheck](https://www.notebookcheck.net/GTA-6-trailer-3-release-anticipated-as-Take-Two-targets-fake-AI-generated-leaks.1351256.0.html), sekundarno |

**Činjenice o igri.** Izlazak 19. 11. 2026. za PS5 i Xbox Series X|S, PC kasnije
([GamesRadar](https://www.gamesradar.com/games/grand-theft-auto/gta-6-delayed-6-more-months-as-rockstar-commits-to-november-2026-and-says-sorry), sekundarno; datum je
poslije svibnja 2026. ponovljen, novija potvrda nije nađena). Nema ranog pristupa ni pregleda za kreatore
([Malwarebytes](https://www.malwarebytes.com/blog/news/2026/06/gta-6-early-access-is-nothing-but-a-scam), sekundarno).

**DMCA slučaj, kolovoz 2026.** Nakon curenja gameplaya 18. 8. Take-Two je slao masovne zahtjeve za
uklanjanje i tražio DMCA sudske naloge prema Discordu, Microsoftu, X-u i YouTubeu za identitet onih koji
su objavili snimke; imenovani X računi su suspendirani, a YouTube upload je preuzeo Content ID
([TorrentFreak, 23. 8. 2026.](https://torrentfreak.com/take-two-expands-gta-6-leak-hunt-with-dmca-subpoenas/)).
Pouka: kod GTA 6 Take-Two ne staje na uklanjanju, nego traži stvarne osobe.

**Razlika u tri reda.** Vlastiti gameplay je tvoja snimka tuđeg djela (tolerirano, monetizacija siva).
Komentar ili transformativni sadržaj (recenzija, vodič, analiza s vlastitim glasom) je najjači oblik i za
Rockstar i za platforme. Ponovna objava tuđeg (trailer, stream, tuđi clip) je u pravilu povreda, a i kad
nije, platforme je ne plaćaju.

## 2. Monetizacija po platformi

| platforma | program i uvjeti | Hrvatska | pravilo originalnosti | izvor |
|---|---|---|---|---|
| YouTube | YPP: 1.000 pretplatnika i 4.000 sati u 12 mj. **ili** 10 mil. Shorts pregleda u 90 dana; niža razina (500 pretplatnika, 3 uploada u 90 dana, 3.000 sati ili 3 mil. Shorts pregleda) daje samo članstva, Super Thanks i Shopping, ne oglase | YPP dostupan (sažetak pretrage) | Shorts: kreatori dijele bazen, kreator zadržava 45 %; ne broje se neoriginalni Shorts, kompilacije bez dodanog sadržaja i ponovni uploadi | [YPP](https://support.google.com/youtube/answer/72851), [niža razina](https://support.google.com/youtube/answer/13429240), [dostupnost](https://support.google.com/youtube/answer/7101720), [Shorts](https://support.google.com/youtube/answer/12504220) |
| YouTube | „Inauthentic content" (preimenovano 15. 7. 2025.): predložak, masovna proizvodnja, AI iz generičnih predložaka; „reused content" vrijedi za **cijeli kanal** | — | spam pravilo: „automatizirani alati ili AI za izbacivanje velikih količina sličnog sadržaja" vodi do gubitka monetizacije ili gašenja kanala; tri opomene u 90 dana gase kanal | [reused/inauthentic](https://support.google.com/youtube/answer/1311392), [spam](https://support.google.com/youtube/answer/2801973) |
| TikTok | Creator Rewards: 18+, 10.000 pratitelja, 100.000 pregleda u 30 dana, video 60 s ili duži | **vjerojatno nije dostupno**: popisi navode 7 do 8 zemalja, Hrvatske nema; službena stranica se nije prikazala | originalan sadržaj (sekundarno) | [ttcalculator](https://ttcalculator.net/learn/creator-fund-countries/), [ShortSync](https://www.shortsync.app/resources/tiktok-creator-rewards-program-2026), sekundarno |
| Instagram | bonusi i Reels monetizacija | nije potvrđeno | od 30. 4. 2026. računi koji uglavnom ponovno objavljuju gube preporuke (Reels i sada fotografije); izuzeće je stvarna prerada: „vlastiti tekst, kreativna obrada i glas"; ubrzanje i ime autora nisu dovoljni | [Tubefilter](https://www.tubefilter.com/2026/04/30/instagram-removes-algorithm-recommendations-repost-content-aggregator) |
| Facebook | Content Monetization (beta od listopada 2024.): spaja in-stream oglase, oglase na Reelovima i bonus, **samo na poziv**; zemlja prebivališta i financijski subjekt moraju biti u dopuštenoj zemlji | nije potvrđeno; službenog popisa nema | od 14. 7. 2025. računi koji ponavljaju tuđe bez prerade privremeno gube monetizaciju i doseg; u prvoj polovici 2025. akcija protiv oko 500.000 računa za spam | [Meta](https://about.fb.com/news/2024/10/monetize-content-facebooks-new-streamlined-program/), [pravila](https://www.facebook.com/business/help/169845596919485), [Tubefilter](https://www.tubefilter.com/2025/07/15/ai-slop-unoriginal-repetitive-content-monetization-facebook-meta/), [Gigazine](https://gigazine.net/gsc_news/en/20250715-meta-combating-unoriginal-facebook-content), sekundarno |

**Koliko plaća.** Shorts oko 0,01 do 0,15 $ na 1.000 pregleda, ovisno o niši i zemlji gledatelja
([ShortSync](https://www.shortsync.app/resources/how-much-do-youtube-shorts-pay-2026), sekundarno). Milijun
pregleda mjesečno je dakle 10 do 150 $.

**Što se događa s masovnim računima neoriginalnog sadržaja:** YouTube skida monetizaciju s cijelog kanala
i gasi mreže kanala; Facebook skida monetizaciju i doseg; Instagram skida preporuke, pa račun vide samo
postojeći pratitelji; TikTok ograničava broj objava kroz API (odjeljak 5). Zajedničko: kazna pada na
**račun**, ne na video, pa jedan loš tjedan briše mjesece rada.

## 3. Zakoniti modeli zarade

| model | tko plaća | prava | realno | glavni rizik | izvor |
|---|---|---|---|---|---|
| **Plaćene clipping kampanje** (Whop Content Rewards i slično) | vlasnik kampanje, po 1.000 provjerenih pregleda, iz ograničenog budžeta; vlasnik odobrava isječke | vlasnik daje sadržaj i dopuštenje u briefu | medijan oko 1 $ na 1.000 pregleda ([ZARADA.md](./ZARADA.md)); 100.000 pregleda je oko 100 $ | budžet se troši po redu dolaska; kampanja koja traži uplatu za ulaz je prijevara; isti isječak na YouTubeu ne prolazi YPP („promoviranje tuđeg, i uz dopuštenje") | [Opus o Whopu](https://www.opus.pro/blog/whop-content-rewards), [ClipAffiliates](https://www.clipaffiliates.com/blog/is-whop-content-rewards-legit), sekundarno, prodavatelji alata |
| **Clipping kao usluga** za jednog kreatora ili podcast | kreator, mjesečno | ugovor, kreator daje izvorne datoteke | vidi model A u [ZARADA.md](./ZARADA.md) | Leonovo vrijeme | — |
| **Vlastiti GTA 6 kanal s vlastitim gameplayem i glasom** | platforma iz oglasa (YouTube), kasnije sponzori | tolerirano (odjeljak 1), monetizacija siva | do YPP-a nula; poslije 0,01 do 0,15 $ na 1.000 Shorts pregleda | konkurencija: GTA 6 će biti najpokrivenija igra (procjena); spoileri u prvim tjednima | odjeljci 1 i 2 |
| **Vodiči i vijesti uz vlastitu snimku i izvore** | isto | najčišće | isto | trud: traži stvaran rad u igri | — |
| Afilijacije (oprema, igra) | trgovac | vlastiti sadržaj | nije provjereno | — | — |
| Licencirani sadržaj | — | ugovor s nositeljem prava | nije provjereno | cijena licence | — |

## 4. Tehnički clipping

| tehnika | čemu služi | imamo li | izvor |
|---|---|---|---|
| prijepis s vremenom po riječi | granice rečenica, titlovi, ulaz za ocjenu | **da**, `faster-whisper`; hrvatski WER oko 34 %, engleski znatno bolji ([BACKLOG](../records/BACKLOG.md)) | — |
| ocjena isječka iz teksta | Claude dobije numerirane rečenice i vrati raspone i razlog (udica, zaokruženost); program reže | **da**, isti obrazac kao tri teksta (ADR-005: Claude bira riječima, ne piksele) | — |
| granice kadrova | rez ne pada usred kadra | ne; PySceneDetect, BSD-3 | [GitHub](https://github.com/Breakthrough/PySceneDetect) |
| glasnoća i vrhunci zvuka | eksplozije, vika, smijeh kao signal | djelomično: FFmpeg `ebur128` ili `astats`; prepoznavanje smijeha zasebnim modelom nije provjereno | — |
| reframe 16:9 u 9:16 | kadar prati lice ili radnju | ne; Googleov AutoFlip (2020., na MediaPipeu, lice i objekti, mutna pozadina kao pad); `pyautoflip` i `auto-vertical-reframe` koriste PySceneDetect i MediaPipe, licence i održavanje nisu provjereni | [Google Research](https://research.google/blog/autoflip-an-open-source-framework-for-intelligent-video-reframing/), [pyautoflip](https://pypi.org/project/pyautoflip/), [GitHub](https://github.com/KazKozDev/auto-vertical-reframe) |
| raspored za gameplay | gameplay nema lice; središnji izrez gubi mapu i HUD; bolje je 16:9 u sredini s mutnom pozadinom ili facecam gore, igra dolje | **da**, to je predložak u Chromium sloju, ne AI | — |
| titlovi | gledanje bez zvuka | ne; TOP 5, br. 3 u [PRILIKE.md](./PRILIKE.md) | — |

**SaaS kao mjerilo za „gradi ili kupi":**

| alat | cijena | API | izvor |
|---|---|---|---|
| OpusClip | Free; Starter 15 $/mj; Pro 29 $/mj; Business po ponudi; minute po planu stranica ne navodi | Pro i Business: Video Editing API, Scheduler API, MCP; prema sekundarnom izvoru do 15 sati videa mjesečno kroz API i najmanje 10 kredita po projektu | [cjenik](https://www.opus.pro/pricing), [diyai](https://diyai.io/ai-tools/code-generation/opus-clip-pricing/), sekundarno |
| Vizard | 1 kredit = 1 minuta videa; Creator oko 29 $ za 600 kredita (sekundarno) | uključen u sve plaćene planove; 3 upita u minuti na Creatoru, 10 na Businessu | [dokumentacija](https://docs.vizard.ai/docs/pricing), [MakerStack](https://makerstack.co/reviews/vizard-review/) |
| Klap | Pro oko 39 $/mj (izvor prodavatelja) | naplata po operaciji, iznosi se nisu prikazali | [dokumentacija](https://docs.klap.app/pricing) |

**Gradi ili kupi:** gradi jezgru, kupi mjerilo. Prijepis, ocjena tekstom, izrada, titlovi, opis i
Telegram tok već postoje; nov je samo reframe i rezanje na kandidate. Kupljeni API daje strani raspored i
titlove koje ne kontroliramo, plus trošak po minuti. Jedan mjesec OpusClip Pro (29 $) vrijedi kao
**zlatna usporedba**: isti dugi video kroz oba, presuda na oko, prije nego što se gradi reframe.

## 5. Automatska objava

| platforma | API i kvota | ograničenja | zakazivanje | izvor |
|---|---|---|---|---|
| YouTube | `videos.insert`: 100 poziva dnevno u zasebnoj kvoti za upload; ostalo 10.000 jedinica dnevno; više tek uz audit | dokumentacija od 4. 11. kaže da uploadi neprovjerenih projekata **nisu** zaključani na privatno (ranije pravilo je bilo suprotno; potvrditi prvim uploadom); polje `containsSyntheticMedia` za AI oznaku | `status.publishAt` | [kvote](https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits), [videos.insert](https://developers.google.com/youtube/v3/docs/videos/insert) |
| TikTok | Content Posting API, Direct Post ili upload | neauditiran klijent: najviše 5 korisnika u 24 h, samo `SELF_ONLY`, račun mora biti privatan; oko 15 objava dnevno po računu, **zajedničko za sve aplikacije**; obavezan pregled prije slanja, ručni izbor privatnosti bez zadane vrijednosti, izričit pristanak. **Audit izričito odbija** „alat za upload na račune koje ti ili tvoj tim vodite" i „kopiranje sadržaja s drugih platformi" | API ga ne nudi (nije spomenuto) | [početak](https://developers.tiktok.com/doc/content-posting-api-get-started), [smjernice](https://developers.tiktok.com/doc/content-sharing-guidelines), [Direct Post](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post) |
| Instagram | 100 objava kroz API u 24 h (u istom dokumentu piše i 50, nedosljedno); provjera kroz `content_publishing_limit` | profesionalni račun; stranica s Page Publishing Authorization ne može objavljivati dok je ne dovrši; spremnik istječe za 24 h | parametra nema, vlastiti red | [Content Publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing) |
| Facebook | Reels API: 30 objava u 24 h | samo stranice, ne profili; 3 do 90 s; preporučeno 1080 × 1920 | `scheduled_publish_time`, od 10 min do 29 dana unaprijed | [Reels Publishing](https://developers.facebook.com/docs/video-api/guides/reels-publishing) |

**Posljedica za TikTok:** Leonov osobni alat vjerojatno ne prolazi audit, pa ostaje privatna objava.
Realno: bot pošalje gotov MP4 i opis u Telegram, Leon objavi s mobitela; ili plaćeni alat za zakazivanje
s vlastitim auditiranim klijentom (cijene nisu provjerene).

**Više računa i spam:** YouTube kažnjava „koordinirane mreže kanala" i poplavu sličnog sadržaja; TikTokov
dnevni limit dijele sve aplikacije. Preporuka: jedan račun po platformi i niši, 1 do 3 objave dnevno,
svaka uz ljudski pregled.

## 6. Pravni okvir EU i HR

| tema | što znamo | izvor |
|---|---|---|
| AI akt, čl. 50 (od 2. 8. 2026.) | onaj tko objavljuje (deployer) mora označiti deepfake sadržaj; za umjetnički, satirični ili fikcijski oblik oznaka je blaža, ali ostaje; kazne do 15 mil. € ili 3 % prometa. Za clipping: sintetički glas i AI slika trebaju oznaku (YouTube `containsSyntheticMedia`); Claude koji piše opis nije deepfake. Izuzeće za tekst s urednikom vidi [PRILIKE.md](./PRILIKE.md) | [McCann FitzGerald](https://www.mccannfitzgerald.com/knowledge/data-privacy-and-cyber-risk/ai-transparency-european-commissions-guidelines-on-article-50-part-2-deployer-obligations), [GDPR Local](https://gdprlocal.com/eu-ai-act-article-50/), sekundarno |
| DSA | obveze su na platformama, ne na Leonu; korisna prava: obrazloženje uklanjanja (čl. 17) i interna žalba (čl. 20) | [Uredba 2022/2065](https://eur-lex.europa.eu/eli/reg/2022/2065/oj), nije dohvaćena 4. 11. |
| porez | prihodi s YouTubea, TikToka, sponzorstava i afilijacija tretiraju se kao poslovni; uobičajeno obrt ili tvrtka, paušalni obrt je najjednostavniji. Na prihod od američkih gledatelja YouTube je od 2021. mogao zadržati do 30 % jer HR i SAD tada nisu imale ugovor o dvostrukom oporezivanju; današnji status nije potvrđen | [Fiskai](https://www.fiskai.hr/vodic/youtuber-influencer/), [tportal, 2021.](https://www.tportal.hr/biznis/clanak/hladan-tus-za-domace-youtubere-od-danas-moraju-placati-novi-porez-na-zaradu-ostvarenu-u-sad-u-donosimo-detalje-foto-20210601), sekundarno |

**Prije prve isplate: računovođa.** Isplate iz inozemstva (Whop, Google, Meta) i PDV na usluge iz
inozemstva ovdje nisu provjereni.

## Ulaz preko linka

Želja: Leon pošalje poveznicu (YouTube, TikTok, Instagram, Twitch, X), sustav sam preuzme video i izreže
isječke. Danas bot prima samo datoteke ([ADR-007](../records/DECISIONS.md)), a `worker-media` nema internet
([ARCHITECTURE.md](../architecture/ARCHITECTURE.md), [SECURITY.md](../architecture/SECURITY.md)).

### a) Tehnika

| što | stanje | izvor |
|---|---|---|
| `yt-dlp` | Unlicense; gotovi izvršni paketi uključuju GPLv3+ kod | [README](https://github.com/yt-dlp/yt-dlp) |
| YouTube | puna podrška traži `yt-dlp-ejs` i JavaScript runtime (Deno, Node, Bun, QuickJS); YouTube postupno traži „PO token" koji yt-dlp ne zna sam napraviti; ograničenje oko 300 videa na sat bez prijave, oko 2.000 s prijavom; preporuka 5 do 10 s pauze | [README](https://github.com/yt-dlp/yt-dlp), [wiki](https://github.com/yt-dlp/yt-dlp/wiki/Extractors) |
| kolačići i prijava | trebaju samo za privatno, dobno ograničeno i članski sadržaj; **račun može biti blokiran** privremeno ili trajno | [wiki](https://github.com/yt-dlp/yt-dlp/wiki/Extractors) |
| održavanje | stabilna verzija otprilike mjesečno, a za obične korisnike se preporučuje nightly; TLS impersonacija (`curl_cffi`) za neke stranice | [README](https://github.com/yt-dlp/yt-dlp) |

Posljedica: preuzimanje s mreža je **lomljivo po prirodi**. Svaka promjena na platformi lomi ga, popravak
dolazi kao nova verzija, a ADR-014 traži da je svaka nadogradnja namjerna radnja uz pun gate. To je
stalan trošak održavanja, ne jednokratna cigla. Blokade IP adresa podatkovnih centara su česte u praksi,
ali nisu potvrđene u dokumentaciji.

### b) Što kažu uvjeti

| platforma | preuzimanje | automatizirani pristup | izvor |
|---|---|---|---|
| YouTube | zabranjeno osim kako usluga izričito dopušta, uz pisano dopuštenje **YouTubea** i nositelja prava, ili prema propisima | zabranjen (roboti, scraperi), osim tražilica i uz pisano dopuštenje | [Uvjeti, 5. 1. 2022.](https://www.youtube.com/t/terms) |
| TikTok (EEA) | licenca za preuzimanje samo „u svrhu zabave", prema postavkama platforme, i samo za tebe (t. 4.4, 4.9) | t. 4.5: zabranjeno izvlačenje sadržaja alatom koji TikTok nije dao ili pisano odobrio | [Uvjeti, srpanj 2026.](https://www.tiktok.com/legal/page/eea/terms-of-service/en) |
| Meta (Facebook, Instagram) | dijeljenje tuđeg što krši intelektualno vlasništvo zabranjeno | t. 3.2: zabranjeno automatizirano prikupljanje bez prethodnog dopuštenja | [Uvjeti, 1. 1. 2025.](https://www.facebook.com/terms.php) |
| X | umnožavanje i prerada samo kroz X-ova sučelja | crawling i scraping zabranjeni bez pisanog pristanka; ugovorna kazna 15.000 € na milijun objava iznad milijuna u 24 h | [Uvjeti, 9. 10. 2026.](https://x.com/en/tos) |
| Twitch | nije potvrđeno (stranica se nije prikazala) | nije potvrđeno | [Uvjeti](https://legal.twitch.com/en/legal/terms-of-service/) |

**Kad je preuzimanje u redu:** (1) vlastiti sadržaj, najbolje kao izvorna datoteka (YouTube Studio ili
izvoz platforme), ne preko yt-dlp-a; (2) izričito pisano dopuštenje vlasnika **uz izvornu datoteku**;
(3) licenca; (4) clipping kampanja koja daje izvorne datoteke ili u briefu dopušta preuzimanje.
Važno: ni dopuštenje vlasnika ne mijenja YouTubeov uvjet da i **YouTube** mora dopustiti preuzimanje.
Dopuštenje vlasnika rješava autorsko pravo, ne uvjete platforme.

### c) Sigurnost

Link je opasniji ulaz od datoteke: sustav sam odlazi na mrežu.

| prijetnja | obrana |
|---|---|
| SSRF: poveznica ili preusmjeravanje na `postgres`, unutarnju mrežu ili `169.254.169.254` | zaseban radnik u vlastitoj mreži bez pristupa bazi i servisima; DNS se razriješi i provjeri prije spajanja i nakon svakog preusmjeravanja; samo `https` |
| veličina, trajanje, beskonačni live | najveća veličina i trajanje prije preuzimanja (`--max-filesize`, filtar trajanja), odbij live i playlistu (`--no-playlist`), vremensko ograničenje posla |
| nepoznat format, zlonamjeran medij | preuzeta datoteka ide istim putem kao Telegram datoteka: `worker-media` bez interneta, ista provjera i normalizacija |
| ubacivanje argumenata | URL kao zaseban argument iza `--`, bez ljuske; `--ignore-config`; samo dopušteni extractori |
| JavaScript runtime u yt-dlp-u | izvršava tuđi kod: radnik bez tajni, samo za čitanje, s ograničenim CPU-om i memorijom |
| kolačići | tajna kao i API ključ; najbolje ih uopće nemati |

### d) Preporuka

1. **Prvo bez yt-dlp-a.** Dopušteni izvori: Telegram datoteka (kao danas) i izravna HTTPS poveznica na
   datoteku iz pohrane (Google Drive, Dropbox) koju daju kampanja ili vlasnik. Obično HTTPS preuzimanje
   uz SSRF zaštitu, bez extractora koji se lome.
2. **Bot pita čiji je video** prije rada, gumbima: `Moj` · `Imam pisano dopuštenje` · `Kampanja` ·
   `Ništa od toga`. Zadnji odbija. Odgovor, dokaz (poveznica na brief ili dopuštenje) i izvor se
   spremaju u bazu uz posao; bez zapisa nema objave.
3. **yt-dlp tek kasnije i usko:** popis dopuštenih kanala (vlastiti i oni s pisanim dopuštenjem), bez
   kolačića, s pauzama, zasebna nadogradnja uz gate. Uz otvoreno pitanje YouTubeovih uvjeta.
4. **U toku bota:** link je samo novi put do iste ulazne datoteke. Sve iza toga (provjera, prijepis,
   kandidati, odabir u Telegramu, izrada, odobrenje) ostaje isto.

## Procjena rizika GTA 6 ideje

| aktivnost | zakonito? | ubija račun? | ocjena |
|---|---|---|---|
| procurene snimke, leakovi | ne | da: uklanjanje, suspenzija, sudski nalog za identitet | **crveno** |
| ponovna objava trailera, cutscena, kraja igre | ne (Rockstar uklanja) | da, kroz Content ID i opomene | **crveno** |
| isječci tuđih GTA streamova bez dopuštenja | ne | da | **crveno** |
| AI „GTA 6" sadržaj koji glumi stvarno | obmana; Take-Two ga cilja | da | **crveno** |
| masovna objava predloška (isti format, AI glas, tuđe snimke) | ovisi o snimci | da: inauthentic i spam pravila | **crveno** |
| isječci streamera u plaćenoj kampanji | da, prema streameru; Rockstar tolerira gameplay | ne, ako je isječak stvarno obrađen; zaradu daje kampanja, ne YPP | **žuto** |
| vlastiti gameplay bez komentara, automatski izrezan | tolerirano, monetizacija siva | moguće, ako izgleda masovno | **žuto** |
| spoileri priče u prvim tjednima | Rockstar uklanja izolirane i velike otkrića | opomene | **žuto** |
| vlastiti gameplay s vlastitim glasom, vodiči, analiza | tolerirano, najčišći oblik | ne, uz umjeren ritam | **zeleno** |

**Zaključak:** GTA 6 „na veliko" iz tuđih snimki ubija račune i može dovesti do pravnog progona.
GTA 6 iz vlastitog gameplaya s vlastitim glasom je zakonit, ali zarada iz oglasa ostaje siva zona.
Ubija **masovnost bez čovjeka**, ne tema.

## Preporučeni model

1. **Prvo plaćene clipping kampanje** s izvornim datotekama i dopuštenjem u briefu. Zašto: plaća se
   po pregledu bez vlastite publike i YPP-a, prava su riješena briefom, ne čeka se 19. 11., a cjevovod
   se dokazuje na stvarnom novcu. Isječci moraju biti stvarno obrađeni (titl, udica, rez), inače
   Instagram skida preporuke. Zarada je skromna (oko 1 $ na 1.000 pregleda) i to je u redu: cilj je
   dokaz.
2. **Uz to, od 19. 11. vlastiti GTA 6 kanal:** Leon igra i govori, sustav samo reže, prilagođava 9:16,
   titla i predlaže opis. 1 do 3 objave dnevno, svaka uz pregled. Jezik po izboru (otvoreno pitanje).
3. **Ne:** ponovna objava tuđeg, leakovi, mreže računa, autopilot.

## Grubi tehnički nacrt

```text
Telegram datoteka ─┐                                    ┌─► Telegram: izbor isječaka (gumbi)
HTTPS poveznica ───┼─► worker-fetch ─► worker-media ────┤
(dopušteni izvor)  │   (internet,      (bez interneta:  └─► izrada ─► odobrenje ─► worker-publish
zapis prava ───────┘    bez baze)       provjera, prijepis,                         (internet, red
                                        scene, glasnoća,                             u Postgresu,
                                        kandidati)  ◄── worker-ai: ocjena riječima   limiti po platformi)
```

| korak | što | ponovno koristimo | novo |
|---|---|---|---|
| 1. ulaz | datoteka ili poveznica s dopuštenog izvora, uz zapis prava | Telegram ulaz i spremanje | `worker-fetch`, tablica prava |
| 2. provjera medija | ffprobe, normalizacija, ograničenja | `worker-media` | ograničenja za duge videe (sati, ne sekunde) |
| 3. prijepis | riječi s vremenom | `faster-whisper` | duge datoteke u dijelovima |
| 4. signali | granice kadrova, glasnoća | FFmpeg | PySceneDetect |
| 5. kandidati | program reže na rečenice i kadrove, 20 do 90 s (TikTok nagrade traže 60 s ili više) | — | rezač kandidata |
| 6. ocjena | Claude čita numerirane kandidate i vraća ID-eve i razlog | `worker-ai`, provjere izlaza | upute za ocjenu |
| 7. reframe | lice ili predložak za gameplay | Chromium sloj za raspored | MediaPipe praćenje i glađenje putanje |
| 8. titlovi, naslov, opis | — | Chromium sloj, opis iz `worker-ai` | titlovi ([PRILIKE.md](./PRILIKE.md)) |
| 9. izrada i provjera | MP4 1080 × 1920 | cijeli render | — |
| 10. odobrenje | čovjek bira isječke i potvrđuje objavu | Telegram gumbi | više isječaka po poslu |
| 11. objava | red i zakazivanje po platformi | zamišljeni radnik za objavu ([ARCHITECTURE.md](../architecture/ARCHITECTURE.md)) | YouTube, Facebook i Instagram API; TikTok ručno |
| 12. mjerenje | pregledi za kampanje i učenje | — | povratak brojki ([PRILIKE.md](./PRILIKE.md) §4) |

## Otvoreno

1. Igraš li GTA 6 sam i želiš li govoriti na snimci? Na kojem jeziku (engleski globalno ili hrvatski)?
2. Prihvaćaš li Whop ili sličnu platformu (provjera identiteta, isplata iz inozemstva)?
3. Smije li clipping koristiti kod pilota, ili treba dogovor s naručiteljem o vlasništvu koda?
4. Imaš li obrt i računovođu prije prve isplate?
5. Koliko vremena dnevno imaš za pregled isječaka?
6. Prihvaćaš li ručnu objavu na TikToku, jer audit za osobni alat vjerojatno ne prolazi?
7. Koje izvore poveznica stvarno trebaš: svoje kanale, kampanje ili nešto treće?
8. Isti poslužitelj kao pilot ili zaseban?
9. Može li jedan mjesec OpusClip Pro (29 $) kao zlatna usporedba?
