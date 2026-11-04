---
decisions: [D-002, D-003, D-004]
---

# Product

## Vision

**One line:** Tutorlink lets secondary-school students in the UK book one-to-one online tutoring with vetted university students, for far less than an agency charges.

### The problem

Tutoring through an agency costs £40 to £60 an hour, so most families can't afford regular help. University students would tutor for less, but parents have no way to know who is safe and good.

### Who it's for

Students aged 14 to 18 preparing for GCSEs and A-levels, and their parents. It's not for primary-school children or adult learners.

### Principles

- **Safety first.** No tutor meets a student until the team has vetted them, because parents trust us with their children.
- **Cheap enough to be weekly.** Families should be able to book every week, so the price stays well under an agency's.
- **Every session leaves a record.** Sessions happen only in the app's own video room.

## Roadmap

### Phases and gates

A phase starts only when the gate before it is met.

| Phase | What ships | Gate to move on |
| --- | --- | --- |
| `mvp` | [Accounts](features/accounts.md), [tutor profiles](features/tutor-profiles.md), [matching](features/matching.md) and [bookings](features/bookings.md), as a free pilot (D-004) | 100 completed sessions in the first eight weeks after launch |
| `after-launch` | [Reviews](features/reviews.md) and paying tutors through the app | 30% of students book a second session within a month |
| `later` | Nothing yet; parked ideas wait in [ideas.md](ideas.md) | None |

### Build order

Each milestone lists its steps by who works them, and a step that needs another names it with `(after …)`. Build each list top to bottom and tick each step when its done-when holds. When all of a milestone's steps are ticked, the team confirms its done-when before the next milestone starts. The format is in [the docs rules](AGENTS.md#build-order).

#### 1. Foundation

Done when the API and the app deploy to staging from `main`, and a tester can sign up and sign in.

Backend:

- [ ] **1.1** The FastAPI project with Postgres, CI running the checks, and a staging deploy (D-002)
  - Done when: CI passes on `main` and `GET /health` answers 200 on staging.
- [ ] **1.2** Accounts: sign-up and sign-in with email links (after 1.1; D-003)
  - Done when: API tests sign a student and a tutor up and in.

Client:

- [ ] **1.3** The Expo app shell, with sign-up and sign-in (after 1.2)
  - Done when: a screen test signs a user in against a mocked API.

#### 2. First booking

Done when a student on staging can book a session with a vetted tutor and both can join its video room.

Backend:

- [ ] **2.1** Tutor profiles and matching (after 1.2)
  - Done when: API tests show a student gets a tutor for a subject.
- [ ] **2.2** Bookings and the free booking limit (after 2.1)
  - Done when: API tests book a session and refuse one past the limit.

Client:

- [ ] **2.3** Tutor onboarding screens (after 2.1)
  - Done when: tutors find onboarding easy and quick.
- [ ] **2.4** The booking screens and the video room (after 2.2)
  - Done when: a screen test books a session against a mocked API.
