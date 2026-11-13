"""Each test breaks one rule in a valid spec and expects check_spec.py to name it.

    python3 -m unittest discover -s tests
"""
import importlib.util
import re
import shutil
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCAFFOLD = REPO / "skills" / "draftsman" / "assets" / "scaffold"
FIXTURE = Path(__file__).resolve().parent / "fixture"

spec = importlib.util.spec_from_file_location("check_spec", SCAFFOLD / "scripts" / "check_spec.py")
check_spec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_spec)


def edit(root, rel, old, new, count=1):
    path = root / rel
    text = path.read_text()
    assert old in text, f"{old!r} not in {rel}"
    path.write_text(text.replace(old, new, count))


def append(root, rel, text):
    path = root / rel
    path.write_text(path.read_text() + text)


def edits(root, *changes):
    """Several edits, each (rel, old, new)."""
    for rel, old, new in changes:
        edit(root, rel, old, new)


def one_platform_table(root):
    """docs/platform/decisions.md as Draftsman 0.4 wrote it: one table, no open rows, nothing waiting on them."""
    path = root / "docs/platform/decisions.md"
    text = path.read_text()
    text = text.replace("## Accepted and proposed\n\n", "")
    path.write_text(text[:text.index("## Open")].rstrip("\n") + "\n")
    edit(root, "docs/platform/build-order.md", "(after 1.1; P-004)", "(after 1.1)")


PLATFORM_DECISIONS, PLATFORM_DOC = "docs/platform/decisions.md", "docs/platform/sign-in.md"
PLATFORM_ORDER = "docs/platform/build-order.md"


