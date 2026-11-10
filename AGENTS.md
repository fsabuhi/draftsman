# Working on draftsman

Draftsman is one Agent Skill, `skills/draftsman/`, packaged for several agents.

- `SKILL.md` is what an agent loads. `references/` holds each mode's procedure, and `assets/scaffold/` is copied into users' repositories as is.
- The spec formats are defined once, in `assets/scaffold/docs/AGENTS.md`. SKILL.md and the references point to it rather than restating it.
- `assets/scaffold/.agents/skills/` holds the build workflow's skills, adapted from Ponytail (MIT). Keep the notice in `assets/scaffold/THIRD-PARTY-NOTICES.md` and the one at the repository root current when they change.
- `assets/scaffold/scripts/check_spec.py` is the checker. It stays standard-library Python 3.9+, with PyYAML needed only for YAML data files. The audit eval's `files/` holds a copy as input, so refresh it when the checker changes.
- `tests/fixture/` is a spec that passes. Every rule the checker enforces has an entry in `BREAKS` in `tests/test_check_spec.py` that breaks the fixture in exactly one way. A new rule adds one, and a fix adds a test that fails without it.
- Run the tests on Python 3.9 and on the newest Python: `python3 -m unittest discover -s tests`.
- Eval cases live in `skills/draftsman/evals/`. Their results go in `../draftsman-workspace/`, outside the repository.
- A release bumps the version in every manifest together: `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.github/plugin/plugin.json` and `gemini-extension.json`.
