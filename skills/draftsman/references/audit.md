# Audit: find and close gaps

The checker catches what a script can see. The audit catches the rest: the gaps an agent would otherwise fill with a guess.

## Order

1. Run the checker. Every problem it reports is a finding. If the project's `scripts/check_spec.py` differs from this skill's copy, tell the user and offer to replace it with the skill's copy; never change it any other way.
2. Walk the unticked steps in build order, the current milestone first and then the next. For each step, read it, its feature file, and every shared doc and data key they link to, and ask every question in the table below. These steps are what agents build next, so their gaps cost the most.
3. Read the whole spec once more, end to end, looking for contradictions and duplicates across files.
4. If the repository has code, compare it with the spec: the error codes the code returns, its tables and columns, its endpoints and their fields, and its config values and limits. A fact in the code but not in the spec is a gap. A fact that differs is a contradiction.

## What to look for

| Gap | How to spot it | Example |
| --- | --- | --- |
| Blocked step | An unticked step needs a decision that's still open, or a fact nobody has written down | A payments step while the billing provider is undecided |
| Missing team work | A milestone's done-when needs something no agent can do, and no `(team)` step does it | "Testers play a quiz set" while every quiz item is a draft nobody is assigned to review |
| Unprovable done-when | An agent's step whose done-when no test or command can check, or a team step's that names no one to confirm it | "Users love it", "it feels fast" |
| Incomplete contract | An interface missing an input, a possible result, an error or a limit | An endpoint that "returns the booking", though a booking can fail when the tutor is full |
| Undefined rule | Something is picked, drawn, computed, ranked or matched with no rule, no tie-break or no empty case | "The app picks the best tutor" |
| Vague counter | A limit without what it counts, when it's spent, when it resets, or what happens at the limit | "Free users get 3 bookings": a day, a month, or ever? |
| Undefined term | A word used as if it were defined, but defined nowhere | "a stronger model", "the premium setup" |
| Contradiction | One fact stated two ways, in two docs, or between the prose and a data file | "Sessions last 45 minutes" in prose, 30 in `docs/data/` |
| Duplicate | One fact restated in a second place, even if both agree today | The same limit in a feature file and in a shared doc |
| Overloaded value | One value with two meanings | `null` meaning both "unlimited" and "not decided yet" |
| Unclear lifecycle | A status or state that's missing values, or the moves between them | A relationship that can end, with no rule for when |
| Released-client trap | Something installed apps will depend on, still undecided before the first release | Whether a hidden score is left out of a response, sent as null or flagged |
| Scope leak | An earlier step depends on something only a later phase specifies, or a feature file holds an idea no decision promoted | An MVP step that needs a later feature's data |
| Refused work | A step or a feature that builds something never.md refuses | A reminder that guilt-trips users back, when never.md refuses guilt notifications |
| Over budget | The MVP has more unticked agent steps than its accepted step budget allows | A budget of 12 steps and a build order with 19 |

## Record every finding

Number the findings in the order you find them:

| # | Where | Gap | Blocks | Closed by |
| --- | --- | --- | --- | --- |
| G-1 | docs/features/matching.md:14 | "Picks the best tutor" has no rule, tie-break or empty case | Step 2.2 | open D-009 |
| G-2 | docs/features/bookings.md:9 | The free booking cap has no period | Step 2.3 | answered: per calendar month |

## Close each finding exactly one way

- **Derived:** the docs or the code already answer it. Write the answer in its one home, and name the source in the finding.
- **Answered:** ask the user, in batches of up to five, each question with your recommendation, and write what they say.
- **Open decision:** the user doesn't know, defers, or can't be asked. Add an open row with the question, your recommendation, and the step, milestone or phase it blocks. Where the gap sits in the spec, state only what's already true and link the decision.
- **Not a gap:** you were wrong. Say why in the finding.

Never close a finding by guessing, by deleting the requirement, or by weakening a done-when until it passes. When a fix changes a fact, change it only in its one home, and check that everything linking to it still reads true.
