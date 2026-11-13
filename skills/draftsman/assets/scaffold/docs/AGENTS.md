# Docs rules for agents

Read this before you change anything in `docs/`. How to build from these docs is in [the root AGENTS.md](../AGENTS.md).

These docs are the spec the code is built from, so an agent building from them should never have to guess. That takes three things: every fact has one home, nothing is left vague, and every unknown is a recorded decision. `scripts/check_spec.py` enforces the mechanical part on every commit; the rest is up to whoever writes the docs.

## Where each kind of fact lives

| You have | It goes in |
| --- | --- |
| What the product is, who it's for, and its principles | `docs/product.md`, under Vision |
| Phases, gates, milestones and build steps | `docs/product.md`, under Roadmap |
| A decision: accepted, proposed, open or superseded | `docs/decisions.md`, as a new row |
| What a feature does for the user: its rules, done-when and what's out of scope | `docs/features/<slug>.md`, under Behavior |
| How a feature is built: the interfaces it owns, the data it reads and writes, its jobs and limits | `docs/features/<slug>.md`, under Implementation |
| Anything two or more features use | `docs/shared/<topic>.md` |
| A number or list the code reads: limits, caps, prices it charges, formula parameters | `docs/data/<name>.yaml`, `.toml` or `.json` |
| An error code | `docs/shared/errors.md` |
| A decision, error code, shared fact or build step that a template gives every project built from it | `docs/platform/`, changed only in the template ([the platform layer](#the-platform-layer)) |
| Something we refuse to build | `docs/never.md` |
| An idea nobody has decided on | `docs/ideas.md`, one line |
| A risk and its guardrail | `docs/risks.md` |
| The market and competitors, how the product finds users, and pricing strategy | `docs/business.md`, when the team keeps these in the repository |
| Which existing app each screen's layout borrows from, with a link to its screens | `docs/shared/design.md`, when the product has screens |
| How the code in a folder is written | `<folder>/AGENTS.md` |
| The build workflow and the rules for the whole repository | `AGENTS.md` |
<<fill: add a row for each shared doc this project has, such as the data model or the API conventions, and delete the error-code row if the project has no error codes>>

## Rules

1. **One home per fact.** Anything else that needs the fact links to its home. A summary never restates a value, a list or a rule.
2. **Numbers the code reads live in `docs/data/`.** Prose names the file and the key instead of the value, and the checker resolves every such reference:

   ```markdown
   Free users get `limits.yaml → free.plans_per_week` plans a week.
   ```

   Numbers the code never reads, such as targets, gate bars and prices quoted in prose, stay in prose in their one home. A value means one thing: never let one value, such as `null`, stand for both "unlimited" and "not decided yet".
3. **Decisions are append-only.** Never rewrite an accepted row: add a new one, set the old one to `superseded`, and name it in the new row's Supersedes cell. Other docs state only the current answer and cite the decisions behind it, never a superseded one.
4. **Unknowns are `open` decisions, never placeholder text.** Each open row carries a recommendation and, under Needed by, the first work that waits for the answer: a step (`Step 2.3`), a milestone (`Milestone 4`, so none of its steps start) or a phase, written as its backticked slug (`after-launch`, which doesn't start until then). The checker fails on `TBD`, `TODO`, `etc.`, `and so on` and other placeholders.
5. **Accepted means the team said yes.** Agents never decide: they add `open` rows, and `proposed` rows when the team asks for a draft; only the team accepts one. A recommendation in a proposed or open row doesn't authorize building it.
6. **New ideas start in `docs/ideas.md`.** A feature file is created only when a decision promotes the idea.
7. **Leave nothing to guess.**
   - A list names every member.
   - An interface states its whole contract where it's defined: its inputs, every possible result, its errors and its limits.
   - A rule that picks, computes, ranks or matches says how: its inputs, the rule, how ties break, and what happens when there's nothing to pick.
   - A counter says what it counts, when it's spent, when it resets and what happens at the limit.
   - A state lists every value it can take and what moves it from one to the next.
8. **Run the check after every change:** `uv run scripts/check_spec.py` (plain `python3` works once PyYAML is installed or when no data file is YAML), and fix every problem it reports. `--fix` regenerates the feature index in `docs/README.md`. Never edit the checker to make a problem go away.

## Feature files

Each feature lives in `docs/features/<slug>.md`, named with a lowercase-kebab-case slug, and starts with exactly this frontmatter:

```yaml
---
ships_in: mvp
decisions: [D-004, D-012]
---
```

`ships_in` is the earliest phase the feature ships in, one of the phases in [the roadmap](product.md#phases-and-gates). A feature's `ships_in` stays its schedule until a decision changes it, whatever an open row recommends. `decisions` lists the decisions the feature relies on, or `[]`. The title is the `# H1`, followed by two sections and no others:

- `## Behavior`: what the user experiences and the rules, then a `### Done when` list and an optional `### Out of scope`.
- `## Implementation`: the interfaces the feature owns, the data it reads and writes, its jobs and its limits. Every feature in the first phase has one; later features may hold only notes.

Order and progress live in the build order and history lives in git, so feature files repeat neither.

## Decisions

`docs/decisions.md` holds two tables with these headers:

```markdown
| ID | Date | Status | Decision | Why | Supersedes |
| ID | Date | Status | Question | Recommendation | Needed by |
```

The first holds `accepted`, `proposed` and `superseded` rows; the second holds `open` rows. An id here is `D-` and three digits, never reused; platform decisions have `P-` ids ([the platform layer](#the-platform-layer)). To resolve an open row, move it to the first table under the same id, with the answer under Decision and the reasoning under Why.

## Build order

The build order in `docs/product.md` is a list of milestones. Each milestone says what a person can do once it's built, then lists its steps by who works them:

```markdown
#### 2. First practice

Done when a tester on staging can play a quiz set.

Backend:

- [ ] **2.1** Quiz sessions: server-picked sets and the daily counter (after 1.4)
  - Done when: API tests show a set is picked, answered and counted once a day.

Client:

- [ ] **2.2** The quiz screen (after 2.1)
  - Done when: a screen test plays a set against a mocked API.

Team:

- [ ] **2.3** Review and publish the first 50 quiz items (team)
  - Done when: the content lead confirms 50 items are published.
- [ ] **2.4** Confirm milestone 2's done-when (team)
  - Done when: the team confirms the milestone's done-when holds.
```

- Milestones are numbered from 1. A step id is `<milestone>.<n>` and unique; a split step adds a letter, like `2.1a`.
- Every unticked step has a `Done when:` line. An agent's step names what a test or a command proves; a `(team)` step names the outcome and who confirms it.
- `(after 2.1)` names the steps that must be ticked first; it can share the parentheses with a link or decision ids, separated by `;`. `(team)` marks work only people can do, such as writing or reviewing content, creating accounts and keys, and legal text; agents never take those steps.
- Each list is named for whoever works it, and one agent works one list at a time.
- Every milestone's Team list ends with `Confirm milestone <n>'s done-when (team)`. The team ticks it once the milestone's done-when holds, and agents work only in the earliest milestone whose confirm step is unticked.
- A step that names an open decision waits for it: the decision's Needed by names the step, or the step comes `(after …)` one that it names. A step never builds on a `proposed` row. When only part of a step is blocked, the team may split it, and the unblocked part becomes its own step; agents ask, never split on their own.

## Error codes

When the project has error codes of its own, `docs/shared/errors.md` is their one home: a single table that starts `| Code | Status |`. With [a platform layer](#the-platform-layer), its codes are in `docs/platform/errors.md`, in the same format, and no code is in both tables. Other docs name a code with its status, and the checker matches each mention against the tables:

```markdown
Past the cap, the request fails with `limit_reached` (429).
```

## The platform layer

A project built from a template keeps the template's own decisions, shared docs and build order in `docs/platform/`. Every project built from the template gets the same copy, so only the template changes the folder. The project never edits it, and keeps its own decisions and docs where the rest of this guide puts them. Without the folder, this section doesn't apply.

- `docs/platform/decisions.md` holds the two tables of [the decisions](#decisions), under the same headings. Its ids are `P-` and three digits, never reused. An open row names under Needed by the step or milestone of the platform's build order that it blocks; the platform has no phases.
- `docs/platform/build-order.md` is the platform's build order: a `# Build order` heading, a short introduction, then only its milestones, headed `## <n>. <name>`, each in the format of [the build order](#build-order). The template's repository builds its steps, and this project's agents never take one. A step of this project that needs one waits for it with `platform` before each platform id, as in `(after 3.4, platform 2.1, platform 2.2)`; it's done once it's ticked in this repository's copy, which the template's updates bring. A ticked step never comes after an unticked platform step.
- An open `P-` row holds back only platform steps, so a step of this project that needs its answer comes `(after platform …)` an unticked platform step the row holds. Like any proposed row, a proposed `P-` row is built on only once the template's team accepts it.
- `docs/platform/errors.md` holds the platform's error codes, in the format of [the error codes](#error-codes).
- Every other file in `docs/platform/` is a shared doc, and follows the rules a file in `docs/shared/` follows.
- The project's docs, features and frontmatter may cite `P-` ids, and the checker resolves them as it does `D-` ids.
- Supersedes works across the two decision files: a `superseded` row in either is named under Supersedes by a row in either. A `P-` row may name `D-` rows. One this project has is marked `superseded`; one it doesn't have is history from the project the platform came from. A `D-` row never names a `P-` row, since a project can't replace a platform decision.
- The folder stands on its own. Nothing in it cites a `D-` id, names an error code from `docs/shared/errors.md`, or links outside `docs/platform/` except to files in `docs/data/`. The one exception is the Supersedes cells of `docs/platform/decisions.md`, which may name `D-` rows.
