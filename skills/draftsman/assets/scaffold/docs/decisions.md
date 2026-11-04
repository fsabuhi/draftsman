# Decisions

One row per decision, append-only. Never rewrite an accepted row: add a new one, set the old one to `superseded`, and name it under Supersedes. Status is `accepted`, `proposed` (written into the docs, waiting for the team's yes), `open` (not decided; the row carries a recommendation) or `superseded`. To resolve an open row, move it into the first table under the same id, with the answer under Decision and the reasoning under Why.

A recommendation in a proposed or open row doesn't authorize building that choice. The work it blocks, named under Needed by, waits; independent work continues.

## Accepted and proposed

| ID | Date | Status | Decision | Why | Supersedes |
| --- | --- | --- | --- | --- | --- |
| D-001 | <<fill: today's date, YYYY-MM-DD>> | accepted | The spec lives in `docs/` in the draftsman layout: one home per fact, decisions in this file, and `scripts/check_spec.py` on every commit | Agents build from these docs, so the docs must never disagree with each other or leave a gap to guess at | |

## Open

| ID | Date | Status | Question | Recommendation | Needed by |
| --- | --- | --- | --- | --- | --- |
