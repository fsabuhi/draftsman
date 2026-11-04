---
ships_in: mvp
decisions: [D-004, D-005]
---

# Bookings

## Behavior

A student books a session with the tutor they were matched with. During the pilot, sessions are free for students (D-004).

### What the user experiences

1. The student confirms the tutor and the time.
2. Both of them see the session in their list of upcoming sessions.
3. At the start time, both join the session's video room from the app (D-005).

### Rules

- Each session lasts 45 minutes.
- Booking reserves `limits.yaml → session.minutes` minutes of the tutor's availability, so a tutor is never booked twice at once.
- Free students get `limits.yaml → free.bookings` bookings.

### Done when

- A booked session appears for both the student and the tutor.
- A student can't book past the limit.

## Implementation

| Endpoint | Does |
| --- | --- |
| `POST /v1/bookings` | Takes `{tutor_id, start_time}` and returns 201 with the booking: `{id, tutor_id, start_time, end_time, room_url}`. Fails with `not_found` (404) when the tutor doesn't exist. |
| `GET /v1/bookings` | Returns the signed-in user's upcoming sessions, soonest first. |

The video room is created on Daily when the booking is made, and `room_url` opens it.
