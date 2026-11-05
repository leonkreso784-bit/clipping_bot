# Dizajn: Clipping, alat za plaćene clipping kampanje

**Datum:** 4. 11. 2026. · **Status:** ✅ odobrio Leon 4. 11. 2026. · **Autor:** Claude uz Leonove odluke iz sesije 4. 11.

Ovaj dokument zamjenjuje smjer iz `docs/plan/PLAN_V1.md` (vlastiti video, GTA 6). Graditelj bi iz njega trebao
moći složiti plan cigli bez pitanja Leonu. Što je Leon odlučio, piše "Leon". Što je Claudeov izbor, piše "izbor".

## 1. Namjera i zašto

Leon radi **clipping za druge kreatore kroz plaćene kampanje** (Clipping.net; Whop kasnije). Kampanja daje dugi video
i brief; clipper objavljuje kratke isječke na **vlastitim** računima i dobiva isplatu po 100.000 provjerenih pregleda.
Zarada ovisi o broju dobrih isječaka objavljenih dnevno na više računa i platformi. Ručno to ne skalira.

Alat radi na Leonovu računalu. Kad Leon kaže "kreni", alat sam prođe cijeli put od kampanje do objave, a Leon se
pojavljuje samo na jednom mjestu: pregledu serije prije objave. Claude Code bira trenutke iz prijepisa (nema
plaćenog API-ja po isječku, ADR-002), program reže (ADR-005).

Proba od 4. 11. (`docs/istrazivanje/PROBA_AUTOCLIP.md`) pokazala je da lanac "Claude bira, program reže,
kadriranje po licu, karaoke titlovi" daje kvalitetu koju Leon prihvaća. Ovaj dizajn gradi proizvod oko toga.

## 2. Ciljevi, ne-ciljevi, anti-ciljevi

**Ciljevi**
- Jedan dugi video (60 do 120 min) → 6 do 10 isječaka 9:16 s titlovima, žigom i tekstom po briefu, u manje od 30 minuta
  na Leonovu CPU-u (12 jezgri, 16 GB, bez grafičke).
- Nula ručnih koraka između "kreni" i mape za pregled. Nula ručnih koraka između odobrenja i objave na Instagram i YouTube.
- Svaki isječak ima zapisano: kampanja, brief, platforma, račun, status, poveznica objave, pregledi, isplata.
- Sve se može nastaviti nakon prekida (struja, Windows restart, Claude sesija ugašena).

**Ne-ciljevi (ovaj dizajn ne pokriva)**
- Leonov vlastiti kanal, GTA 6, hrvatski jezik. Ulazi su engleski videi iz kampanja.
- Objava na TikTok i X kroz API (ostaju ručne s mobitela, vidi §7).
- Desktop aplikacija za statistiku (kasnije; čita istu bazu, §9).
- Whop i druge platforme osim Clipping.net (kasnije; profil kampanje je neovisan o platformi).
- Automatizacija tuđih dashboarda preglednikom.

**Anti-ciljevi (ovo bi bio neuspjeh i da "radi")**
- Isječak objavljen bez Leonova odobrenja serije (ADR-003).
- Objava kroz neslužbeni alat ili automatizaciju preglednika (ADR-006). Jedna zabrana računa briše mjesece rada.
- Isječak koji krši brief (nema žiga, nema obveznog teksta, kriva platforma, tema koja se u briefu zabranjuje).
- Izvorni video koji nije iz kampanje (ADR-004).
- "Blatantly automated or low-effort" izgled: isti predložak bez udice, bez obrade. Clipping.net to izričito zabranjuje.

## 3. Ograničenja

