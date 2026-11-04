---
description: Izgradi jednu ciglu od kraja do kraja i STANI za Leonov OK.
argument-hint: <oznaka ili opis cigle>
---

# /brick — jedna cigla, sigurno

**Cigla: $ARGUMENTS**

## 0 · Hladan početak

Pročitaj `CLAUDE.md`, `docs/plan/PLAN_V1.md`, tu ciglu i dokumente arhitekture koje dira.

## 1 · Ograniči i potvrdi PRIJE koda

Prepričaj ciglu, popiši datoteke i dokaz. Ako je opseg nejasan, pitaj Leona.

## 2 · Grana

Nikad `main`. Nova cigla je `feature/<slug>`.

## 3 · Gradi u kratkim dionicama

Rub koji prepoznaš odmah dobiva test.

## 4 · Dokaz

Preflight iz `CLAUDE.md` mora završiti s izlaznim kodom 0. Pokreni brane koje cigla dira. Izvještaj nosi stvaran izlaz.

## 5 · Dokumenti

Ažuriraj plan (cigla gotova), BACKLOG, ADR i SLJEDECA_SESIJA gdje je potrebno.

## 6 · Commit lokalno, pa STANI

`git add -- <putanje>`, nikad slijepi `git add -A`. Push traži Leonov izričit OK.

## 7 · Izvještaj

Što je isporučeno, koje datoteke, stvaran izlaz brana, što je ostalo otvoreno.
