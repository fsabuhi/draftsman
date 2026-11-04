---
tags: [draftsman, migrate]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Our docs are all over the place: a PRD, meeting notes, an API doc and the README all say slightly different things. We're about to have Claude Code and Codex build the app from them, so please restructure everything into a proper spec they can build from without guessing. Don't lose anything we wrote down. I'm in workshops all day and can't answer questions, so leave me a list of anything you need me to decide.

Input files: README.md, docs/PRD.md, docs/notes.md, docs/api.md, backend/app.py
