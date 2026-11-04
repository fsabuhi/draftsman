---
tags: [draftsman, audit]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Our spec is in docs/, and agents start building from it tomorrow. Can you audit it and fix anything an agent would otherwise have to guess at? I'm unreachable until tomorrow morning, so don't wait for me. Leave me a list of anything only I can decide.

Input files: AGENTS.md, CLAUDE.md, .githooks/pre-commit, scripts/check_spec.py, docs/
