# Agent guide

<<fill: what this repository builds, in one sentence>> Everything in it is built from the spec in `docs/`.

| Folder | Holds | Read first |
| --- | --- | --- |
| `docs/` | The spec: product, features, decisions and shared definitions | [docs/AGENTS.md](docs/AGENTS.md), before changing anything there |
| `scripts/` | `check_spec.py`, the spec checker | |
<<fill: a row for each code folder, naming the guide an agent reads before working there>>

## Before you write code

1. **Pick a step** from [the build order](docs/product.md#build-order), in the list you're working on: the first unticked step that isn't marked `(team)`, whose `(after …)` steps are all ticked on `main`, and that isn't waiting on a decision: no `open` row in [decisions.md](docs/decisions.md) names the step or its milestone under Needed by. If no step qualifies, stop and tell the team which decisions or team steps are in the way.
2. **Read** the step's feature file, then the shared docs and data keys it links to. Links into later phases are context, not scope.
3. **Build the step and nothing else.** Its done-when is the bar: prove it with a test or a command.
4. **Tick the step** once its done-when holds and the checks pass. When every step of a milestone is ticked, stop: the team confirms the milestone's done-when before the next milestone starts.

## When the spec doesn't say

Stop and ask the team. Don't pick an answer and carry on, and don't write a test that picks one. Put the answer in its one home in the same change; if it's a choice the team will make later, add an `open` row to decisions.md that names the step it blocks. If only part of a step is blocked, split the step and build the unblocked part.

## Parallel sessions

Agents can work at the same time, one per build-order list; two on the same list would pick the same step. Git is the shared state, so there's no status file to keep up to date.

- A step is done once it's ticked on `main`. It's taken while a branch named `step-<id>` exists, on this machine or on the remote: check `git branch --list 'step-*'` and `git ls-remote --heads origin 'step-*'` before you pick one.
- Work in one worktree per step, `git worktree add .worktrees/<id> -b step-<id>`, and push the branch straight away so other machines see the claim.
- Merge when the checks pass: commit, `git rebase main`, rerun the checks, then fast-forward `main` with `git merge --ff-only step-<id>`. When a rebase conflicts in a generated file, rerun its generator instead of merging it by hand.
- Afterwards, remove the worktree and delete the branch, here and on the remote.

## Rules for the whole repository

- **Ask, never assume.** When the docs and the code don't answer a question, ask before writing anything that depends on the answer.
- **The docs are the spec.** Code never contradicts them. When code needs a fact the docs don't have, the fact goes into the docs in the same change.
- **Nothing in [never.md](docs/never.md) gets built.**
- **A fix comes with a test** that fails without it.
- **Recommend a refactor when code gets messy:** say what it fixes and what it touches, then wait for a yes. A refactor is its own commit.
- **Commit each change once its checks pass,** one commit per change, named `<area>: <what it does> (<step or decision id>)`.

## Commands

| Task | Command |
| --- | --- |
| Check the spec, after any change to the docs | `python3 scripts/check_spec.py` |
| Regenerate the feature index | `python3 scripts/check_spec.py --fix` |
| Block commits that fail the checks, once per clone | `git config core.hooksPath .githooks` |
<<fill: a row for each code folder: the one command that runs all of its checks>>
