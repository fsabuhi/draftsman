# Migrate: existing docs into the strict layout

The goal is the same knowledge with every fact in its one home, nothing lost, and every contradiction put to the user instead of settled by you.

## 1. Make it safe to undo

Check `git status`. If there are uncommitted changes, ask the user to commit or stash them first, or to let you work on a new branch. If there's no repository, ask before going on. The migration should land as one diff that the user can review or throw away.

## 2. List the sources

- List every document that holds product knowledge: everything under `docs/`, root markdown such as README.md, PRDs, specs, ADRs, design notes, and any file the user points at. Leave out code, generated files and vendored folders.
- Show the list to the user, then read every source in full.

## 3. Pull out the facts

Go source by source, top to bottom, and split each one into facts. A fact is one claim, rule, number, decision, idea, risk, refusal or open question. Keep each fact's source as `path:line`.

## 4. Place each fact

Use the table in `docs/AGENTS.md`:

- **A decision stated as made,** with or without a reason, becomes an accepted row. Keep the source's date if it has one, otherwise use today's. A proposal or a "maybe" becomes an open row. A choice that was later reversed becomes a superseded row, named by the row that replaced it.
- **A number the code reads** goes in a data file and is referenced by key.
- **A TODO, a TBD or a question** becomes an open decision, with your recommendation and what it blocks.
- **An idea no decision backs** goes in ideas.md, even when the old docs described it as a feature.
- **Anything the docs promised never to do** goes in never.md, citing a decision.
- **A fact that appears in several sources** goes in its one home; the other copies are duplicates.

## 5. Put contradictions to the user

When two sources disagree (two values, two rules, two names for one thing), don't pick one. Ask which is current. Until the user answers, record an open decision that quotes both versions and their sources, and write neither version as fact. Once the user picks, the losing version becomes a superseded row if it was a decision.

## 6. Write the new layout

- Copy the scaffold without overwriting, as in `references/create.md`, step 1, merging into any AGENTS.md, CLAUDE.md or pre-commit hook that already exists.
- When the existing AGENTS.md already has a build workflow, keep every rule of it that the scaffold's guide lacks, such as release steps, contract rules or stack checks, and add the scaffold's rules it lacks. Where the two disagree, such as how a step is claimed or merged, ask which one holds, and list the answer in the ledger.
- Write the docs from the placed facts.
- Move the old source files under `docs/` into `docs-archive/` with `git mv`, so the checker stops reading them and nothing is deleted yet. Leave sources outside `docs/`, such as README.md, where they are.
- Write the build order from what the sources say is done and what's left. Tick only the steps the code shows are done, and ask about anything unclear.

## 7. Write the ledger

Write `spec-migration.md` at the repository root:

| Source | Fact | Now in |
| --- | --- | --- |
| docs/PRD.md:12-14 | Free users get three analyses a day | docs/data/limits.yaml, key free.analyses_per_day |
| docs/notes.md:3 | Free users get five analyses a day | open D-007 (contradicts docs/PRD.md:12) |
| README.md:5 | The one-line pitch | duplicate of docs/product.md, Vision |

Every line of every source has to be covered. "Now in" is a home, "duplicate of <home>", an open decision, or "dropped: <reason>". A dropped fact needs the user's yes. End the ledger with what can be removed once the user approves: everything in `docs-archive/`, and the parts of README.md or other files outside `docs/` that now only restate the spec.

## 8. Audit and check

Run the audit in `references/audit.md`, then the checker until it passes. Point the user to the ledger, and ask them to approve it before `docs-archive/` is deleted.
