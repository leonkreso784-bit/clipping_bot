> **Snimka iz BOORA repozitorija, 4. 11. 2026.** Poveznice `../records/…` i `../architecture/…` vode u
> `C:\Users\leonk\Documents\Bot za BOORA.ai\docs\`, ne u ovaj repozitorij.

# Ideja: izvori za trendove i vijesti

Popis izvora za dvije buduće funkcije: **T** prepoznavanje trendova i **V** automatske vijesti.
Provjereno 2026-11-04, osim gdje piše drukčije.

> Nije plan i nije obećanje. Obje funkcije čekaju vlastiti plan ([BACKLOG](../records/BACKLOG.md),
> „Sljedeće faze"). Objava ostaje na naredbu čovjeka ([ADR-002](../records/DECISIONS.md)).
> Ovo nije pravni savjet. Stupac „preuzimanje" kaže što piše u uvjetima, a ne što je zakonito u svakom slučaju.

**Pravilo za cijeli popis:** sadržaj drugih (videi, objave, članci, fotografije, glazba) služi kao **signal**,
a bot radi **vlastiti** Reel i vlastiti tekst. Preuzimanje i ponovna objava traže licencu ili pisano dopuštenje.

## Društvene mreže

| izvor | za | pristup | cijena i ograničenja | preuzimanje | svježina | napomena |
|---|---|---|---|---|---|---|
| [X API](https://docs.x.com/x-api/getting-started/pricing) | T, V | službeni API v2, kredit unaprijed | čitanje objave 0,005 $, korisnika 0,010 $, objava 0,015 $; do 3 mil. čitanja mjesečno, iznad toga Enterprise; besplatne razine za nove nema (Basic i Pro zatvoreni, prema sekundarnim izvorima) | samo signal | trenutno | [trendovi po WOEID](https://docs.x.com/x-api/trends/introduction): Hrvatska nije na popisu, podrška nije potvrđena |
| [TikTok Research API](https://developers.tiktok.com/docs/en/research-api-faq) | T | prijava za istraživački projekt | besplatno, ali samo neprofitni i akademski istraživači; kreatori, oglašivači i komercijalni korisnici nisu prihvatljivi | ne | — | **nedostupno** naručitelju |
| [TikTok Content Posting API](https://developers.tiktok.com/doc/content-posting-api-get-started) | — | službeni API | neauditiran klijent objavljuje samo privatno; audit uvjeta je obavezan | — | — | za objavu, nije izvor; vidi [OBJAVA.md](./OBJAVA.md) |
| [TikTok uvjeti (EEA)](https://www.tiktok.com/legal/page/eea/terms-of-service/en) | — | — | t. 4.5 zabranjuje izvlačenje podataka automatskim alatom koji TikTok nije dao ili pisano odobrio | ne | — | vrijedi za svaki scraper TikToka |
| [Instagram hashtag search](https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-facebook-login/hashtag-search) | T | Graph API, poslovni ili kreatorski račun | besplatno; 30 različitih hashtagova u 7 dana po računu; traži App Review i Instagram Public Content Access; bez Storiesa | samo signal | top i nedavne objave | službenog API-ja za trendove ili zvukove u trendu nema (nije potvrđeno u Metinoj dokumentaciji) |
| Instagram Professional Dashboard | T | samo ručno, u aplikaciji | besplatno | ne | zvukovi u trendu | dostupnost po zemljama nije potvrđena (vodiči navode SAD) |
| [Meta Content Library](https://transparency.meta.com/en-gb/researchtools/meta-content-library/) | T | prijava preko ICPSR-a | samo kvalificirane akademske i istraživačke institucije | ne | — | **nedostupno** naručitelju |
| [Threads keyword search](https://developers.facebook.com/documentation/threads/keyword-search) | T, V | Threads API, dozvola `threads_keyword_search` | besplatno; 2.200 upita u 24 sata po korisniku; do 100 rezultata | samo signal | TOP ili RECENT | API za trendove ne postoji |
| [YouTube Data API](https://developers.google.com/youtube/v3/docs/videos/list) | T | službeni API, ključ | `chart=mostPopular` s `regionCode=HR` stoji 1 jedinicu i vraća do 50 videa; zadana kvota 10.000 jedinica dnevno (sekundarni izvori) | samo metapodaci i ugradnja | dnevno | YouTube je stranicu Trending ugasio 21. 7. 2025.; API i dalje dokumentira `mostPopular` |
| [Reddit Data API](https://redditinc.com/policies/data-api-terms) | T | OAuth API | oko 100 upita u minuti, samo za odobrenu nekomercijalnu uporabu; komercijalno traži ugovor, cijena nije objavljena | ne; zabrana treniranja AI-ja (sekundarni izvori) | trenutno | uvjeti nisu dohvaćeni izravno; malo hrvatske publike |
| [Telegram javni kanali](https://core.telegram.org/api/obtaining_api_id) | V | MTProto s `api_id`; Bot API ne čita kanal u kojem bot nije član | besplatno; zabrana spama; prijave s neslužbenih klijenata su pod nadzorom | ne | trenutno | smije li se čitati korisničkim računom za posao nije potvrđeno |
| [Bluesky](https://docs.bsky.app/) | T | javni API bez ključa (`public.api.bsky.app`), Jetstream | besplatno; ograničenja „izdašna", broj nije službeno objavljen | ne | trenutno | `app.bsky.unspecced.getTrendingTopics` radi (proba 4. 11.), ali vraća globalne, uglavnom američke teme; „unspecced" znači nestabilno sučelje |
| Facebook, LinkedIn | — | — | javnog API-ja za trendove ili čitanje tuđih objava nema | — | — | nije potvrđeno u pojedinostima |

## Alati za trendove

| izvor | za | pristup | cijena i ograničenja | preuzimanje | svježina | napomena |
|---|---|---|---|---|---|---|
| [TikTok Creative Center](https://ads.tiktok.com/help/article/trend-discovery) | T | samo ručno (web) | besplatno; javnog API-ja nema, anonimni JSON putevi vraćaju „no permission" (sekundarni izvori) | ne | dnevno do tjedno | trendovi po regiji i industriji; je li Hrvatska među regijama nije potvrđeno; pjesme u trendu nisu sve odobrene za komercijalnu uporabu, poslovni profil koristi Commercial Music Library |
| Google Trends (web) | T | samo ručno | besplatno | samo signal | gotovo trenutno | Hrvatska podržana |
| [Google Trends API](https://developers.google.com/search/apis/trends) | T | alpha, prijava za testere | cijena nije objavljena; posljednjih 5 godina, regije i podregije | samo signal | dnevno | Google kaže da ga ne može otvoriti svima |
| Google Trends „Trending now" RSS (`trends.google.com/trending/rss?geo=HR`) | T, V | RSS bez ključa | besplatno | samo signal | gotovo trenutno | radi (10 stavki, 4. 11.); nedokumentiran, službena podrška nije potvrđena |
| [Wikimedia Pageviews API](https://wikimedia.org/api/rest_v1/) | T | REST bez ključa, obavezan User-Agent | besplatno | samo signal | kasni oko 1 dan | najčitaniji članci `hr.wikipedia` po danu (proba 4. 11.: 2. 11. dostupan, 3. 11. još ne) |
| YouTube Charts | T | samo ručno | besplatno | ne | tjedno | glazba, podcasti, najave; Hrvatska nije potvrđena |
| Plaćeni agregatori trendova (Exploding Topics, Glimpse, Apify scraperi) | T | API ili web | plaćeno | — | — | nije potvrđeno; scraperi društvenih mreža krše uvjete platformi |

## Agencije i agregatori

| izvor | za | pristup | cijena i ograničenja | preuzimanje | svježina | napomena |
|---|---|---|---|---|---|---|
| [HINA](https://hina.hr/english) | V | pretplata | cijena vijesti nije javna (cjenik OTS-a, 30 € po priopćenju, je druga usluga); `hina.hr/rss` vraća 403 | da, prema ugovoru | trenutno | najčišći zakoniti put za hrvatske vijesti |
| FENA (BiH), Tanjug (RS), STA (SI), MINA (CG) | V | pretplata | nije potvrđeno | prema ugovoru | trenutno | regionalne agencije |
| [Reuters Connect](https://webcf.waybackmachine.org/web/20211004045531/https://www.reutersagency.com/en/about/faqs) | V | B2B platforma | uredničko licenciranje po bodovima, cijena ovisi o vrsti uporabe i publici; komercijalno po ponudi | prema licenci | trenutno | izvor je arhivirani FAQ iz 2021.; javnog RSS-a nema (401 na 4. 11.) |
| AP, AFP | V | licenca, API | cijena nije javna | prema licenci | trenutno | nije potvrđeno; `apnews.com` RSS vraća 403 |
| [GDELT DOC 2.0](https://www.gdeltproject.org/about.html) | T, V | API bez ključa | besplatno, i komercijalno; redistribucija podataka uz navođenje GDELT-a; jedan upit u 5 sekundi | podaci GDELT-a da, članci ne (daje naslov i URL) | 15 minuta | filtar `sourcecountry:croatia` radi |
| [NewsAPI.org](https://newsapi.org/pricing) | V | API | Developer besplatno samo za razvoj (ne produkcija), 100 upita dnevno, 24 sata kašnjenja; Business 449 $ mjesečno | puni tekst nije uključen | trenutno (plaćeno) | hrvatski izvori nisu potvrđeni |
| [Event Registry / NewsAPI.ai](https://newsapi.ai/plans) | V | API | besplatno 2.000 pretraga jednokratno; plan 5K 90 $ mjesečno; neiskorišteni tokeni propadaju | uvjeti nisu potvrđeni | trenutno | višejezično; pokrivenost hrvatskog nije potvrđena |
| [Google News RSS](https://www.google.com/intl/en_us/terms_google_news.html) | V | RSS (`hl=hr&gl=HR`) | besplatno | ne; uvjeti dopuštaju samo osobnu nekomercijalnu uporabu | trenutno | radi (38 stavki, 4. 11.); za poslovnog bota sporno |
| Newsdata.io, GNews, Mediastack | V | API | nije potvrđeno | nije potvrđeno | — | nije provjereno |

## Hrvatski mediji

RSS je proban `curl`-om 4. 11. Za sve: članci i fotografije su autorsko djelo, a nakladnik od 2021. ima
i srodno pravo ([ZAPSP, NN 111/21](https://narodne-novine.nn.hr/clanci/sluzbeni/2021_10_111_1941.html), čl. 163).
Opseg izuzeća za kratke isječke u hrvatskom zakonu nije potvrđen. Uvjeti koji nisu pročitani: „nije potvrđeno".

| medij | RSS (radi 4. 11.) | stavki | uvjeti preuzimanja |
|---|---|---|---|
| Index.hr | `index.hr/rss` | 150 | [uvjeti](https://www.index.hr/uvjeti-koristenja): umnožavanje i prerada bez pisanog odobrenja su povreda; **izričito zabranjeno rudarenje teksta i podataka** bez pisanog odobrenja |
| tportal | `tportal.hr/rss` | 20 | [uvjeti](https://www.tportal.hr/uvjeti-koristenja-tportal): komercijalna uporaba samo uz pristanak HT-a; mediji smiju prenositi uz izvor u zaglavlju; foto i video traže pisanu suglasnost |
| Jutarnji list | `jutarnji.hr/feed` | 50 | nije potvrđeno |
| Večernji list | `vecernji.hr/feeds/latest` | 20 | nije potvrđeno |
| 24sata | `24sata.hr/feeds/aktualno.xml` | 20 | nije potvrđeno |
| Poslovni dnevnik | `poslovni.hr/feed` | 20 | nije potvrđeno |
| Lider | `lider.media/rss.xml` | 59 | nije potvrđeno |
| N1 Hrvatska | `n1info.hr/feed/` | 50 | nije potvrđeno |
| HRT | `hrt.hr/rss/vijesti` | 33 | nije potvrđeno |
| Net.hr · Dnevnik.hr · RTL | `net.hr/feed` · `dnevnik.hr/rss` · `rtl.hr/rss` | 50 · 10 · 19 | nije potvrđeno |
| Slobodna Dalmacija · Novi list · Nacional | `slobodnadalmacija.hr/feed` · `novilist.hr/feed/` · `nacional.hr/feed/` | 50 · 10 · 21 | nije potvrđeno |
| Bloomberg Adria | `bloomberg-adria.com/rss` | 19 | nije potvrđeno |
| Total Croatia News · Croatia Week (engleski) | `total-croatia-news.com/feed` · `croatiaweek.com/feed/` | 11 · 11 | nije potvrđeno |

## Regionalni mediji

| medij | zemlja | RSS (radi 4. 11.) | stavki | uvjeti |
|---|---|---|---|---|
| N1 | BiH · Srbija · Slovenija | `n1info.ba/feed/` · `n1info.rs/feed/` · `n1info.si/feed/` | 50 svaki | nije potvrđeno |
| Klix.ba · Avaz | BiH | `klix.ba/rss` · `avaz.ba/rss` | 30 · 11 | nije potvrđeno |
| Vijesti.me | Crna Gora | `vijesti.me/rss` | 30 | nije potvrđeno; RTCG i CdM: RSS nije pronađen (404, 403) |
| B92 · RTS | Srbija | `b92.net/info/rss/vesti.xml` · `rts.rs/page/stories/sr/rss.html` | 20 · 20 | nije potvrđeno; Blic: RSS nije pronađen |
| 24ur · RTV Slovenija · Delo | Slovenija | `24ur.com/rss` · `rtvslo.si/feeds/00.xml` · `delo.si/rss` | 20 · 20 · 60 | nije potvrđeno |

## Globalni mediji

| medij | RSS (radi 4. 11.) | stavki | uvjeti |
|---|---|---|---|
| BBC World | `feeds.bbci.co.uk/news/world/rss.xml` | 32 | nije potvrđeno |
| The Guardian | `theguardian.com/world/rss` | 45 | nije potvrđeno; ima i Open Platform API |
| Euronews | `euronews.com/rss` | 50 | nije potvrđeno |
| DW | `rss.dw.com/rdf/rss-en-top` | 23 | nije potvrđeno |
| Al Jazeera · NPR | `aljazeera.com/xml/rss/all.xml` · `feeds.npr.org/1001/rss.xml` | 25 · 10 | nije potvrđeno |
| Reuters · AP | nema javnog RSS-a | — | samo licenca (vidi agencije) |

## Podaci za nekretnine i posao

| izvor | za | pristup | cijena i ograničenja | preuzimanje | svježina | napomena |
|---|---|---|---|---|---|---|
| [Eurostat](https://ec.europa.eu/eurostat/help/copyright-notice) | V | API i RSS (`statistics-update.rss`, 1.688 stavki 4. 11.) | besplatno | **da**, i komercijalno, uz navođenje izvora; prerada se mora označiti; podaci drugih izvora iznimka | po objavi | npr. indeks cijena kuća `prc_hpi_q` |
| HNB tečajnica (`api.hnb.hr/tecajn-eur/v3`) | V | API bez ključa | besplatno | uvjeti nisu pronađeni | dnevno | radi (tečajnica 216, 4. 11.); ostala statistika HNB-a nije provjerena |
| [ECB](https://www.ecb.europa.eu/rss/press.html) | V | RSS priopćenja | besplatno | nije potvrđeno | po objavi | kamate i odluke ECB-a |
| DZS (`podaci.dzs.hr`) | V | web baza; RSS nije pronađen | besplatno | licenca i API nisu potvrđeni | po objavi | cijene stanova i graditeljstvo; provjeriti uvjete |
| [data.gov.hr](https://data.gov.hr/) | V | portal otvorenih podataka | besplatno | prema licenci skupa | različito | nije provjereno po skupovima |
| Njuškalo | — | samo ručno | — | uvjeti nisu pročitani: stranica uvjeta vraća zaštitu od botova | — | `robots.txt` zabranjuje `/search` i `/papi/`; oglasi sadrže osobne podatke (GDPR); samo uz partnerski dogovor |
| Crozilla | — | samo ručno | — | uvjeti nisu dostupni (405) | — | `robots.txt` blokira robote; nije potvrđeno |

## Preporuka

**T, početak (besplatno, službeno ili ručno):** YouTube `mostPopular` za `HR`, Google Trends „Trending now"
RSS za `HR` i najčitaniji članci `hr.wikipedia` kao automatski signal tema. Format i zvuk bira čovjek ručno
iz TikTok Creative Centra i Instagram Professional Dashboarda. Kad naručitelj dobije Meta aplikaciju za
objavu, dodati Instagram hashtag search (30 hashtagova tjedno). Bot iz signala radi **vlastiti** Reel;
glazba samo iz komercijalne knjižnice platforme.

**V, početak (zakonito bez pregovora):** službeni podaci Eurostata, HNB-a, ECB-a i DZS-a za objave o
nekretninama i poslovanju, uz navođenje izvora. GDELT kao besplatan signal o čemu se piše. RSS hrvatskih
medija najviše kao signal naslova uz poveznicu, tek nakon provjere uvjeta pojedinog medija: Index.hr
rudarenje izričito zabranjuje. Za prepričavanje tuđih vijesti zakonit put je pretplata na HINA-u.

**Ne za početak:** TikTok Research API i Meta Content Library (nedostupni), X (plaća se po čitanju,
Hrvatska nepotvrđena), NewsAPI.org Developer (zabranjen u produkciji), Google News RSS (samo osobna
uporaba), scraperi TikToka, Instagrama i Njuškala.

## Otvoreno

1. Smije li bot sažimati tuđe vijesti, ili samo službene podatke i naručiteljeve teme? Treba pravnika.
2. Ima li naručitelj budžet za HINA-u ili drugu agenciju?
3. Koje teme i koja regija: samo nekretnine i posao u Hrvatskoj ili i regija?
4. Ima li naručitelj poslovni Instagram povezan s Facebook stranicom (hashtag search i objava)?
5. Ima li poslovni TikTok račun, zbog Commercial Music Libraryja?
6. Tko provjerava činjenice i navodi li Reel izvor na ekranu ili u opisu?
7. Veza s pitanjem 2 naručitelju o tuđim Reelovima ([pitanja-za-narucitelja.html](../client/pitanja-za-narucitelja.html)).