# (name, how to break the fixture, a phrase the problem report must contain)
BREAKS = [
    ("placeholder word", lambda r: append(r, "docs/features/swaps.md", "\nPricing is TBD.\n"), "`TBD` leaves a gap"),
    ("incomplete list", lambda r: append(r, "docs/ideas.md", "- Comics, magazines, etc.\n"), "`etc` leaves a gap"),
    ("unfilled template", lambda r: append(r, "docs/ideas.md", "<<fill: ideas>>\n"), "`<<fill` leaves a gap"),
    ("broken link", lambda r: append(r, "docs/ideas.md", "- [Maps](maps.md)\n"), "broken link maps.md"),
    ("broken anchor", lambda r: append(r, "docs/ideas.md", "- [x](product.md#nope)\n"), "broken anchor product.md#nope"),
    ("unknown decision", lambda r: append(r, "docs/ideas.md", "- Per D-099.\n"), "D-099 isn't in decisions.md"),
    ("superseded citation", lambda r: append(r, "docs/ideas.md", "- Per D-001.\n"), "D-001 is superseded"),
    ("dangling superseded row", lambda r: edit(r, "docs/decisions.md", "| D-001 |\n", "| |\n"),
     "D-001 is superseded, but no row names it"),
    ("supersedes a live row", lambda r: edit(r, "docs/decisions.md", "| D-001 |\n", "| D-001, D-003 |\n"),
     "D-002 supersedes D-003, so mark D-003 `superseded`"),
    ("open row blocks nothing", lambda r: edit(r, "docs/decisions.md", "| Step 1.3 |", "| soon |"),
     "D-003: Needed by names what it blocks"),
    ("phase named in prose", lambda r: edit(r, "docs/decisions.md", "| Step 1.3 |", "| Before the MVP launch |"),
     "D-003: Needed by names what it blocks"),
    ("open row blocks a ticked step", lambda r: edit(r, "docs/decisions.md", "| Step 1.3 |", "| Step 1.1 |"),
     "step 1.1 is ticked, but D-003"),
    ("open row blocks a missing step", lambda r: edit(r, "docs/decisions.md", "| Step 1.3 |", "| Step 4.1 |"),
     "needed by step 4.1, which isn't in the build order"),
    ("bad status for its table", lambda r: edit(r, "docs/decisions.md", "| open |", "| accepted |"),
     "`accepted` doesn't belong in the Open table"),
    ("step without done-when", lambda r: edit(r, "docs/product.md", "  - Done when: an API test", "  - Proof: an API test"),
     "step 1.2 needs an indented `- Done when: …` line"),
    ("step after a missing step", lambda r: edit(r, "docs/product.md", "(after 1.1,", "(after 1.9,"),
     "step 1.2 comes after step 1.9"),
    ("after sharing its parentheses",
     lambda r: edit(r, "docs/product.md", "(after 1.1, platform 1.1; D-002)", "(D-002; after 1.9, platform 1.1)"),
     "step 1.2 comes after step 1.9"),
    ("missing step after a platform step",
     lambda r: edit(r, "docs/product.md", "(after 1.1, platform 1.1; D-002)", "(after platform 1.1 and 1.9; D-002)"),
     "step 1.2 comes after step 1.9"),
    ("step names an open decision that doesn't hold it",
     lambda r: edit(r, "docs/product.md", "(after 1.1, platform 1.1; D-002)", "(after 1.1, platform 1.1; D-002, D-003)"),
     "step 1.2 names D-003, which is open but doesn't hold the step back"),
    ("step builds on a proposed decision",
     lambda r: edit(r, "docs/decisions.md", "| accepted | Listings carry no photo", "| proposed | Listings carry no photo"),
     "step 1.2 names D-002, which is only proposed"),
    ("milestone without a confirm step", lambda r: edit(r, "docs/product.md", "Confirm milestone 1's done-when", "Check milestone 1"),
     "milestone 1 needs a `Confirm milestone 1's done-when (team)` step"),
    ("confirmed milestone with an unticked step", lambda r: edit(r, "docs/product.md", "- [ ] **1.4** Confirm", "- [x] **1.4** Confirm"),
     "milestone 1 is confirmed, but step 1.2 isn't ticked"),
    ("malformed step", lambda r: edit(r, "docs/product.md", "- [x] **1.1**", "- [x] 1.1"),
     "a step is written `- [ ] **<id>** <what it builds>`"),
    ("step in the wrong milestone", lambda r: edit(r, "docs/product.md", "**1.3**", "**2.1**"),
     "step 2.1 sits in milestone 1"),
    ("milestone without done-when", lambda r: edit(r, "docs/product.md", "Done when a tester", "When a tester"),
     "milestone 1 needs a `Done when"),
    ("phase not a slug", lambda r: edit(r, "docs/product.md", "| `after-launch` |", "| After launch |"),
     "each phase is a backticked slug"),
    ("feature frontmatter", lambda r: edit(r, "docs/features/swaps.md", "decisions: []\n", "decisions: []\nowner: sam\n"),
     "starts with exactly four lines"),
    ("feature in an unknown phase", lambda r: edit(r, "docs/features/swaps.md", "ships_in: after-launch", "ships_in: someday"),
     "ships_in `someday` isn't a phase"),
    ("feature without done-when", lambda r: edit(r, "docs/features/swaps.md", "### Done when", "### Finished when"),
     "Behavior needs a `### Done when` list"),
    ("first-phase feature without implementation",
     lambda r: edit(r, "docs/features/listings.md", "## Implementation", "### Implementation"),
     "features in `mvp` need an `## Implementation` section"),
    ("extra feature section", lambda r: append(r, "docs/features/swaps.md", "\n## Notes\n\nMore.\n"),
     "its sections are `## Behavior` then `## Implementation`"),
    ("feature not on the roadmap", lambda r: shutil.copy(r / "docs/features/swaps.md", r / "docs/features/trades.md"),
     "trades.md: isn't linked from the roadmap"),
    ("endpoint defined twice",
     lambda r: append(r, "docs/features/swaps.md", "\n| Endpoint | Does |\n| --- | --- |\n| `POST /v1/listings` | Also |\n"),
     "`POST /v1/listings` is already defined"),
    ("unregistered error code", lambda r: append(r, "docs/ideas.md", "- Fails with `shelf_full` (409).\n"),
     "error code `shelf_full` isn't in docs/shared/errors.md"),
    ("error code with the wrong status", lambda r: append(r, "docs/ideas.md", "- Fails with `listing_full` (422).\n"),
     "`listing_full` is 409 in docs/shared/errors.md, not 422"),
    ("error code without a registry", lambda r: (r / "docs/shared/errors.md").unlink(),
     "it needs a row in docs/shared/errors.md"),
    ("missing data key", lambda r: append(r, "docs/ideas.md", "- Up to `limits.json → free.swaps`.\n"),
     "docs/data/limits.json has no key `free.swaps`"),
    ("missing data key in a decision", lambda r: edit(r, "docs/decisions.md", "no photo in the MVP |", "no photo, under `limits.json → free.photos` |"),
     "docs/data/limits.json has no key `free.photos`"),
    ("missing data file", lambda r: append(r, "docs/ideas.md", "- Up to `caps.yaml → free.swaps`.\n"),
     "docs/data/caps.yaml doesn't exist"),
    ("unreadable data file", lambda r: (r / "docs/data/limits.json").write_text("{nope"), "limits.json: can't be read"),
    ("stale feature index", lambda r: edit(r, "docs/features/swaps.md", "# Swaps", "# Book swaps"),
     "the feature index is out of date"),
    ("CLAUDE.md that skips AGENTS.md", lambda r: (r / "CLAUDE.md").write_text("Be nice.\n"), "must import the shared guide"),
    ("AGENTS.md that skips the docs rules",
     lambda r: edit(r, "AGENTS.md", "read [docs/AGENTS.md](docs/AGENTS.md) first", "read the docs"),
     "must link to docs/AGENTS.md"),
    ("refusal without a decision", lambda r: append(r, "docs/never.md", "| Ads | Users hate them | |\n"),
     "each refusal says why and cites the decision"),
    ("missing required file", lambda r: (r / "docs/ideas.md").unlink(), "docs/ideas.md: missing"),
    ("bad frontmatter outside features", lambda r: edit(r, "docs/product.md", "decisions: [D-002]\n", "tags: [x]\n"),
     "frontmatter outside docs/features/ is exactly"),
    # The platform layer: docs/platform/, which a template ships to every project built from it.
    ("open row in the platform's accepted table",
     lambda r: edit(r, PLATFORM_DECISIONS, "| P-003 | 2026-11-04 | accepted |", "| P-003 | 2026-11-04 | open |"),
     "P-003: `open` doesn't belong in the Accepted and proposed table"),
    ("platform decisions in one table, as before 0.5.0", lambda r: one_platform_table(r),
     "holds the two tables of docs/decisions.md, under `## Accepted and proposed` and `## Open`, since Draftsman 0.5.0"),
    ("app decision id in the platform decisions",
     lambda r: edit(r, PLATFORM_DECISIONS, "| P-004 |", "| D-005 |"),
     "`D-005` isn't a decision id like P-012"),
    ("platform decisions header", lambda r: edit(r, PLATFORM_DECISIONS, "| Why | Supersedes |", "| Why |"),
     "the Accepted and proposed table's header is | ID | Date | Status | Decision | Why | Supersedes |"),
    ("open platform row blocks nothing", lambda r: edit(r, PLATFORM_DECISIONS, "| Step 1.2 |", "| soon |"),
     "P-004: Needed by names what it blocks: a step (Step 2.3) or a milestone (Milestone 4) of docs/platform/build-order.md"),
    ("open platform row names a phase", lambda r: edit(r, PLATFORM_DECISIONS, "| Step 1.2 |", "| `mvp` |"),
     "P-004: Needed by names what it blocks"),
    ("open platform row blocks a missing platform step", lambda r: edit(r, PLATFORM_DECISIONS, "| Step 1.2 |", "| Step 2.1 |"),
     "P-004 is needed by platform step 2.1, which isn't in docs/platform/build-order.md"),
    ("open platform row blocks a ticked platform step", lambda r: edit(r, PLATFORM_DECISIONS, "| Step 1.2 |", "| Step 1.1 |"),
     "step 1.1 is ticked, but P-004"),
    ("platform step names an open platform row that doesn't hold it",
     lambda r: edit(r, PLATFORM_DECISIONS, "| Step 1.2 |", "| Step 1.3 |"),
     "build-order.md:12: step 1.2 names P-004, which is open but doesn't hold the step back"),
    ("open platform row cites an app decision",
     lambda r: edit(r, PLATFORM_DECISIONS, "| Step 1.2 |", "| Step 1.2, as D-002 needs |"),
     "D-002 is this project's own decision"),
    ("proposed platform row a platform step builds on",
     lambda r: edits(r, (PLATFORM_DECISIONS, "| P-003 | 2026-11-04 | accepted |", "| P-003 | 2026-11-04 | proposed |"),
                     (PLATFORM_ORDER, "(after 1.1; P-004)", "(after 1.1; P-003, P-004)")),
     "build-order.md:12: step 1.2 names P-003, which is only proposed: the team accepts it first"),
    ("project step names a proposed platform row",
     lambda r: edits(r, (PLATFORM_DECISIONS, "| P-003 | 2026-11-04 | accepted |", "| P-003 | 2026-11-04 | proposed |"),
                     ("docs/product.md", "platform 1.1; D-002)", "platform 1.1; D-002, P-003)")),
     "product.md:31: step 1.2 names P-003, which is only proposed: nothing builds on it until the template's team"),
    ("project step waits for an open platform row through a ticked platform step",
     lambda r: edits(r, (PLATFORM_DECISIONS, "| Step 1.2 |", "| Milestone 1 |"),
                     ("docs/product.md", "platform 1.1; D-002)", "platform 1.1; D-002, P-004)")),
     "step 1.2 names P-004, an open platform decision: make it wait (after platform …) for an unticked platform step"),
    ("platform word the (after …) doesn't read",
     lambda r: edit(r, "docs/product.md", "(after 1.1, platform 1.1; D-002)", "(after 1.1, platform step 1.1; D-002)"),
     "step 1.2: in (after …), each platform step is written `platform 2.1`, one `platform` per id"),
    ("open platform row with no platform build order",
     lambda r: edits(r, ("docs/product.md", "(after 1.1, platform 1.1; D-002)", "(after 1.1; D-002)"))
     or (r / PLATFORM_ORDER).unlink(),
     "P-004 is needed by the platform's build order, but there's no docs/platform/build-order.md"),
    ("platform build order without its heading", lambda r: edit(r, PLATFORM_ORDER, "# Build order\n", "# Platform plan\n"),
     "starts with a `# Build order` heading"),
    ("platform step after a missing platform step", lambda r: edit(r, PLATFORM_ORDER, "(after 1.1; P-004)", "(after 1.9; P-004)"),
     "step 1.2 comes after step 1.9, which isn't another step in the platform's build order"),
    ("project step names an open platform row without waiting for it",
     lambda r: edit(r, "docs/product.md", "(after 1.1, platform 1.1; D-002)", "(after 1.1; D-002, P-004)"),
     "step 1.2 names P-004, an open platform decision: make it wait (after platform …)"),
    ("project step waits for a missing platform step",
     lambda r: edit(r, "docs/product.md", "platform 1.1;", "platform 1.9;"),
     "step 1.2 comes after platform step 1.9, which isn't in docs/platform/build-order.md"),
    ("project step waits for a platform step with no platform build order",
     lambda r: (r / PLATFORM_ORDER).unlink(),
     "step 1.2 comes after platform step 1.1, but there's no docs/platform/build-order.md"),
    ("project step ticked before its platform step",
     lambda r: edit(r, "docs/product.md", "- [ ] **1.2** Creating listings (after 1.1, platform 1.1;",
                    "- [x] **1.2** Creating listings (after 1.1, platform 1.2;"),
     "step 1.2 is ticked, but platform step 1.2, which it comes after, isn't ticked"),
    ("platform step names a platform step with the prefix",
     lambda r: edit(r, PLATFORM_ORDER, "(after 1.1; P-004)", "(after platform 1.1; P-004)"),
     "names other platform steps by number alone"),
    ("platform milestone without a confirm step",
     lambda r: edit(r, PLATFORM_ORDER, "Confirm milestone 1's done-when (team)", "Final check (team)"),
     "build-order.md:5: milestone 1 needs a `Confirm milestone 1's done-when (team)` step"),
    ("platform milestone headed like the project's",
     lambda r: edit(r, PLATFORM_ORDER, "## 1. Sign-in", "#### 1. Sign-in"),
     "the platform's build order needs at least one milestone, headed `## 1. <name>`"),
    ("platform step without done-when",
     lambda r: edit(r, PLATFORM_ORDER, "  - Done when: an API test sends", "  - Proof: an API test sends"),
     "build-order.md:12: step 1.2 needs an indented `- Done when: …` line"),
    ("platform build order cites an app decision",
     lambda r: edit(r, PLATFORM_ORDER, "(after 1.1; P-004)", "(after 1.1; P-004, D-002)"),
     "D-002 is this project's own decision"),
    ("app decision supersedes a platform decision", lambda r: edit(r, "docs/decisions.md", "| D-001 |\n", "| D-001, P-001 |\n"),
     "D-002 can't supersede P-001"),
    ("superseded platform row nothing names", lambda r: edit(r, PLATFORM_DECISIONS, "| P-001 |\n", "| |\n"),
     "P-001 is superseded, but no row names it under Supersedes"),
    ("platform row supersedes a missing platform row", lambda r: edit(r, PLATFORM_DECISIONS, "| P-001 |\n", "| P-001, P-009 |\n"),
     "P-002 supersedes P-009, which doesn't exist"),
    ("platform row supersedes a live app row",
     lambda r: edit(r, "docs/decisions.md", "| D-004 | 2026-11-02 | superseded |", "| D-004 | 2026-11-02 | accepted |"),
     "P-003 supersedes D-004, so mark D-004 `superseded`"),
    ("unknown platform decision", lambda r: append(r, "docs/ideas.md", "- Per P-009.\n"),
     "P-009 isn't in docs/platform/decisions.md"),
    ("superseded platform citation", lambda r: append(r, "docs/ideas.md", "- Per P-001.\n"), "P-001 is superseded"),
    ("code in both error tables",
     lambda r: append(r, "docs/shared/errors.md", "| `code_expired` | 401 | The code is too old | Asks for a new code |\n"),
     "`code_expired` is already in docs/platform/errors.md"),
    ("platform code with the wrong status", lambda r: append(r, "docs/ideas.md", "- Fails with `code_expired` (403).\n"),
     "`code_expired` is 401 in docs/platform/errors.md, not 403"),
    ("platform doc cites an app decision", lambda r: append(r, PLATFORM_DOC, "\nListings follow D-002.\n"),
     "D-002 is this project's own decision"),
    ("platform decision cites an app decision outside Supersedes",
     lambda r: edit(r, PLATFORM_DECISIONS, "not on messages |", "not on messages, as D-002 found |"),
     "D-002 is this project's own decision"),
    ("platform doc names an app error code", lambda r: append(r, PLATFORM_DOC, "\nA full shelf fails with `listing_full` (409).\n"),
     "`listing_full` is this project's own error code"),
    ("platform doc links outside its folder", lambda r: append(r, PLATFORM_DOC, "\nSee [listings](../features/listings.md).\n"),
     "../features/listings.md is outside docs/platform/"),
]