| ograničenje | izvor | posljedica |
|---|---|---|
| CPU bez grafičke, 16 GB RAM | Leonovo računalo | modeli moraju raditi na CPU-u; Whisper large je prespor (103 min za 90 min videa) |
| Jedan račun po kreatoru i platformi | Leon | svaki profil kampanje nosi svoje račune; nema dijeljenja računa među kampanjama |
| Clipping.net: 50 %+ publike iz US/UK/CA/AU/NZ, bez botova, bez duplikata, objave ostaju javne do isplate, bez "očito automatiziranih" objava | pravila platforme (pročitana 4. 11.) | engleski, raznolik izgled isječaka, nikad brisati objavljeno |
| Platforme po kampanji: Caleb Hammer = TikTok, Instagram, X; ClubWPT Gold = Instagram, YouTube | dashboard 4. 11. | profil kampanje određuje platforme; alat ne objavljuje gdje se ne plaća |
| Brief traži žig (Caleb: centriran) i ponekad obvezni tekst, zvuk ili hashtag | briefovi 4. 11. | sloj grafike po profilu; provjera prije pregleda |
| Instagram API: 50 do 100 objava/24 h; YouTube: 100 uploada/dan, 10.000 jedinica kvote | dokumentacija | red objave s limitima po računu |
| Oznaka plaćene suradnje uvijek | Leon | Instagram `paid partnership` oznaka gdje API dopušta; u opisu "#ad" i "Paid partnership with <kreator>" |
| Ovisnosti pinane, samo MIT/Apache/BSD; modeli s licencom za komercijalnu uporabu | CLAUDE.md pravilo 8 | Parakeet v3 je CC-BY-4.0 („ready for commercial use“), potvrđeno u C1 5. 11. 2026. |
| Izvorni mediji i izlazi ne ulaze u git | CLAUDE.md pravilo 9 | `data/` i `izlaz/` u `.gitignore` |
| Ništa iz BOORA repozitorija | ADR-001 | gradimo nad otvorenim alatima; autoclip (MIT) je uzor |

## 4. Pojmovi

- **Kampanja**: unos na Clipping.net s briefom, cijenom po 100K, platformama i pragom kvalifikacije.
- **Profil kampanje**: naša YAML datoteka koja prevodi brief u pravila koja program može provjeriti (§5).
- **Izvor**: jedan dugi video iz kampanje, s zapisom prava (kampanja, poveznica na brief, datum).
- **Posao**: obrada jednog izvora: prijepis → kandidati → izbor → rezanje → provjera.
- **Isječak**: jedan MP4 9:16 s metapodacima (naslov, opis po platformi, indeksi riječi, ocjena, razlog).
- **Serija**: skup isječaka jednog posla koji Leon odobrava odjednom (ADR-003).
- **Objava**: jedan isječak na jednoj platformi i jednom računu; ima status i poveznicu.

## 5. Profil kampanje (Leon: po kreatoru; izbor: YAML)

Jedna datoteka po kampanji u `kampanje/<slug>.yaml`, ručno napisana iz briefa (prvi put uz Claudeovu pomoć).
Primjer za Caleb Hammer:

```yaml
slug: caleb-hammer
kreator: Caleb Hammer
platforma_kampanje: clipping.net
url_kampanje: https://clipping.net/...
cijena_po_100k_usd: 75
prag_kvalifikacije_pregleda: 50000
platforme: [tiktok, instagram, x]          # gdje se plaća; alat ne objavljuje drugdje
racuni:
  instagram: "@..."                         # jedan račun po kreatoru (Leon)
  tiktok: "@..."
  x: "@..."
izvori:
  dopusteni_kanali: ["https://www.youtube.com/@CalebHammer"]   # iz briefa; `kreni` prati nove videe
  zapis_prava: "brief od 2026-11-03, poveznica ..."
isjecak:
  trajanje_s: {min: 20, max: 90}
  jezik: en
grafika:
  zig: {datoteka: kampanje/caleb-hammer/zig.png, polozaj: centar, neprozirnost: 0.85}
  obvezni_tekst: null                       # npr. "Toronto" za Zeds Dead
  obvezni_zvuk: null                        # npr. TikTok sound ID
  hashtagovi: ["#calebhammer", "#ad"]
opis:
  oznaka_placene_suradnje: true
  predlozak: "{udica}\n\nPaid partnership with Caleb Hammer. Full episode: {url_izvora}\n{hashtagovi}"
pravila_sadrzaja:
  zabranjeno: ["ismijavanje gosta izvan onoga što sam kaže"]
  stil_titlova: [bold_pop, clean_lower]      # rotira se po isječku
  psovke: {titlovi: zvjezdice, zvuk: nista}  # Leon, 4. 11. 2026.
raspored:
  objava_dnevno_po_racunu: 2
  zagrijavanje_dana: 7                      # prvi tjedan 1 do 2 objave dnevno
```

Program odbija posao ako profil nema žig kad brief to traži, ili ako platforma na kojoj bi objavio nije u `platforme`.
Što brief zahtijeva a program ne može provjeriti (npr. "pozitivan ton") ide u uputu Claudeu pri izboru.

## 6. Lanac obrade

