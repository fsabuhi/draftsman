---
name: debt-ledger
description: >
  List every `NOTE:` comment as a ledger of deliberate simplifications, and
  flag the ones that are due because the step they wait for is ticked on
  the shared `main`. One-shot report, changes nothing. Use in the consolidation pass
  (AGENTS.md), and for "list the NOTE comments", "what did we defer".
---

<!-- Adapted from github.com/DietrichGebert/ponytail (MIT); see THIRD-PARTY-NOTICES.md -->

Every deliberate simplification in this repository is marked with a `NOTE:`
comment naming its limit and, usually, when it goes away: a step id such as
`(step 3.1)`, a decision id such as `D-012`, or a condition such as "once the
worker exists". This collects them into one ledger so a deferral can't quietly
become permanent.

## Scan

From the repository root:

`git grep -nE '(#|//|/[*]) ?NOTE:'`

Each hit is one ledger row. The comment prefix keeps prose that merely
mentions the convention out of the ledger.

## Due or not

For each row, find what it waits for and check it:

- A step id: ticked in [the build order](../../../docs/product.md#build-order)
  on the shared `main` (AGENTS.md)? Then it is **due**.
- A platform step id, like `platform 2.1`: ticked in
  `docs/platform/build-order.md` on the shared `main`? Then it is **due**.
- A decision id: `accepted` in [decisions.md](../../../docs/decisions.md),
  or in `docs/platform/decisions.md` for a `P-` id? Then it is **due**.
- A condition ("once the worker exists"): true in the code now? Then it is
  **due**; say what you checked.
- Nothing named: tag it `no-trigger`. Those are the ones that silently rot.
- Otherwise: **waiting**.

## Output

Due rows first, then `no-trigger`, then waiting, grouped by file:

`<file>:<line>, <what was simplified>. waits for: <step, decision or condition>. <due | no-trigger | waiting>`

End with `<N> markers: <D> due, <T> with no trigger.` Nothing found:
`No NOTE: markers.`

## Boundaries

Reads and reports only, changes nothing. The consolidation pass resolves each
due row or, when it isn't a refactor, asks the team.
