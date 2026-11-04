> **Snimka iz BOORA repozitorija, 4. 11. 2026.** Poveznice `../records/…` i `../architecture/…` vode u
> `C:\Users\leonk\Documents\Bot za BOORA.ai\docs\`, ne u ovaj repozitorij.

# Ideja: kako sustav može zarađivati

Kako Leon može zarađivati od sustava koji automatski radi kratke videe, koliko kupaca za to treba i
kakvo je tržište. Provjereno 2026-11-04, osim gdje piše drukčije.

> Nije plan i nije obećanje. Ništa od ovoga ne počinje prije odgovora na pitanje
> „Gradimo li samo za jednog naručitelja ili i za druge?" ([BACKLOG](../records/BACKLOG.md)) i prije
> dogovora s naručiteljem o vlasništvu koda. Ovo nije pravni ni porezni savjet.

**Kako čitati brojke.** Uz svaku brojku stoji izvor. **Potvrđeno** znači da je službena stranica
pročitana 4. 11.; **sekundarno** znači agregator ili članak; **procjena** je izračun ovog dokumenta.
Cijene konkurenata su u USD jer ih tako objavljuju. Tečaj nije preračunavan.

## Modeli zarade

Kupaca za 3.000 €/mj je procjena: cilj podijeljen s pretpostavljenom cijenom, bez PDV-a, prije troškova.
1.000 €/mj traži trećinu tog broja, a 10.000 €/mj trostruko više.

| model | tko plaća | realna cijena | kupaca za 3.000 €/mj | trud | rizik | do prvog novca |
|---|---|---|---|---|---|---|
| **A. Gotovi Reelovi kao usluga** | lokalna tvrtka koja već objavljuje | 150 do 300 €/mj za 15 do 30 Reelova, plus jednokratan postav predloška (procjena; agencije traže 300 do 700 €/mj za osnovni paket, vidi ispod) | 10 do 20 | **S**: postav predloška po brendu i podrška; kod već postoji za jedan profil | srednji: Leonovo vrijeme raste s brojem kupaca | 2 do 6 tjedana |
| **B. Nišni proizvod: nekretnine** | agencija za nekretnine | 99 do 199 €/mj po agenciji (procjena; AutoReel traži 59 $/mj za 3 videa oglasa, [FAQ](https://www.autoreelapp.com/faq/cost-effective-realtor-tools/can-real-estate-photographers-afford-ai-video-tools-to-offer-video-services), prodavateljev izvor) | 15 do 30 (1 do 2 % od 1.534 agencije) | **S**: isto kao A, plus ulaz iz vlastitog oglasa ([PRILIKE.md](./PRILIKE.md) §5) | srednji: tržište sporije od 2026. ([Novi list](https://www.novilist.hr/?p=1685163)) | 1 do 3 mjeseca |
| **C. White-label za marketinške agencije** | agencija koja vodi profile klijenata | 300 do 800 €/mj po agenciji za više profila (procjena) | 4 do 10 | **V**: više profila, prijava, odvojene kvote ([OTVARANJE.md](./OTVARANJE.md)) | srednji: malo kupaca, svaki odlazak boli; agencija posjeduje odnos s klijentom | 3 do 6 mjeseci |
| **D. SaaS pretplata** | tvrtke i kreatori sami | 19 do 49 €/mj (procjena, ispod i oko konkurencije) | 60 do 160 | **V**: prijava, naplata, podrška, uređivač, marketing | visok: globalni konkurenti jeftiniji i bolje financirani | 6 do 12 mjeseci |
| **E. Clipping za kreatore i kampanje** | kreatori ili kampanje po pregledu | medijan oko 1 $ na 1.000 provjerenih pregleda (sekundarno, vidi ispod) | oko 3 mil. plaćenih pregleda mjesečno | **S**: clipping još nije izgrađen | visok: plaća se samo prolaz, isplata nije zajamčena | nepredvidivo |
| **F. Vlastiti kanali** | platforma iz oglasa | Shorts oko 0,01 do 0,07 $ na 1.000 pregleda (sekundarno) | desetci do stotine milijuna pregleda mjesečno | **V**: sadržaj svaki dan | vrlo visok: algoritam, kazna za neoriginalan sadržaj | 6 do 18 mjeseci, često nikad |

### Pojedinosti

- **A i B su ista tehnika s različitom prodajom.** B prodaje istu uslugu jednoj grani, pa svaki kupac
  zna što dobiva, a predložak i ton profila se ponavljaju. Podatak o tržištu: 1.534 agencije u Registru
  posrednika i 4.901 agent u Imeniku na 31. 12. 2025. ([PZE 276, Sabor](https://www.sabor.hr/sites/default/files/uploads/sabor/2026-03-18/142202/PZE_276.pdf), potvrđeno u sažetku pretrage).
  Novi Zakon o posredovanju (NN 69/2026) primjenjuje se od 7. 7. 2026. i uređuje oglašavanje ([zakon.hr](https://www.zakon.hr/c/vijest/1058127/na-snagu-stupio-novi-zakon-o-posredovanju-u-prometu-nekretnina-%E2%80%93-jasnija-pravila-za-provizije%2C-oglasavanje-i-razgledavanje-nekretnina)),
  što je argument za proizvod koji provjerava obavezne podatke oglasa.
- **Turizam i apartmani:** velik broj vrlo malih kupaca, sezonski. Ukupan broj iznajmljivača u 2025.
  nije pronađen u službenom izvoru (eVisitor, DZS). Realnije kao sezonski paket (ožujak do lipnja) nego
  kao cjelogodišnja pretplata (procjena).
- **Ugostitelji:** broj restorana za 2025. nije pronađen. Sadržaj (jelo, prostor, događaj) dobro odgovara
  Reelu od fotografije, ali spremnost na plaćanje nije provjerena.
- **Clipping (E):** samo okvirno. Pregled 50 kampanja na Whop Content Rewards dao je medijan 1,00 $
  na 1.000 pregleda, raspon 0,05 do 3,00 $, isplata tek nakon odobrenja i za provjerene preglede
  ([OpenClip, 28. 9. 2026](https://openclip.app/clipping/clipper-pay-rates), izvor je konkurentska
  platforma). Pravila platformi i tehnika clippinga idu u zaseban dokument.
- **Vlastiti kanali (F):** TikTok Creator Rewards je prema sekundarnim izvorima dostupan u 7 do 8
  zemalja, a Hrvatska nije na popisu ([ttcalculator](https://ttcalculator.net/learn/creator-fund-countries/), nije potvrđeno kod TikToka).
  Facebook Content Monetization je djelomično na poziv i Meta ne objavljuje popis zemalja
  ([SocialBee](https://socialbee.com/blog/monetize-facebook-reels/), sekundarno). RPM za Shorts:
  [Joyspace](https://joyspace.ai/youtube-shorts-rpm-2026-calculator), sekundarno; službene brojke nema.
  Instagram od travnja 2026. uklanja preporuke računima koji uglavnom ponovno objavljuju tuđe
  ([Tubefilter](https://tubefilter.com/2026/04/30/instagram-removes-algorithm-recommendations-repost-content-aggregator)).

## Tržište i konkurencija

| podatak | brojka | izvor |
|---|---|---|
| Tržište AI generatora videa | 1,08 mlrd. USD (2025.) do 1,97 mlrd. USD (2030.), CAGR 12,8 %; drugi izvještaj daje 10,55 mlrd. USD za 2025. i 20 % rasta | [Knowledge Sourcing](https://www.knowledge-sourcing.com/report/ai-video-generator-market), sekundarno; procjene se razlikuju deset puta jer svaka tvrtka drukčije definira tržište |
| OpusClip | oko 10 mil. USD prihoda 2024., valuacija oko 215 mil. USD (ožujak 2025.), 10 mil.+ korisnika | [CB Insights](https://www.cbinsights.com/company/opus-clip/financials), [aiwiki](https://aiwiki.ai/wiki/opus_clip), sekundarno |
| Kratki video i povrat ulaganja | 49 % marketinških stručnjaka kaže da kratki video donosi najveći ROI (HubSpot 2026) | [Shno](https://www.shno.co/marketing-statistics/short-form-video-statistics), sekundarno; HubSpotov izvještaj nije pročitan |
| Besplatna konkurencija | Meta Edits besplatan u svibnju 2026., Meta najavljuje moguće plaćene AI funkcije | [inro.social](https://www.inro.social/blog/edits-new-meta-app), sekundarno |

### Cijene konkurenata

| alat | što radi | cijena | izvor |
|---|---|---|---|
| OpusClip | dugi video u isječke, titlovi, zakazivanje | Free, Starter 15 $/mj, Pro 29 $/mj (API, zakazivanje, do 4 predloška), Business po ponudi | [opus.pro/pricing](https://www.opus.pro/pricing), potvrđeno |
| Submagic | titlovi i montaža | Starter 19 $, Pro 39 $, Business 69 $ po članu mjesečno; godišnje 12, 23, 41 $; 15, 40, 100 videa | [submagic.co/pricing](https://www.submagic.co/pricing), potvrđeno |
| Vizard | isječci, zakazivanje | iznosi se na službenoj stranici nisu prikazali; Pro oko 29 do 50 $/mj | [Layer3 Labs, 4. 10. 2026](https://www.layer3labs.io/guides/vizard-ai-pricing), sekundarno |
| Predis.ai | AI objave i videi | Core 32 $, Rise 79 $, Enterprise+ 249 $ mjesečno | [AdMake, 18. 10. 2026](https://admakeai.com/alternatives-to/predis-ai/pricing), sekundarno |
| CapCut | montaža | Pro 12,99 €/mj ili 89,99 €/god (Francuska), Business 24,99 € po sjedalu; besplatna razina samo za nekomercijalnu uporabu | [Spliiit, 23. 4. 2026](https://www.spliiit.com/en/blog/capcut-apk-tarif-alternative), [Async](https://async.com/blog/capcut-terms-of-service/), sekundarno |
| Canva | dizajn, predlošci, Brand Kit | Pro 144 $/god od 11. 9. 2026.; Business oko 250 $/god po osobi | [PricingSaaS](https://pricingsaas.com/companies/canva/diffs/2026D254), sekundarno |
| Blaze | AI marketing sadržaj | Starter oko 79 $/mj, Growth 149 $/mj | [PricingSaaS](https://pricingsaas.com/companies/blaze), sekundarno |
| Metricool | zakazivanje i analitika | Free, Starter 20 $/mj, Advanced od 53 $/mj | [Metricool](https://metricool.com/metricool-vs-later/), prodavateljev izvor |
| Later | zakazivanje | Starter 25 $/mj (16,67 $ godišnje) | [Metricool](https://metricool.com/metricool-vs-later/), konkurentov izvor |
| Agencija u HR | vođenje mreža | osnovno 300 do 700 €/mj, srednje 700 do 1.500 €, premium 1.500 do 3.000 €+ | [Kontentino, 14. 5. 2026](https://www.kontentino.com/hr/blog/paketi-za-drustvene-mreze-za-male-tvrtke-vodic-kroz-cijene/), sekundarno; objavljen cjenik hrvatske agencije s Reelovima nije pronađen |
| Slovenija | vođenje mreža | freelanceri 300 do 1.500 €/mj, butik agencije 1.500 do 5.000 € | [Picmim](https://blog.picmim.com/si/blog/social-media-management-pricing-2026), sekundarno |
| UGC kreator u HR | jedan video od 30 s | prosjek oko 60 €, raspon oko 24 do 66 € | [Influee](https://influee.co/hr/ugc-kreator/zemlje/hrvatska), platforma posrednik |

### Što konkurenti ne rade dobro

| praznina | koliko je stvarna |
|---|---|
| **Gotov Reel u točnom predlošku brenda**, bez otvaranja alata | Stvarna. Alati daju alat i opće predloške; korisnik i dalje uči i slaže. Canva od rujna 2026. ima autofill brand predložaka preko API-ja ([PRILIKE.md](./PRILIKE.md) §3), pa se razlika može smanjiti. |
| **Hrvatski tekst u tonu profila**, s pravilima tipografije | Djelomično stvarna. Submagic i OpusClip tvrde da rade hrvatske titlove ([Submagic](https://submagic.co/auto-subtitle-generator/croatian), [OpusClip](https://www.opus.pro/de-de/tools/add-croatian-subtitles-to-video)), ali to je prijepis, ne pisanje teksta. Claude piše dobro na hrvatskom i dostupan je svima, pa jezik sam nije zaštita. |
| **Telegram kao sučelje** | Stvarna za zauzetog urednika na mobitelu, ali lako se kopira i nije razlog za kupnju. Kupac plaća rezultat, ne sučelje. |
| **Čovjek iza usluge**, lokalno i na hrvatskom | Najjača prednost za model A i B. Globalni SaaS ne nudi poziv, postav predloška i prilagodbu. Ne skalira se. |
| Srpski, bosanski, slovenski | Tehnički blizu (isti stack, drugi `style.md`), ali svaki jezik traži provjeru izvornog govornika i lokalnu prodaju. Procjena. |

**Zaključak o tržištu:** opći AI video alati su zasićeni i jeftini (15 do 70 $/mj), a glavni igrači imaju
desetke milijuna dolara. Natjecati se s njima kao SaaS nema smisla. Prostor postoji između agencije
od 300 do 700 €/mj i alata od 20 $/mj: **gotova usluga po nižoj cijeni od agencije**, uz rezultat koji
alat sam ne daje.

## Troškovi i marža

| stavka | trošak | izvor |
|---|---|---|
| Claude po prolazu A do D | 0,23 do 0,30 USD | [PILOT_MJERENJA](../records/PILOT_MJERENJA.md), izmjereno 3. 11. |
| Claude po Reelu s ponovnim prijedlozima | oko 0,30 do 0,60 USD | procjena: jedan do dva prolaza |
| Claude za 30 Reelova mjesečno | oko 9 do 18 USD | procjena |
| Prijepis (lokalni Whisper) | 0 €, samo procesor | [ARCHITECTURE.md](../architecture/ARCHITECTURE.md) |
| Poslužitelj | Hetzner CX33 8,49 €/mj nakon poskupljenja 15. 6. 2026.; za više kupaca veći stroj, red veličine 20 do 40 €/mj | [Northflank](https://northflank.com/blog/hetzner-cloud-server-price-increases), sekundarno; izbor pružatelja je otvoren ([OPERATIONS.md](../architecture/OPERATIONS.md)) |
| Objava preko službenih API-ja | 0 € | [OBJAVA.md](./OBJAVA.md) |
| Glazba, ako se peče u MP4 | 0 € (Pixabay) do oko 30 $/mj (Epidemic Business) | [PRILIKE.md](./PRILIKE.md) §1 |

**Što to znači (procjena):** kupac s 30 Reelova mjesečno stoji oko 10 do 20 € AI-ja i dio poslužitelja.
Uz 200 €/mj izravna marža je iznad 85 %. **Pravi trošak je Leonovo vrijeme:** postav predloška, ispravci,
podrška i prodaja. Ako kupac traži 2 sata mjesečno, 15 kupaca je 30 sati mjesečno uz studij. Zato cijena
mora uključivati jednokratan postav (npr. 150 do 300 €) i jasnu granicu ispravaka.

## Prednosti koje Leon realno ima

1. **Radni sustav, ne ideja.** Pilot od kraja do kraja s izmjerenim troškom po Reelu.
2. **Prvi naručitelj u niši nekretnina i poslovnog sadržaja**, ako ugovor dopusti da posluži kao referenca.
3. **Hrvatski tekst i tipografija kao gotov proizvod**, ne kao titl.
4. **Niski troškovi**: nema plaća ni ureda, pa i 5 kupaca pokriva troškove.
5. **Lokalna prisutnost**: osobni sastanak i postav predloška, što globalni alat ne nudi.

Slabosti: jedan čovjek, uz studij; nema prodajnog iskustva; nema više profila, prijave ni naplate;
kvaliteta na stvarnim materijalima još nije izmjerena.

## Preporuka

**Počni s modelom A, usmjerenim na nekretnine (B): gotovi Reelovi kao mjesečna usluga po fiksnoj cijeni.**
Kod za jedan profil već postoji, kupcu ne treba uvjeriti da nauči alat, cijena od 150 do 300 €/mj je ispod
agencije, a 3.000 €/mj traži 10 do 20 kupaca, ne stotine. SaaS i white-label dolaze tek kad usluga dokaže
da kupci ostaju i kad je poznato koliko vremena kupac traži.

**Redoslijed za sljedećih 90 dana:**

| dani | korak | izlazni uvjet |
|---|---|---|
| 0 do 30 | **Završi pilot i razjasni temelje.** Probni tjedan s naručiteljem ([PRIMOPREDAJA.md](../workflow/PRIMOPREDAJA.md)), ispuni [PILOT_MJERENJA](../records/PILOT_MJERENJA.md). Pisano dogovori s naručiteljem tko je vlasnik koda i smije li Leon nuditi sustav drugima. Razgovaraj s računovođom o obliku poslovanja. | naručitelj prestao koristiti Canvu za obične Reelove; pisani dogovor o vlasništvu; Leon zna u kojem obliku smije izdati račun |
| 30 do 60 | **Tri plaćena pilota.** Tri agencije za nekretnine ili lokalne tvrtke, mjesec po sniženoj cijeni uz postav predloška. Bez novog koda osim onog što pilot traži. Bilježi sate po kupcu. | barem 2 od 3 nastavljaju plaćati; poznato vrijeme po kupcu mjesečno |
| 60 do 90 | **Odluka o rastu.** Ako kupci ostaju i vrijeme po kupcu je podnošljivo: plan za više profila ([OTVARANJE.md](./OTVARANJE.md)) i objavu ([OBJAVA.md](./OBJAVA.md)), pa cilj 10 kupaca. Ako ne: razgovor s 1 do 2 marketinške agencije o modelu C, ili ostanak na jednom naručitelju. | zapisana odluka u [DECISIONS.md](../records/DECISIONS.md) |

**Glavni rizik:** Leonovo vrijeme. Usluga koja raste bez granice ispravaka i bez jednokratnog postava
pojede studij i ne skalira se. Drugi rizik je pravni: bez pisanog dogovora s naručiteljem nije jasno smije
li Leon isti sustav prodavati drugima.

## Pravno i poslovno: što pitati

Samo upozorenja. Odgovore daju računovođa i pravnik.

| tema | što znamo | što razjasniti |
|---|---|---|
| **Vlasništvo koda** | Sustav se gradi za naručitelja; BACKLOG još pita je li BOORA.ai naručitelj ili Leonova firma | Prenosi li se kod naručitelju ili dobiva licencu? Ekskluzivnost za granu ili regiju? Smije li Leon koristiti isti kod i ime naručitelja kao referencu? Predložak, logotip i materijali ostaju naručiteljevi. |
| **Oblik poslovanja** | Paušalni obrt vrijedi do 60.000 € godišnjih primitaka ([Fiskai](https://www.fiskai.hr/vodic/pausalni-obrt/), sekundarno); postoje i j.d.o.o. i d.o.o. | Što je povoljnije uz studij, koliki su fiksni mjesečni doprinosi, može li se uz obrt i dalje raditi preko studentskog ugovora. |
| **PDV** | Prag za ulazak u sustav PDV-a je 60.000 € od 1. 1. 2025. ([Porezna uprava](https://porezna-uprava.gov.hr/hr/oporezivanje-potrosnje/4743)) | 3.000 €/mj je 36.000 €/god, ispod praga; 10.000 €/mj ga prelazi. Što vrijedi za usluge kupcima izvan Hrvatske i za plaćanje stranih alata (Anthropic, poslužitelj). |
| **Studentski status** | Od 2026. neoporezivo do 4.800 € ako roditelj koristi olakšicu, inače do 12.000 € ([Croatia Week, 1. 12. 2025.](https://www.croatiaweek.com/croatia-raises-tax-free-thresholds-for-student-work-from-2026/)); odnosi se na studentski rad | Utječe li obrt na status uzdržavanog člana, roditeljevu olakšicu i zdravstveno osiguranje (HZZO, Porezna, referada). |
| **Ugovor s kupcem** | — | Opseg (broj Reelova, ispravci), rok otkaza, tko odgovara za sadržaj i autorska prava, ugovor o obradi podataka (GDPR), jer kupac šalje snimke osoba ([SECURITY.md](../architecture/SECURITY.md)). |
| **Uvjeti Anthropica** | Već upozoreno u [OTVARANJE.md](./OTVARANJE.md) | Smije li se Claude koristiti u usluzi koja se prodaje većem broju kupaca, i pod kojim uvjetima. |
| **Označavanje AI sadržaja** | AI akt, članak 50, od 2. 8. 2026. ([PRILIKE.md](./PRILIKE.md), upozorenja) | Treba li Reel s tekstom koji je napisao AI, a pregledao čovjek, oznaku. |

## Otvorena pitanja za Leona

1. Je li naručitelj spreman da Leon isti sustav nudi drugima, i pod kojim uvjetima (ekskluzivnost, provizija, ime)?
2. Koliko sati mjesečno Leon realno može dati kupcima uz studij?
3. Želi li Leon prodavati osobno (sastanci, pozivi) ili samo graditi? Model A traži prodaju.
4. Koja grana mu je najbliža za prve kupce: nekretnine, turizam ili ugostitelji, i u kojem gradu?
5. Koliko je naručitelj platio ili plaća, jer je to prva stvarna točka cijene?
6. Postoji li već obrt ili firma (BOORA.ai), ili se oblik tek bira?
