---
description: Analiziraj stanje i preporuči sljedeću ciglu. Samo čitanje.
allowed-tools: Read, Grep, Glob, Bash
---

# /next — što gradimo sljedeće

Cilj je jedna jasna preporuka. Ništa ne mijenjaj.

1. Pročitaj `CLAUDE.md`, `docs/plan/PLAN_V1.md` i `docs/records/BACKLOG.md`.
2. Pogledaj `git status --short` i `git log --oneline -8`.
3. Prvo upaljeni signal odlučuje:

| signal | preporuka |
|---|---|
| nedovršen rad | dovrši ga |
| usred cigle | nastavi nju |
| otvoren važan bug | popravi ga |
| cigla čeka Leona | reci što točno nedostaje |
| inače | sljedeća cigla iz plana |

**Izlaz:** stanje, jedna preporuka s naredbom i što dolazi nakon toga.
