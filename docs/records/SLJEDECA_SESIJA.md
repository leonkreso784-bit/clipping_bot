# Predaja za sljedeću sesiju

**Napisano:** 2026-11-04. Kad se sesija odradi, sadržaj se zamjenjuje novom predajom.

## Stanje

Repozitorij je tek postavljen: `CLAUDE.md`, plan (nacrt), odluke ADR-001 do ADR-006, backlog i snimke
istraživanja. Koda nema.

## Redoslijed na početku sesije

1. `git status` i `git log --oneline -5`.
2. Pročitaj `docs/plan/PLAN_V1.md` i `docs/records/BACKLOG.md` (odjeljak „Čeka Leona").
3. Pitaj Leona za OK plana, prvi video za probu i jezik isječaka.
4. Ako Leon traži još istraživanja ili dorade plana, radi ih kroz agente (`opus`), rezultate upiši u
   `docs/istrazivanje/` ili plan, pa STANI za OK.
5. Tek nakon OK-a: `/brick K0`.

## Prompt za početak

> Pročitaj `docs/records/SLJEDECA_SESIJA.md` i nastavi od tamo. Prvo mi reci stanje i što trebaš od mene.
