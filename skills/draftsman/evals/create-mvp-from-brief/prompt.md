---
tags: [draftsman, create]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I want to build an MVP of a meal planner for university students, and I want AI coding agents (Claude Code and Codex) to build it from a spec in this repo. Can you write the spec so they can start building?

What I know so far:

- It's called Pantry Pal. Students on a tight budget with a small kitchen tell it what's in their cupboard, their weekly food budget and their dietary needs (vegetarian, vegan, halal, allergies). It plans a week of dinners from cheap ingredients and makes a shopping list for whatever's missing.
- MVP: sign up with email, keep a pantry list, generate a plan of 7 dinners, swap any dinner you don't like, and the shopping list.
- Free users get one plan a week. Premium is £2.99 a month for unlimited plans and swaps.
- A mobile app for iOS and Android. I'm thinking Expo with a Python backend, but I'm not sure yet.
- An LLM writes the plans.
- We will never add calorie counting or weight-loss features. We don't want to push diet culture on students.
- Success means 200 students using it every week by the end of the first term.

I'm about to board a long flight and can't answer anything for the next few hours, so don't wait on me. Do as much as you can, and tell me what you need from me when I land.
