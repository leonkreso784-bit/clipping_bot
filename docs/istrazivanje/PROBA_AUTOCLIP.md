# Proba: autoclip na Caleb Hammer videu (4. 11. 2026.)

> Jednokratna proba (spike), ne dio proizvoda. Cilj: izmjeriti koliko traje obrada jednog dugog videa na
> Leonovu računalu (CPU, bez grafičke) i vidjeti kakvu kvalitetu daje gotov alat otvorenog koda
> [artbyjazi/autoclip](https://github.com/artbyjazi/autoclip) (MIT), uz to da **Claude Code bira isječke**, a ne plaćeni API.

## Što je napravljeno

1. Kloniran autoclip u scratchpad (izvan repozitorija), instaliran u vlastiti `uv` venv (Python 3.11).
2. Napisan pomoćni `driver.py` koji autoclip pokreće korak po korak:
   - `prepare`: skidanje videa, izdvajanje zvuka, prijepis Whisperom, popis tišina, ispis prijepisa s indeksom uz svaku riječ;
   - `finish`: prima `candidates.json` (indeksi prve i zadnje riječi, naslov, udica, ocjena), autoclip iz toga računa vremena
     i pomiče rezove na granice rečenica/tišina, pa radi kadriranje, titlove i izvoz.
3. Claude je u sesiji pročitao cijeli prijepis (17.216 riječi) i vratio 9 kandidata. Nijedan API poziv po isječku.
4. Izvezeno 9 isječaka 9:16 s karaoke titlovima.

Izvor: Caleb Hammer, Financial Audit, `https://www.youtube.com/watch?v=JvLklMRThYs`, 89 min 56 s, 1080p AV1, 651 MB.
Video je iz službenog briefa kampanje na Clipping.net (dopušten izvor).

## Gdje su datoteke

Sve je u `izlaz/proba-2026-11-04-caleb-hammer/` (mapa `izlaz/` je u `.gitignore`, ništa od ovoga ne ide u git):

| mapa | sadržaj |
|---|---|
| `isjecci/` | 9 gotovih MP4 datoteka (1080×1920, H.264, 30 fps, AAC, oko 5 Mbit/s, −14 LUFS) |
| `radno/candidates.json` | što je Claude izabrao (indeksi riječi, naslov, udica, ocjena, obrazloženje) |
| `radno/prijepis_s_indeksima.txt` | cijeli prijepis u obliku `[i]riječ` koji je Claude čitao |
| `radno/driver.py` | pomoćna skripta probe (jednokratna, ne ulazi u proizvod) |
| `radno/state.json` | izmjerena trajanja |
| `radno/finish.log` | dnevnik kadriranja i izvoza |
| `radno/primjer_titlova.ass` | generirani titlovi za jedan isječak (format ASS, font Anton) |
| `radno/slicica_caleb.jpg`, `radno/slicica_gosca.jpg` | sličice iz isječaka: kadar na Calebu i kadar na gošći |

Radne datoteke autoclipa (izvorni video, `audio.wav`, sličice, baza) ostaju u scratchpadu dok Leon ne kaže da se brišu.

## Izmjereno trajanje

Računalo: Intel 12 jezgri, 16 GB RAM, integrirana grafika, sve na CPU-u.

| korak | trajanje | napomena |
|---|---|---|
| skidanje (yt-dlp, 1080p) | 66 s | |
| zvuk + sličice svakih 5 s | 477 s | |
| **prijepis** (faster-whisper, `large-v3-turbo`, int8) | **6.209 s = 103 min** | sporije od stvarnog vremena; koristio samo 1–4 jezgre od 12 |
| tišine | 2 s | |
| kadriranje + titlovi + izvoz, 9 isječaka | 1.121 s = 19 min | oko 2 min po isječku, uključuje MediaPipe praćenje lica |
| **ukupno** | **oko 2 h 10 min** | za 90 minuta izvornog videa |

Vrijeme koje je Claude trošio na čitanje prijepisa i izbor nije mjereno (jedna poruka u sesiji).

## Izabrani isječci

| # | naslov | vrijeme u izvoru | trajanje | ocjena |
|---|---|---|---|---|
| 1 | Rather go broke than show a man her finances | 1155.8–1209.7 | 54 s | 94 |
| 2 | $15,300 painting = seven months of child support | 1506.1–1593.2 | 87 s | 93 |
| 3 | "We grew up middle class" (inherited two homes) | 303.7–339.9 | 36 s | 92 |
| 4 | Retire at 50, die at 52 | 411.8–485.6 | 74 s | 90 |
| 5 | $3,000 a month, three kids, a house on the beach | 137.3–191.9 | 55 s | 88 |
| 6 | Nearly $1M gone in nine years | 2227.3–2265.8 | 38 s | 87 |
| 7 | "I thought student loans were good debt" | 4212.0–4283.3 | 71 s | 86 |
| 8 | "He gets a raise for inflation, why don't I?" | 691.5–721.9 | 30 s | 85 |
| 9 | Bought herself a Rolex to see her ex's face | 2674.3–2697.6 | 23 s | 84 |

Kriteriji izbora (po briefu kampanje): udica u prve 3 sekunde, zaokružena priča bez konteksta epizode, konkretne brojke,
bez ismijavanja gošće izvan onoga što je sama rekla. Isječak 7 ima najmanje psovki i najsigurniji je za Instagram.

## Što radi dobro

- **Kadriranje.** Autoclip prati lice govornika i prebacuje kadar između Caleba i gošće; na sličicama nema odsječenih glava ni drhtanja.
- **Titlovi.** Karaoke stil `bold_pop` (font Anton, velika slova, aktivna riječ žuta i uvećana), u donjoj trećini, ne preklapa lice.
  Psovke su već cenzurirane zvjezdicama jer ih Whisper tako prepisuje.
- **Rezovi.** Autoclip od indeksa riječi sam pomiče početak i kraj na granicu rečenice ili tišine; nijedan isječak ne počinje usred riječi.
- **Izbor bez API-ja.** Potvrđeno da ADR-005 (Claude vraća samo ID-eve, program računa vremena) radi u praksi s cijelim prijepisom od 90 minuta.
- **Izvoz.** Jedan prolaz FFmpega po isječku, ispravan format za sve četiri platforme.

## Što ne valja ili nedostaje

1. **Whisper je usko grlo.** 103 minute prijepisa za 90 minuta videa nije održivo za više videa dnevno. Uzrok je dvostruk: model je
   velik za CPU, a autoclip ne zadaje broj niti pa je stroj uglavnom prazan. Rješenje za plan: NVIDIA Parakeet TDT 0.6B v3 (CC-BY-4.0,
   ONNX na CPU-u), očekivano ispod 10 minuta za isti video; mjeriti u prvoj cigli.
2. **Nema vodenog žiga ni obveznog teksta na ekranu.** Caleb Hammer brief traži centrirani žig; druge kampanje traže određeni tekst.
   Autoclip to nema; naš alat mora dodati sloj za grafiku po profilu kampanje.
3. **Nema oznake plaćene suradnje ni opisa/naslova za objavu.** Ide u fazu objave, ne u rezanje.
4. **Nema baze stanja.** Autoclip ima SQLite za svoje poslove, ali ne prati status isječka po kampanji i platformi
   (izrezan → pregledan → objavljen → prijavljen → plaćen).
5. **Razlučivost skidanja ograničena na 1080p**, što je u redu za 9:16 izrez, ali kadar s jednim licem koristi manje od pola piksela.

## Zaključak za plan

Lanac "program reže, Claude bira" je potvrđen. U arhitekturu ulazi: Parakeet umjesto Whispera, sloj za žig i tekst po profilu
kampanje, vlastita baza stanja i faza objave. Autoclipov kod za kadriranje i titlove (MIT) je dobar uzor ili izravna ovisnost;
odluka o tome ide u ADR. Ništa iz probe ne ulazi u proizvod bez nove cigle.

Otvoreno za Leona nakon pregleda isječaka: jesu li izabrani trenuci dobri, odgovara li stil titlova, smeta li skakanje kadra između
dvoje govornika.
