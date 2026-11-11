---
decisions: []
---

# Product

## Vision

**One line:** <<fill: what the product does, for whom, in one sentence>>

### The problem

<<fill: the problem the product solves, what people do about it today, and why that falls short>>

### Who it's for

<<fill: the first audience, and who it's not for>>

### Principles

<<fill: three to seven rules every feature follows, each with its reason>>

## Roadmap

### Phases and gates

A phase starts only when the gate before it is met.

| Phase | What ships | Gate to move on |
| --- | --- | --- |
| `mvp` | <<fill: the features in the first release>> | <<fill: the measurable bar that proves the MVP worked>> |
| `after-launch` | <<fill: what comes once the MVP gate is met>> | <<fill: its measurable bar>> |
| `later` | <<fill: what waits for scale or demand>> | None |

### Build order

Each milestone lists its steps by who works them, and a step that needs another names it with `(after …)`. Every milestone ends with a team step that confirms its done-when, and the next milestone starts once it's ticked. How agents pick and build steps is in [AGENTS.md](../AGENTS.md#before-you-write-code); the format is in [the docs rules](AGENTS.md#build-order).

#### 1. <<fill: the first milestone's name>>

Done when <<fill: what a person can do once this milestone is built>>.

<<fill: one list per stream of work, each step in the format from docs/AGENTS.md, then the Team list's own steps above its confirm step, which keeps the milestone's last id>>

Team:

- [ ] **1.1** Confirm milestone 1's done-when (team)
  - Done when: the team confirms the milestone's done-when holds.
