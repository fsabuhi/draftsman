# Decisions

One row per decision, append-only. Never rewrite an accepted row: add a new one, set the old one to `superseded`, and name it under Supersedes. Status is `accepted`, `proposed` (written into the docs, waiting for the team's yes), `open` (not decided; the row carries a recommendation) or `superseded`. To resolve an open row, move it into the first table under the same id, with the answer under Decision and the reasoning under Why.

A recommendation in a proposed or open row doesn't authorize building that choice. The work it blocks, named under Needed by, waits; independent work continues.

## Accepted and proposed

| ID | Date | Status | Decision | Why | Supersedes |
| --- | --- | --- | --- | --- | --- |
| D-001 | 2026-10-20 | accepted | The spec lives in `docs/` in the draftsman layout: one home per fact, decisions in this file, and `scripts/check_spec.py` on every commit | Agents build from these docs, so the docs must never disagree with each other or leave a gap to guess at | |
| D-002 | 2026-10-20 | accepted | The backend is FastAPI with Postgres, and the app is Expo for iOS and Android | The team already ships Python and React | |
| D-003 | 2026-10-21 | accepted | Everyone signs in with a link sent to their email; there are no passwords | Parents forget passwords, and the link proves the email address | |
| D-004 | 2026-10-21 | accepted | The MVP is a free pilot: students don't pay, and the team pays tutors outside the app | We want proof that families book before we build payments | |
| D-005 | 2026-10-22 | accepted | Sessions happen only in the app's own video room, run on Daily | Every session leaves a record, which safeguarding needs | |

## Open

| ID | Date | Status | Question | Recommendation | Needed by |
| --- | --- | --- | --- | --- | --- |
| D-006 | 2026-10-22 | open | How are tutors paid once the pilot ends? | Stripe Connect, which handles payouts and UK tax reporting | `after-launch` |