```text
kreni
 └► 1. ulaz       yt-dlp (samo poveznice iz briefa) ili datoteka → data/<izvor>/source.mp4 + zapis prava
 └► 2. zvuk       FFmpeg: 16 kHz mono WAV; sličice svakih 5 s (za pregled i kasniju multimodalnu provjeru)
 └► 3. prijepis   Parakeet TDT 0.6B v3 kroz onnx-asr na CPU-u, s VAD-om u dijelovima od ~30 s;
                  izlaz: riječi s vremenima (isti oblik kao proba: transcript.json)
 └► 4. tišine     FFmpeg silencedetect → granice za rezove
 └► 5. prijepis za Claudea: window.txt s [i]riječ (kao u probi), plus sažetak profila (pravila, ton)
 └► 6. izbor      Claude Code čita i vraća candidates.json: start_word_index, end_word_index, title, hook,
                  score, reason, opis po platformi; program odbija indekse izvan prijepisa i trajanja izvan profila
 └► 7. rezanje    za svaki kandidat: rez na granicu rečenice/tišine, kadriranje po licu (MediaPipe, uzor autoclip),
                  karaoke titlovi (ASS + libass, stil iz profila), žig i obvezni tekst (FFmpeg overlay/drawtext),
                  −14 LUFS, H.264 1080×1920 30 fps → izlaz/<posao>/<isjecak>.mp4
 └► 8. provjera   automatska: trajanje u granicama, glasnoća, titlovi u sinkronu (±100 ms na uzorku riječi),
                  žig prisutan (usporedba piksela na poznatom položaju), obvezni tekst prisutan, nema crnih kadrova;
                  neovisni pregled: drugi Claude agent gleda sličice i prijepis isječka i ocjenjuje po briefu
 └► 9. pregled    mapa izlaz/<posao>/ + PREGLED.md (tablica: isječak, platforme, opis, ocjena, što je provjera našla);
                  Leon odobri seriju ili izbaci pojedine (jedna datoteka ODOBRENO.txt ili naredba)
 └► 10. objava    Instagram (Graph API, Reels) i YouTube (Data API, Shorts) iz reda s limitima i rasporedom;
                  TikTok i X: mapa mobitel/<racun>/ s MP4 + opis.txt, Leon objavi s mobitela i zalijepi URL
 └► 11. prijava   poveznice objava se upisuju u bazu; prijava na Clipping.net ručno (nema API-ja) uz popis koji alat ispiše
 └► 12. praćenje  dnevno čitanje pregleda kroz službene API-je (IG, YT) i ručni unos za TikTok/X; isplate ručno
```

Koraci 1 do 5 i 7 do 8 su program (Python). Korak 6 je Claude Code. Korak 9 je Leon. Korak 10 do 12 program, osim
ručnih platformi.

**Zašto Parakeet (izbor).** Proba: Whisper large-v3-turbo na CPU-u 103 min za 90 min videa, koristeći 1 do 4 jezgre.
Parakeet TDT 0.6B v3 kroz onnx-asr radi bez torcha, na CPU-u, s vremenima riječi; objavljeni CPU rezultati su reda
desetaka puta brže od stvarnog vremena. Cigla C1 mjeri na istom videu; prolaz je ispod 10 minuta. Ako padne,
rezerva je faster-whisper `medium` s 12 niti (isto mjeriti).

**Zašto autoclip kao uzor, ne ovisnost (izbor).** Kadriranje i titlovi su dobri, ali autoclip nosi vlastiti LLM sloj,
vlastitu bazu, Whisper i web sučelje. Uzimamo obrasce (CropPath, segment_crop_filter, pysubs2 stilovi, jedan FFmpeg
prolaz po isječku) u vlastiti kod s navedenim izvorom i MIT napomenom. Graditelj može odlučiti vendorati pojedine
module ako je to brže, uz zapis u ADR.

## 7. Objava

| platforma | kako | tko | napomena |
|---|---|---|---|
| Instagram | Graph API: spremnik → stanje → objava; `paid partnership` oznaka kroz `collaborators`/branded content gdje je dostupno, inače u opisu | program | profesionalni račun, povezan s Facebook stranicom; limit 50/24 h po računu |
| YouTube | Data API `videos.insert`, Shorts su obični uploadi 9:16 ≤ 3 min; `publishAt` za raspored; prvi upload potvrđuje ostaje li javan za neprovjeren projekt | program | kvota 10.000 jedinica/dan, upload 1.600 jedinica |
| TikTok | mapa `mobitel/<racun>/<datum>-<isjecak>.mp4` + `opis.txt`; Leon objavi s mobitela; alat čeka URL | Leon | API bez audita ne objavljuje javno; audit odbija alate za vlastite račune |
| X | isto kao TikTok | Leon | API za objavu videa je plaćen; ručno |

