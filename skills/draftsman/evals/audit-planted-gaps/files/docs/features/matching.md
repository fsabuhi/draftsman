---
ships_in: mvp
decisions: []
---

# Matching

## Behavior

A student picks a subject, a level and a time, and the app matches them with the best available tutor. Tutors with a premium badge are shown first.

### Done when

- A student who asks for a subject gets a tutor.

## Implementation

| Endpoint | Does |
| --- | --- |
| `GET /v1/matches` | Takes `subject`, `level` and `start_time` as query parameters and returns the matched tutor's profile. |
