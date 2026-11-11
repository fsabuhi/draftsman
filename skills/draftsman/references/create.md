# Create: a spec from scratch

The goal is a spec agents can start building from today: the MVP fully specified, the later phases sketched, and every unknown recorded where it blocks work.

## 1. Set up

1. Find the repository root (`git rev-parse --show-toplevel`). If there's no repository, ask whether to create one; if nobody can be asked, work in the current folder and say so in your report.
2. Copy `assets/scaffold/` from this skill's folder into the root, without overwriting anything. On macOS and Linux:

   ```sh
   cp -Rn <this skill's folder>/assets/scaffold/. <repo>/
   ```

   For each file that already existed, merge the scaffold's content into it instead, and tell the user what you merged. CLAUDE.md must contain the line `@AGENTS.md`, an existing pre-commit hook gets the spec check added to it, and an existing THIRD-PARTY-NOTICES.md gets the scaffold's entry. Keep `.githooks/pre-commit` executable (`chmod +x`), since git skips a hook that isn't.
   Claude Code reads skills from `.claude/skills/`, so link each skill there: `mkdir -p .claude/skills`, then `ln -s ../../.agents/skills/<name> .claude/skills/<name>` for each folder in `.agents/skills/`.
3. Read the copied `docs/AGENTS.md`. It is the format everything you write follows.
4. If the repository already has code, read enough of it to know the stack, the folders, and any endpoints, tables and limits that already exist. Those are facts: cite them rather than asking about them.
5. **On a base.** When the repository already holds a draftsman spec with `<<fill: …>>` markers left, such as a starter template, its filled parts are facts: the accepted decisions, the shared docs, the data files, the guides and any ticked build steps. Read all of them. Don't ask what they answer, don't rewrite them, and write only what the markers ask for and what the new product adds.

## 2. Interview

Take every answer the user's request and the base already give, and ask only what's missing. On a base, round 4 is usually answered already. Ask in batches of up to five questions, each with your recommendation, following "Asking the user" in SKILL.md.

**Round 1: the product**
1. In one sentence, what does it do, and for whom?
2. What problem does it solve, what do people do about it today, and why does that fall short?
3. Who is it for first, and who isn't it for?
4. What must the MVP do to be worth shipping? Name the features.
5. How will you know the MVP worked? A number you can measure, and by when.

**Round 2: each MVP feature** (two or three features per batch)
- What does the user do, step by step, and what do they see?
- What are the rules: limits, who may do what, what happens when something fails?
- How will you know it's done?
- What's explicitly out of scope?

**Round 3: fences**
- What comes right after the MVP, and what waits until later?
- What will you never build, and why?
- What could sink the product?

**Round 4: how it's built**
- Which apps or folders (backend, web, mobile, CLI, workers), and which stack for each?
- Where does it run? How do users sign in? How do they pay? Which outside services does it call?
- What are the main things it stores?
- Which numbers will the code read: free limits, caps, prices, timeouts?

**Round 5: how you'll work**
- How many people and agents build at once, and on what? That sets the build-order lists.
- How many build steps may the MVP take? A budget keeps the MVP small enough to ship when you need it. Record the answer as an accepted decision.
- Who confirms that a milestone is done?
- Is there a date the MVP must ship by?

Stack and provider questions are where your recommendation matters most. Recommend the well-documented option the team already knows, and say why. An unanswered one is still an open decision, never a choice you make for them.

## 3. Draft

Write in this order, since each part leans on the ones before it:

1. **decisions.md.** D-001 is already there. Add a row for every choice the user made (`accepted`, with their reason) and for every question they didn't answer (`open`, with your recommendation and what it blocks). Number rows in the order you add them, and fill in Needed by once the build order exists.
2. **product.md, Vision:** the one line, the problem, who it's for, and the principles.
3. **product.md, Phases and gates:** usually `mvp`, `after-launch` and `later`, each with a measurable gate.
4. **Features.** Write one file per MVP feature from `assets/feature.md`, fully specified. Later-phase features get Behavior and Done when, plus any implementation notes already known. Link every feature from the roadmap.
5. **Shared docs,** only for facts that two or more features use: architecture and stack, data model, API conventions, auth, and error codes (from `assets/errors.md`). Each fact goes in exactly one of them, and features link to it.
6. **Data files** for every number the code reads, in `docs/data/`, referenced by key from the prose.
7. **never.md, ideas.md and risks.md.**
8. **The build order,** last, from everything above:
   - Milestone 1 is the foundation: the repository, CI running the checks, the empty apps and a first deploy, so every later milestone ships somewhere real.
   - Every later milestone ends with something a person can try end to end, and its done-when says what.
   - Bring in the hard parts one at a time, the riskiest early.
   - Make one list per stream of work, such as Backend, Client and Team. A step that needs another names it with `(after …)`.
   - End each milestone's Team list with `Confirm milestone <n>'s done-when (team)`, under the milestone's last id.
   - Each step is one sentence of scope, small enough for one agent session, with a `Done when:` that a test or a command proves. A `(team)` step's done-when names the outcome and who confirms it.
   - Work only people can do (accounts and keys, store listings, legal text, content, reviews, paid services) is a `(team)` step, placed before the step that needs it.
   - A step that an open decision blocks waits for it: name the step under the decision's Needed by, or make it come `(after …)` a step that's named. When only part of a step is blocked, ask the user whether to split off the unblocked part.
   - On a base, keep its milestones and ticked steps as they are, and number new milestones after them.
   - When the MVP has more unticked agent steps than the budget decision allows, don't cut on your own. List the features that could move to `after-launch`, the least needed first, with what each move saves, and ask.
9. Fill in the remaining `<<fill: …>>` markers in AGENTS.md, docs/AGENTS.md and docs/README.md.

## 4. Audit and check

Run the audit in `references/audit.md` on the draft, close every finding, then run the checker until it passes. A new spec has gaps wherever the interview was thin, and the audit is where they become questions or open decisions instead of an agent's guesses later on.