Red objave: SQLite tablica `objava` sa statusom (`ceka`, `zakazano`, `objavljeno`, `greska`, `rucno_ceka_url`),
vrijeme, račun. Radnik objave uzima prvu dospjelu, poštuje `objava_dnevno_po_racunu` i zagrijavanje, i nikad ne
objavljuje isti isječak dvaput na istu platformu (duplikat = kršenje pravila).

Tajne (OAuth tokeni) u `.env` izvan gita; osvježavanje tokena automatski; istek traži Leonovu prijavu jednom.

## 8. Baza stanja i nastavljivost (izbor: SQLite)

Jedna datoteka `data/clipping.db`. Tablice: `kampanja`, `izvor` (s pravima), `posao`, `isjecak`, `objava`, `pregledi`
(dnevne brojke), `isplata`. Svaka faza posla upisuje status prije i poslije; `kreni` nastavlja od zadnjeg
dovršenog koraka (prijepis se ne ponavlja ako `transcript.json` postoji i hash izvora se slaže).

Statusi isječka: `izrezan → provjeren → odobren | izbacen → zakazan → objavljen → prijavljen → placen`.

## 9. Pokretanje: "kreni" i bez Leona

- Naredba `clipping kreni [--kampanja slug] [--izvor url]`: pokreće korake 1 do 9 i stane na pregledu.
- Korak 6 (izbor) se izvodi kroz `claude -p` s uputom i `window.txt`, uz shemu odgovora; program provjerava JSON.
  Ako Claude vrati manje od `min` kandidata ili neispravne indekse, program traži ponovno (najviše 2 puta), pa javlja grešku.
- Naredba `clipping objavi <posao>` nakon ODOBRENO; `clipping prati` dnevno.
- Windows Task Scheduler pokreće `clipping prati` svaki dan i `clipping objavi` svakih 30 min (samo odobrene serije).
- Dnevnik: `izlaz/<posao>/dnevnik.log` i tablica `dogadjaj` u bazi.
- Desktop app (kasnije, Tauri ili slično) čita istu bazu: zarada, pregledi po računu, propuštene i nove kampanje.

Što Leon radi ručno, i to je sve: otvara račune i povezuje ih (jednom), piše/odobrava profil kampanje (jednom po
kampanji), pregledava seriju (nekoliko minuta po poslu), objavljuje TikTok i X s mobitela, prijavljuje poveznice na
Clipping.net i prima isplate.

## 10. Kvaliteta i mjerenje

- Svaka cigla ima dokaz: izmjereno vrijeme ili test koji bi pao na starom kodu (CLAUDE.md pravilo 3).
- Zlatni video za mjerenje: Caleb Hammer `JvLklMRThYs` (90 min), isti kao u probi. Referentni isječci iz probe su
  u `izlaz/proba-2026-11-04-caleb-hammer/`.
- Ciljevi: prijepis < 10 min; rezanje < 2 min po isječku; cijeli posao < 30 min; 0 isječaka bez žiga; 0 duplikata.
- Praćenje učinka po isječku (pregledi u 48 h) ide u bazu i kasnije u uputu Claudeu (koji tipovi udica rade).

## 11. Rizici

| rizik | što radimo |
|---|---|
| Parakeet nije dovoljno točan ili licenca ne dopušta | C1 mjeri WER na uzorku i čita licencu; rezerva Whisper medium |
| Instagram/YouTube odbiju API aplikaciju ili traže pregled | prvi tjedan ručno s mobitela; API tek nakon što računi imaju povijest |
| Platforme kažnjavaju "automatizirani" izgled | raznolik stil (2 do 3 stila titlova, različite udice), 1 do 2 objave dnevno u zagrijavanju, Leonov pregled |
| Clipping.net odbije isplatu (publika izvan ciljanih zemalja) | pratiti geografiju gledatelja u IG/YT statistici; opisi i hashtagovi na engleskom |
| yt-dlp se lomi | pinana verzija, nadogradnja kao namjerna radnja; rezerva: ručno skinuta datoteka |
| Porez i isplate | Leonova odgovornost; preporučen računovođa prije prve veće isplate |

## 11a. Odgovori na pitanja iz pregleda graditelja (4. 11.)

1. **Odakle `kreni` uzima izvor.** Profil kampanje ima `izvori.dopusteni_kanali` (YouTube kanal ili playlist iz briefa).
   `kreni` bez `--izvor` ispiše popis videa kanala (yt-dlp, samo metapodaci), uzme najnoviji koji nije u tablici
   `izvor`, i obradi ga. `--izvor <url>` radi samo ako je URL s dopuštenog kanala; inače odbija (ADR-004). Leon je
   tražio da alat sam prati kampanje; Clipping.net nema API, pa je praćenje kanala kreatora najbliže tome. (izbor)
