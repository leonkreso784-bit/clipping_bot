# Profili kampanja

Jedna datoteka po kampanji: `kampanje/<slug>.yaml`, napisana iz briefa (ključevi iz dizajna §5). Učitava je
`clipping.profile.load_profile`, koja odbija profil s porukom na hrvatskom ako nešto ne valja.

Pravila koja program provjerava:

- `platforme` smije sadržavati samo `tiktok`, `instagram`, `x`, `youtube`; alat objavljuje samo tamo.
- `racuni` smije imati ključeve samo iz `platforme` (jedan račun po kreatoru i platformi, ADR-011).
- `grafika.zig.datoteka` mora postojati (putanja relativna na korijen repozitorija). Žig se drži u
  `kampanje/<slug>/zig.png`; ta mapa je izvan gita.
- `pravila_sadrzaja.stil_titlova` je neprazan popis stilova iz `clipping.captions.PRESETS`
  (`bold_pop`, `clean_lower`, `boxed`); rotiraju se po isječku.
- `pravila_sadrzaja.psovke.zvuk` smije biti samo `nista`; `beep` se ne gradi u V1.

Uzorak s komentarima: `caleb-hammer.yaml`. Testni profil: `tests/fixtures/kampanja_test.yaml`.
