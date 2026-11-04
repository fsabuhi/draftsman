---
ships_in: mvp
decisions: [D-005]
---

# Tutor profiles

## Behavior

A tutor fills in a profile, and the team vets them before any student can book them.

### What the user experiences

1. After signing up, the tutor gives their university, their course, the subjects and levels they teach (GCSE or A-level) and their weekly availability.
2. The profile shows "Waiting for vetting" until the team has vetted them.
3. Once vetted, the tutor can be matched and booked.

### Rules

- A tutor is `pending` until the team vets them, then `vetted`. Only vetted tutors are matched or booked.
- Vetting is an interview and an enhanced DBS check, done by the team outside the app.
- Sessions happen only in the app's video room (D-005).

### Done when

- API tests show a pending tutor isn't matched, and a vetted one is.

## Implementation

| Endpoint | Does |
| --- | --- |
| `PUT /v1/tutors/me` | Saves the signed-in tutor's profile: `{university, course, subjects, availability}`. |
| `GET /v1/tutors/{id}` | Returns a vetted tutor's public profile. Fails with `not_found` (404) for a pending tutor. |

During the pilot, the team marks a tutor vetted directly in the database.