2. **ADR-005 i pravilo 4.** Vrijedi novi model potvrđen probom: Claude vraća **indekse prve i zadnje riječi**, naslov,
   udicu, ocjenu i razlog; program pomiče rezove na granicu rečenice ili tišine i odbija indekse izvan prijepisa ili
   trajanja izvan profila. Program ne slaže kandidate unaprijed. ADR-005 i CLAUDE.md pravilo 4 se mijenjaju tako. (Leon, probom)
3. **Psovke.** Titlovi prikazuju psovke sa zvjezdicama (program ima popis riječi), zvuk ostaje netaknut, isto na
   svim platformama. Polje profila `psovke: {titlovi: zvjezdice|puno, zvuk: nista|beep}`; `beep` se ne gradi u V1. (Leon)
4. **Objava kroz API u V1.** Računi još ne postoje (Leon ih otvara kasnije). C3 odmah radi mapu `mobitel/<racun>/`
   za **sve** platforme, pa se prva serija objavljuje ručno s mobitela. C4 (API) se gradi tek kad računi postoje i imaju
   tjedan ručne povijesti; test C4 ide na ClubWPT profil (ima YouTube) i Caleb profil (Instagram). (izbor)
5. **Licence.** Pravilo 8 se precizira: za kod MIT/Apache/BSD; za **težine modela i fontove** licenca mora dopuštati
   komercijalnu uporabu, uz navođenje autora ako traži (CC-BY-4.0, OFL za fontove prolaze;
   nekomercijalne i "research only" ne prolaze). C1 je potvrdio: Parakeet v3 CC-BY-4.0. (izbor)
6. **Raznolikost stilova.** `stil_titlova` je popis; C2 rotira stilove po isječku (indeks mod broj stilova). Proba je
   dala `bold_pop`; C2 dodaje bar još jedan (npr. `clean_lower`). Različite udice su posao Claudea pri izboru. (izbor)
7. **30 minuta po poslu** je smjer, ne uvjet prolaza. Uvjeti prolaza su po cigli (C1: prijepis < 10 min; C2: < 2 min po
   isječku). Sličice se rade rjeđe (svakih 15 s) i samo za pregled; paralelno rezanje je graditeljev izbor. (izbor)
8. **Duplikati.** Baza pamti pokrivene raspone izvora (`izvor_id`, `start_s`, `end_s`) po kampanji. Novi isječak koji se
   preklapa više od 50 % s već objavljenim u istoj kampanji se odbija, bez obzira na posao ili platformu. (izbor)

## 12. Što ostaje graditelju

- Struktura Python paketa, CLI alat (preporuka: `typer`), raspored modula.
- Točan način kadriranja (vlastita implementacija po uzoru na autoclip ili vendorani moduli).
- Format `PREGLED.md` i način odobrenja (datoteka ili naredba), dok god je jedan korak za Leona.
- Kako se obvezni tekst crta (drawtext ili ASS sloj) i gdje stoji da ne pokriva lice ni titlove.
- Shema SQLite tablica u detalje; migracije.
- Redoslijed cigli, uz preporuku: C1 prijepis (Parakeet, mjerenje) → C2 rezanje po profilu (žig, tekst, titlovi) →
  C3 baza, `kreni`, pregled → C4 objava Instagram + YouTube → C5 praćenje i prijava.

## 13. Odluke koje ovaj dizajn traži u DECISIONS.md

- ADR-007: smjer projekta su plaćene kampanje, engleski; vlastiti kanal i GTA 6 su parkirani.
- ADR-008: prijepis Parakeet TDT na CPU-u umjesto Whispera (uvjetno na C1 mjerenju i licenci).
- ADR-009: autoclip (MIT) kao uzor za kadriranje i titlove; ne kao ovisnost.
- ADR-010: Instagram i YouTube kroz API, TikTok i X ručno iz pripremljene mape.
- ADR-011: jedan račun po kreatoru i platformi; oznaka plaćene suradnje uvijek.
- ADR-005 prelazi iz "prijedlog" u "potvrđeno probom" (Claude vraća indekse riječi, program računa vremena).
- CLAUDE.md pravilo 8 se precizira za težine modela i fontove (vidi §11a, točka 5).

## 14. Otvoreno za Leona

Nema otvorenih pitanja. Psovke su odlučene 4. 11. 2026. (§11a, točka 3): zvjezdice u titlovima, zvuk netaknut.
