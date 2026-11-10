# Agent guide

<<fill: what this repository builds, in one sentence>> Everything in it is built from the spec in `docs/`.

| Folder | Holds | Read first |
| --- | --- | --- |
| `docs/` | The spec: product, features, decisions and shared definitions | [docs/AGENTS.md](docs/AGENTS.md), before changing anything there |
| `scripts/` | `check_spec.py`, the spec checker | |
| `.agents/skills/` | Skills any agent follows by reading the file: [review-step](.agents/skills/review-step/SKILL.md), [audit-milestone](.agents/skills/audit-milestone/SKILL.md) and [debt-ledger](.agents/skills/debt-ledger/SKILL.md) | |
<<fill: a row for each code folder, naming the guide an agent reads before working there>>

## Before you write code

1. **Pick a step** from [the build order](docs/product.md#build-order), in the list you're working on: the first unticked step that isn't marked `(team)`, whose `(after …)` steps are all ticked on the shared `main`, that nobody has taken (see [Parallel sessions](#parallel-sessions)), and that isn't waiting on a decision: no `open` row in [decisions.md](docs/decisions.md) names the step or its milestone under Needed by. If no step qualifies, stop and tell the team which decisions or team steps are in the way.
2. **Read** the step's feature file, then the shared docs and data keys it links to. Links into later phases are context, not scope.
3. **Build the step and nothing else.** Its done-when is the bar: prove it with a test or a command.
4. **Tick the step** on its branch once its done-when holds and the checks pass, so the tick lands with the step. When every step of a milestone is ticked, run the [consolidation pass](#consolidation-pass), then stop: the team confirms the milestone's done-when before the next milestone starts.

## When the spec doesn't say

Stop and ask the team. Don't pick an answer and carry on, and don't write a test that picks one. Put the answer in its one home in the same change; if it's a choice the team will make later, add an `open` row to decisions.md that names the step it blocks. If only part of a step is blocked, split the step and build the unblocked part.

## Parallel sessions

Agents can work at the same time, one per build-order list; two on the same list would pick the same step. Git is the shared state, so there's no status file to keep up to date.

**The shared `main`** is `origin/main` after `git fetch origin` when the repository has a remote, and the local `main` when it has none. Read the build order there, never from a stale local copy. A step is done once it's ticked on the shared `main`. It's taken while a branch named `step-<id>` exists: check `git branch --list 'step-*'` and, with a remote, `git ls-remote --heads origin 'step-*'` and the open pull requests.

1. **One worktree per change, named for it.** Never edit or commit in the root checkout. Branch from the shared `main`: `git worktree add .worktrees/<id> -b step-<id> origin/main`, or `main` without a remote, using a short name instead of `step-<id>` for a change that isn't a step. With a remote, push the branch straight away so other machines see the claim.
2. **Commit each change once its checks pass**, then rebase onto the shared `main` and rerun the checks. Never merge `main` into a branch. When a rebase conflicts in a generated file, rerun its generator instead of merging it by hand.
3. **Review before merging.** Once the checks pass, start a fresh agent with none of the step's context and have it follow [review-step](.agents/skills/review-step/SKILL.md) on the branch. Fix what it finds that this guide and the spec agree with. A finding that would change the spec is a question for the team.
4. **Merge.**
   - With a GitHub remote: push, open a pull request with `gh pr create`, wait for its checks with `gh pr checks --watch`, then `gh pr merge --rebase --delete-branch`. If GitHub says the branch is out of date, run `gh pr update-branch --rebase` and wait for the checks again; if that conflicts, rebase locally and `git push --force-with-lease`. If the merge is still refused, stop and ask.
   - Without a remote: fast-forward `main` with `git merge --ff-only step-<id>`.
5. **Force-push only your own branch, and only with `--force-with-lease`.** Never force-push `main`.
6. **Clean up after the merge:** `git worktree remove .worktrees/<id>`, then `git branch -D step-<id>` (a rebase merge gives the commits new ids, so `-d` refuses), then update the root checkout with `git pull --ff-only` when there's a remote.

## Consolidation pass

Cleanup happens at the end of every milestone, without waiting for a yes. Once every list's steps for a milestone are ticked on the shared `main`, one agent runs the pass in a worktree named `consolidate-<milestone>`:

1. Follow [audit-milestone](.agents/skills/audit-milestone/SKILL.md) on the code folders, and [debt-ledger](.agents/skills/debt-ledger/SKILL.md) for the `NOTE:` comments that are due.
2. Fix every must-fix and should-fix finding: delete dead code, reuse instead of duplicating, merge near-copies, split code that mixes jobs, and resolve each `NOTE:` whose upgrade point has been reached.
3. Each refactor is its own commit and changes no behavior: the existing tests pass unchanged, and a bug fix still comes with its test. Name it like any other commit, with `(consolidate <milestone>)` in parentheses.
4. A finding that would change specified behavior or a published interface is not a refactor: ask the team.

Then merge as usual and ask the team to confirm the milestone's done-when.

## Rules for the whole repository

- **Ask, never assume.** When the docs and the code don't answer a question, ask before writing anything that depends on the answer.
- **The docs are the spec.** Code never contradicts them. When code needs a fact the docs don't have, the fact goes into the docs in the same change.
- **Nothing in [never.md](docs/never.md) gets built.**
- **Reuse before writing.** Before new code, look for a helper, component or pattern already in the repository, then the standard library or an installed package. Only then write the minimum the step needs: no option, config or abstraction it doesn't use.
- **Never cut safety to make a change smaller.** Validation at trust boundaries, error handling that prevents data loss, security and accessibility stay, whatever the diff size.
- **Finish the whole change.** Every caller, test and fixture your change breaks is part of it. Code you move or merge keeps its error handling and validation.
- **Comment only the why** the code can't show, in one line.
- **Say what you skipped.** End each reply and pull request description (the commit message, without a remote) with what wasn't done or checked, and any risk the team must know.
- **Fix a bug at its root.** Find every caller of the code you touch and fix the shared code once, not one caller.
- **A fix comes with a test** that fails without it.
- **Refactor in its own commit, never folded into a build step.** When a step can't be built cleanly without one, commit the refactor first on the same branch. Other mess you notice waits for the [consolidation pass](#consolidation-pass).
- **Mark deliberate simplifications** with a `NOTE:` comment that names the limit and what lifts it: a step id, a decision id or a condition. [debt-ledger](.agents/skills/debt-ledger/SKILL.md) finds them once they're due.
- **Commit each change once its checks pass,** one commit per change, named `<area>: <what it does> (<step or decision id>)`.

## Commands

| Task | Command |
| --- | --- |
| Check the spec, after any change to the docs | `python3 scripts/check_spec.py` |
| Regenerate the feature index | `python3 scripts/check_spec.py --fix` |
| Block commits that fail the checks, once per clone | `git config core.hooksPath .githooks` |
<<fill: a row for each code folder: the one command that runs all of its checks>>
