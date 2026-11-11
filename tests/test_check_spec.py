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
    ("step after a missing step", lambda r: edit(r, "docs/product.md", "(after 1.1;", "(after 1.9;"),
     "step 1.2 comes after step 1.9"),
    ("after sharing its parentheses", lambda r: edit(r, "docs/product.md", "(after 1.1; D-002)", "(D-002; after 1.9)"),
     "step 1.2 comes after step 1.9"),
    ("step names an open decision that doesn't hold it",
     lambda r: edit(r, "docs/product.md", "(after 1.1; D-002)", "(after 1.1; D-002, D-003)"),
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
        edit(self.root, "docs/product.md", "(after 1.1; D-002)", "(after 1.1, 1.3; D-002, D-003)")
        self.assertEqual(self.problems(), [])

    def test_team_step_may_name_the_decision_it_answers(self):
        edit(self.root, "docs/product.md", "Confirm milestone 1's done-when (team)", "Confirm milestone 1's done-when (team; D-003)")
        self.assertEqual(self.problems(), [])

    def test_superseded_rows_may_name_keys_that_moved(self):
        edit(self.root, "docs/decisions.md", "Listings carry a photo |", "Listings carry `limits.json → free.photos` photos |")
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
