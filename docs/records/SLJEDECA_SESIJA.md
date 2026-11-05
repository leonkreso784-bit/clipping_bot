# Predaja za sljedeću sesiju

**Napisano:** 2026-11-05. Kad se sesija odradi, sadržaj se zamjenjuje novom predajom.

## Stanje

- C0, C1, C2 spojene u `main` i pushane (5. 11.).
- **C3 spojena u `main` i pushana (5. 11.)**: `db.py` + `schema.sql`, `select/` (prozor, `claude -p`, upute), `ingest.py`
  (yt-dlp, provjera kanala), `job.py` (koraci s nastavkom), `review.py` (neovisni pregled, `PREGLED.md`),
  `approve.py` + `cli.py` (`kreni`, `odobri`). Dokaz u `docs/plan/PLAN_V1.md` (red C3), odluke u ADR-012.
  Usput popravljen C2 kvar: `align_start` je mogao početi rez usred prve riječi (test dodan).
  Neovisni pregled (opus) našao 9 nalaza; popravljeni: provjera kanala uvijek po metapodacima videa (handle u URL-u
  bio je zaobilaznica), plan rezova spremljen u `radno/plan.json`, duplikati po hashu izvora i i u `odobri`,
  ponovni rez osvježava tekst i pregled, kopiranje u `mobitel/` preko `.part`, `.cmd` bez `claude.exe` je greška.
- Zlatni posao: `izlaz/20261105-caleb-hammer-df0e/PREGLED.md`; mapa `izlaz/mobitel/` (7 isječaka × 3 platforme).
- **Pauza do resetiranja tjednog limita (Leon, 5. 11.).**
- **Čeka Leona:** pravi žig u `kampanje/caleb-hammer/zig.png` (pregledač ga s pravom zove
  "bijela točka preko lica"); licence MPL-2.0 i `license = "MIT"` (BACKLOG „Čeka Leona"); računi za `racuni:`.
- Push na `origin` je trajno dopušten nakon `PREFLIGHT 0` (Leon, 5. 11.).

## Redoslijed na početku sesije

1. `git status` i `git log --oneline -5`.
2. Dalje po Leonu: ili kvaliteta isječaka iz nalaza pregleda (čitljivost `clean_lower`, kontekst na početku,
   memorija i int8 Parakeet; BACKLOG), ili plan za C4/C5 kad računi postoje i imaju tjedan ručne povijesti.
3. Jedna cigla odjednom, dokaz prije tvrdnje, stani za OK.

## Prompt za početak

> Pročitaj `docs/records/SLJEDECA_SESIJA.md` i nastavi od tamo. Prvo mi reci stanje i što trebaš od mene.