class CheckSpec(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp()) / "repo"
        shutil.copytree(FIXTURE, self.root)

    def tearDown(self):
        shutil.rmtree(self.root.parent)

    def problems(self, fix=False):
        return check_spec.check(self.root, fix)[0]

    def test_fixture_passes(self):
        self.assertEqual(self.problems(), [])

    def test_each_break_is_caught(self):
        for name, breaker, phrase in BREAKS:
            with self.subTest(name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "repo"
                shutil.copytree(FIXTURE, root)
                breaker(root)
                found = check_spec.check(root)[0]
                self.assertTrue(any(phrase in p for p in found), f"{name}: no problem mentions {phrase!r}: {found}")

    def test_code_spans_and_blocks_may_quote_placeholders(self):
        append(self.root, "docs/ideas.md", "\nThe check rejects `TBD` and `etc.`:\n\n```\nTODO etc. D-999 [x](nope.md)\n```\n")
        self.assertEqual(self.problems(), [])

    def test_open_decision_held_through_an_earlier_step(self):
        """D-003 holds step 1.3, so a step that comes after 1.3 waits for it too."""
        edit(self.root, "docs/product.md", "(after 1.1, platform 1.1; D-002)", "(after 1.1, 1.3; D-002, D-003)")
        self.assertEqual(self.problems(), [])

    def test_open_platform_decision_held_through_a_platform_step(self):
        """P-004 holds platform step 1.2, so a project step that comes after it waits for P-004 too."""
        edit(self.root, "docs/product.md", "(after 1.1, platform 1.1; D-002)", "(after platform 1.2, 1.1; D-002, P-004)")
        self.assertEqual(self.problems(), [])

    def test_open_platform_decision_held_through_project_and_platform_chains(self):
        """Project 1.5 waits for project 1.2, which waits for platform 1.5, which waits for platform 1.2, which P-004 holds."""
        edits(self.root, ("docs/product.md", "(after 1.1, platform 1.1; D-002)", "(after 1.1, platform 1.5; D-002)"),
              (PLATFORM_ORDER, "\nTeam:\n", "- [ ] **1.5** Codes in the user's language (after 1.2)\n"
                                            "  - Done when: an API test gets a code in French.\n\nTeam:\n"))
        append(self.root, "docs/product.md", "")
        edit(self.root, "docs/product.md", "\nTeam:\n", "- [ ] **1.5** Listing expiry (after 1.2; P-004)\n"
                                                      "  - Done when: an API test expires a listing.\n\nTeam:\n")
        self.assertEqual(self.problems(), [])

    def test_one_platform_table_still_resolves_its_rows(self):
        """A 0.4 platform decisions file gets one problem, not one per citation of its rows."""
        one_platform_table(self.root)
        found = self.problems()
        self.assertEqual(len(found), 1, found)
        self.assertIn("since Draftsman 0.5.0", found[0])

    def test_summary_counts_platform_decisions_and_steps(self):
        problems, summary = check_spec.check(self.root)
        self.assertEqual(problems, [])
        self.assertEqual(summary, "Spec OK: 2 features, 4 decisions (1 open), 4 platform decisions (1 open), "
                                  "4 steps (1 ticked), 3 platform steps (1 ticked).")

    def test_proposed_platform_decision_is_allowed(self):
        edit(self.root, PLATFORM_DECISIONS, "| P-003 | 2026-11-04 | accepted |", "| P-003 | 2026-11-04 | proposed |")
        self.assertEqual(self.problems(), [])

    def test_platform_decisions_may_hold_an_open_row_for_a_milestone(self):
        edit(self.root, PLATFORM_DECISIONS, "| Step 1.2 |", "| Milestone 1 |")
        self.assertEqual(self.problems(), [])

    def test_team_step_may_name_the_decision_it_answers(self):
        edit(self.root, "docs/product.md", "Confirm milestone 1's done-when (team)", "Confirm milestone 1's done-when (team; D-003)")
        self.assertEqual(self.problems(), [])

    def test_superseded_rows_may_name_keys_that_moved(self):
        edit(self.root, "docs/decisions.md", "Listings carry a photo |", "Listings carry `limits.json → free.photos` photos |")
        self.assertEqual(self.problems(), [])

    def test_spec_without_platform_layer_passes(self):
        """docs/platform/ is optional: without it, the doc that builds on it and the row it replaced, the spec passes."""
        shutil.rmtree(self.root / "docs/platform")
        (self.root / "docs/shared/sign-in.md").unlink()
        edit(self.root, "docs/product.md", "(after 1.1, platform 1.1; D-002)", "(after 1.1; D-002)")
        edit(self.root, "docs/decisions.md", "| D-004 | 2026-11-02 | superseded | API errors carry an English message "
                                             "and no code | One field is simpler | |\n", "")
        problems, summary = check_spec.check(self.root)
        self.assertEqual(problems, [])
        self.assertEqual(summary, "Spec OK: 2 features, 3 decisions (1 open), 4 steps (1 ticked).")

    def test_features_may_cite_platform_decisions(self):
        edit(self.root, "docs/features/listings.md", "decisions: [D-002]", "decisions: [D-002, P-002]")
        self.assertEqual(self.problems(), [])

    def test_migration_archive_is_ignored(self):
        (self.root / "docs-archive").mkdir()
        (self.root / "docs-archive/AGENTS.md").write_text("Old rules, TBD. See D-404 and [x](gone.md).\n")
        self.assertEqual(self.problems(), [])

    def test_fix_regenerates_the_index(self):
        edit(self.root, "docs/features/swaps.md", "# Swaps", "# Book swaps")
        self.assertEqual(self.problems(fix=True), [])
        self.assertIn("| [Book swaps](features/swaps.md) | after-launch |", (self.root / "docs/README.md").read_text())

    def test_problems_carry_line_numbers(self):
        append(self.root, "docs/features/swaps.md", "\nPricing is TBD.\n")
        found = self.problems()
        line = len((self.root / "docs/features/swaps.md").read_text().splitlines())
        self.assertIn(f"docs/features/swaps.md:{line}: `TBD` leaves a gap", found[0])

    def test_scaffold_fails_until_filled(self):
        root = Path(tempfile.mkdtemp()) / "fresh"
        shutil.copytree(SCAFFOLD, root)
        self.assertTrue(any("<<fill" in p for p in check_spec.check(root)[0]))
        shutil.rmtree(root.parent)

    def test_scaffold_passes_once_filled(self):
        """Filling every marker and adding one feature must be enough: the templates themselves are valid."""
        root = Path(tempfile.mkdtemp()) / "filled"
        shutil.copytree(SCAFFOLD, root)
        for f in root.rglob("*.md"):
            text = re.sub(r"<<fill: today's date[^>]*>>", "2026-11-05", f.read_text())
            f.write_text(re.sub(r"<<fill:[^>]*>>", "Filled in.", text))
        (root / "docs/features").mkdir(exist_ok=True)
        shutil.copy(FIXTURE / "docs/features/swaps.md", root / "docs/features/swaps.md")
        edit(root, "docs/features/swaps.md", "ships_in: after-launch", "ships_in: later")
        append(root, "docs/product.md", "\nThe first feature is [swaps](features/swaps.md).\n")
        problems = check_spec.check(root, fix=True)[0]
        shutil.rmtree(root.parent)
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
