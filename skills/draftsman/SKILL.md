---
name: draftsman
description: Writes and enforces strict, agent-ready specs for spec-driven development, so coding agents (Claude Code, Codex, Cursor, Copilot, Gemini CLI and others) can build an app without guessing. Creates a spec from scratch for a new app or MVP by interviewing the user; migrates existing docs (PRDs, READMEs, notes, loose markdown) into the strict layout without losing a fact; audits a spec for gaps, contradictions and missing decisions, turning each into a question or an open decision instead of a guess. Installs a checker that fails the commit while the spec has a gap. Use it whenever someone wants to plan or spec an app or MVP for AI agents to build, set up spec-driven development, write a PRD or build plan that agents can follow, make their docs agent-ready, restructure a docs folder, or find what's missing or contradictory in a spec, even if they never say "spec".
---

# Draftsman

A draftsman draws the plans that builders follow exactly; here the builders are coding agents. Draftsman writes a spec where every fact has one home, nothing is left vague, and every unknown is a recorded decision, and it installs a checker that fails the commit when any of that stops being true. Agents build exactly what a spec says, with confidence, so every gap left in it turns into a guess that ships.

## What it produces

```
AGENTS.md              how agents build from the spec: pick a step, build it, review it, merge it, tick it
CLAUDE.md              @AGENTS.md, so Claude Code reads the same guide as every other agent
.githooks/pre-commit   runs the checker before every commit
.agents/skills/        review-step, audit-milestone and debt-ledger, which the build workflow uses
THIRD-PARTY-NOTICES.md the licence of the work those skills adapt
scripts/check_spec.py  the checker: plain Python 3.9+ (PyYAML only for YAML data files)
docs/
  AGENTS.md            the rules and formats for everything below (read it before writing)
  README.md            entry point, with a generated feature index
  product.md           vision, phases and gates, and the build order
  decisions.md         the project's decisions: accepted, proposed, open or superseded
  features/<slug>.md   one per feature: Behavior (with Done when) and Implementation
  shared/<topic>.md    facts two or more features use: architecture, data model, errors
  data/<name>.yaml     numbers the code reads, referenced by key from the prose
  never.md             what will never be built, and why
  ideas.md             parked ideas, one line each
  risks.md             risks and their guardrails
```

The skeleton is in `assets/scaffold/` in this skill's folder, with a `<<fill: …>>` marker wherever the project's own content goes; the checker fails until every marker is gone. `assets/feature.md` and `assets/errors.md` are templates for a feature file and the error-code registry. The formats themselves are defined once, in `assets/scaffold/docs/AGENTS.md`. Read that file before writing any spec content, because everything you write follows it.

## Rules this skill never bends

1. **Never invent a fact.** What the user said, what the docs say, what the code does and the outside rules the product must follow (an app store's guidelines, a law) are facts. Everything else is a recommendation, and recommendations go only in decision rows. A guess written as a fact becomes shipped behavior that nobody chose.
2. **Close every gap one of three ways:** derive it from the docs, the code or an outside rule and name the source where you write it, get the answer from the user, or record an `open` decision with your recommendation and what it blocks. Once a gap is an open decision, nothing else in the spec may answer it: write only what's true whatever the answer, and link the decision. Never leave placeholder text, and never drop a gap silently; an unrecorded gap comes back later as an agent's guess.
3. **Accepted means the user said yes.** Mark a decision `accepted` only when the user stated or confirmed it. Your recommendations go in `open` rows, or in `proposed` rows when the user asks you to draft decisions for them to approve.
4. **One home per fact.** Before writing a fact, find its home in the table in `docs/AGENTS.md`. If the fact already exists, link to it instead of restating it. When you move a fact, delete the old copy.
5. **Lose nothing when migrating.** Every fact in the old docs lands in a home, or is listed as an exact duplicate. Nothing else is dropped without the user's yes, and old files are archived, not deleted, until the user approves the ledger.
6. **The checker decides when you're done.** `uv run scripts/check_spec.py` has to pass in the final state. Fix the docs, never the checker, and never move or rename files to get around it.
7. **Docs only.** Don't change application code, configuration or dependencies. Read code only as evidence for the spec. The scaffold's guides, skills and hook are part of the spec setup, not application code.
8. **Leave the user in control of git.** Start from a clean working tree or a new branch, so the result is one diff the user can review. If there are uncommitted changes and nobody can be asked, go on, and name those files in your report. Don't commit unless the user asks.

## Pick the mode

| What the repository has | Mode | Follow |
| --- | --- | --- |
| No product docs | Create | `references/create.md` |
| Docs of any other shape: a docs folder, a PRD, product sections in a README, notes | Migrate | `references/migrate.md` |
| A draftsman spec whose `docs/product.md` still has `<<fill: …>>` markers, such as a starter template with its platform already specified | Create, on that base | `references/create.md` |
| A draftsman spec with no `<<fill: …>>` markers left in `docs/product.md` | Audit | `references/audit.md` |

Tell the user which mode you picked and why, in one line. If they asked for something specific, such as "just audit it", do that instead. Asking to improve or refactor a draftsman spec means an audit, because the audit fixes what it finds. Every mode ends with the audit and the checker.

## Asking the user

- Ask in batches of at most five questions, the most blocking first.
- Give every question your recommendation and its reason, so that "yes" is a complete answer.
- Never decide for the user, and that includes structure: whether to split a step, which steps a decision holds, or what a milestone contains. Recommend, then ask.
- Ask only what the user alone can know. If the docs or the code answer it, derive the answer and cite where it came from.
- "I don't know", "later", or no answer at all becomes an `open` decision with your recommendation and the step, milestone or phase it blocks.
- If the user says they can't answer now, or nobody can be asked (an unattended run), don't stop. Record every question as an open decision, finish everything else, and list those decisions in your report.

## Writing the spec

- Write short, plain sentences in the present tense ("The server picks the set"), with one term per concept, used the same way everywhere.
- A number the code reads goes in `docs/data/`, and the prose names its key. Numbers the code never reads, such as gate bars and targets, stay in prose in their one home.
- Write each rule so that a test could check it: who does what, under which condition, with which result, and what happens when it fails.

## The checker

- Once the scaffold is copied, run `uv run scripts/check_spec.py` from the repository root; plain `python3` works once PyYAML is installed or when no data file is YAML.
- Before that (during a migration or an audit of a repository without it), run this skill's copy against the repository: `uv run <this skill's folder>/assets/scaffold/scripts/check_spec.py --root <repo>`.
- YAML data files need PyYAML: use `uv run scripts/check_spec.py`, which installs it, or `pip install pyyaml`. If nothing can be installed, say so in your report; never skip the check without saying so.
- Fix every problem it reports in the docs. `--fix` only regenerates the feature index in `docs/README.md`.

## Finishing

1. The checker passes.
2. Offer two things, and do them only if the user agrees: turning on the hook (`git config core.hooksPath .githooks`, a local git setting) and, for a GitHub repository, copying `assets/spec-check.yml` from this skill to `.github/workflows/spec.yml`.
3. Report in this shape:

```markdown
## Spec <created | migrated | audited>: <the checker's summary line>

### What changed
<each file created, moved or edited, one line each>

### Gaps, and how each was closed
| # | Where | Gap | Closed by |
<derived from <source> | answered by you | open D-### | fixed for the checker>

### Decisions waiting for you
<each open decision: the question, your recommendation, and what it blocks>

### What agents can build next
<the first step each build-order list can take now, or what blocks it>
```

After a migration, add a last section pointing to the ledger in `spec-migration.md`, and ask the user to approve it before `docs-archive/` is deleted.
