# Draftsman

Strict, agent-ready specs for spec-driven development. Draftsman is an [Agent Skill](https://agentskills.io) for Claude Code, Codex, Copilot, Gemini CLI, Cursor and any other agent that reads skills.

Coding agents build exactly what the spec says, and they do it confidently. Every gap in the spec turns into a guess, and the guess ships. Draftsman writes a spec with no room for guesses: every fact has one home, nothing is left vague, and every unknown is a recorded decision that names the work it blocks. It also installs a checker that fails the commit whenever any of that stops being true.

It's strict about gaps, not about length. A small MVP gets a small spec.

## What it does

| You have | Draftsman |
| --- | --- |
| An idea, or a starter template whose spec is partly filled | **Creates** the spec. It interviews you a few questions at a time, always with a recommendation, and drafts the vision, phases, features, decisions and a build order agents can follow step by step. |
| Docs in some other shape: a PRD, a README, notes | **Migrates** them into the strict layout without losing a fact. A ledger shows where every line went, and contradictions come back to you as questions instead of being settled quietly. |
| A draftsman spec | **Audits** it for what the checker can't see: undefined rules, vague limits, contradictions, blocked steps and missing human work. Then it closes each gap. |

Every gap is closed one of three ways: Draftsman derives it from your docs or code and cites the source, asks you, or records an `open` decision with its recommendation and the step it blocks. It never writes down an answer nobody gave it. If you're away, it turns every question into an open decision, finishes everything else, and leaves you the list.

## What you get

```
AGENTS.md              how agents build: pick a step, build it, review it, merge it, tick it
CLAUDE.md              @AGENTS.md, so Claude Code reads the same guide
.githooks/pre-commit   runs the checker before every commit
.agents/skills/        review-step, audit-milestone and debt-ledger for the build workflow
THIRD-PARTY-NOTICES.md the licence of the work those skills adapt
scripts/check_spec.py  the checker
docs/
  AGENTS.md            the rules and formats for everything below
  README.md            entry point, with a generated feature index
  product.md           vision, phases and gates, and the build order
  decisions.md         accepted, proposed, open and superseded decisions
  features/<slug>.md   Behavior (with Done when) and Implementation
  shared/<topic>.md    facts two or more features use
  data/<name>.yaml     numbers the code reads, referenced by key
  never.md             what will never be built, and why
  ideas.md             parked ideas
  risks.md             risks and their guardrails
```

`AGENTS.md` is the standard file every major agent reads, so one spec works whichever agent you use. Several agents can work in parallel too: each takes one build-order list, and git branches show which steps are taken.

The guide also carries a build workflow that runs without someone watching every step: one worktree per step, a review by a fresh agent before each merge, pull requests merged once CI passes (or fast-forwards without a remote), and a consolidation pass at the end of each milestone that audits the code and resolves the `NOTE:` comments marking deliberate simplifications. Agents never decide: a step that an open decision names waits for the answer, and nothing is stubbed. Each milestone ends with a team step that confirms its done-when, and agents start the next milestone only once it's ticked.

## What the checker enforces

`scripts/check_spec.py` is plain Python 3.9+ and needs nothing installed unless your data files are YAML (then it needs PyYAML; `uv run scripts/check_spec.py` installs it). It exits non-zero, with `file:line`, when any of these happens:

- Placeholder text: `TBD`, `TODO`, `etc.`, "to be decided" or an unfilled template marker.
- A broken link or anchor.
- A decision that's cited but doesn't exist, or a citation of a superseded decision.
- A malformed decision row, an open decision that doesn't name the step, milestone or backticked phase it blocks, or a superseded row that nothing replaced.
- An unticked build step without a done-when, an `(after …)` that names a missing step, or a milestone without a done-when or a confirm step.
- An agent's step that names an open decision without waiting for it, or builds on a proposed one.
- A feature with the wrong frontmatter or sections, no done-when, or an unknown phase, or one that isn't linked from the roadmap.
- The same endpoint defined in two places.
- An error code that isn't in the registry, or that's used with the wrong status.
- A reference like `limits.yaml → free.plans_per_week` to a file or key that doesn't exist.
- A refusal in never.md that doesn't cite a decision, or a feature index that's out of date.
- With a platform layer (`docs/platform/`, the decisions, docs and build order a template gives every project built from it): an open `P-` decision that doesn't name the platform step or milestone it blocks, a project decision that replaces a platform one, an error code in both tables, or a platform doc that cites a project decision, names a project error code or links outside the folder.
- With a platform build order (`docs/platform/build-order.md`): any of the build-order problems above in it; a project step that waits for a missing platform step, or is ticked before one it waits for; a project step that names an open `P-` decision without waiting for an unticked platform step it holds.

Turn the hook on with `git config core.hooksPath .githooks`, and copy [spec-check.yml](skills/draftsman/assets/spec-check.yml) into `.github/workflows/` to run the same check in CI.

## Install

### Claude Code

```
/plugin marketplace add fsabuhi/draftsman
/plugin install draftsman@draftsman
```

### Codex

```bash
codex plugin marketplace add fsabuhi/draftsman
```

Then open `/plugins` in Codex and install Draftsman.

### GitHub Copilot CLI

```bash
copilot plugin marketplace add fsabuhi/draftsman
copilot plugin install draftsman@draftsman
```

### Gemini CLI

```bash
gemini extensions install https://github.com/fsabuhi/draftsman
```

### Any agent, with the skills CLI

```bash
npx skills add fsabuhi/draftsman
```

### By hand

Copy `skills/draftsman/` into your agent's skills folder, such as `~/.claude/skills/` for Claude Code. If an agent doesn't support skills, tell it: "Read `skills/draftsman/SKILL.md` and follow it."

## Use

Just say what you want:

- "I want to build an MVP of a meal planner for students. Write the spec so Claude Code can build it."
- "Our docs folder is a mess. Make it something agents can build from, and don't lose anything."
- "Audit our spec. What would an agent have to guess?"

Draftsman picks the mode from what's in the repository and says which one it picked. It only changes docs, never your code. It doesn't commit unless you ask, so the result is a single diff you can review.

## Develop

```bash
python3 -m unittest discover -s tests
```

Each rule the checker enforces has a test that breaks a valid spec in exactly one way. Contributor notes are in [AGENTS.md](AGENTS.md).

## License

[MIT](LICENSE)
