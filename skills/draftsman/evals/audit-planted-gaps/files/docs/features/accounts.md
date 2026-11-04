---
ships_in: mvp
decisions: [D-003]
---

# Accounts

## Behavior

Students and tutors sign up and sign in with a link sent to their email (D-003). There are no passwords.

### What the user experiences

1. The user enters their email and says whether they're a student or a tutor.
2. They get an email with a sign-in link that works for `limits.yaml → sign_in.link_minutes` minutes.
3. Opening the link signs them in on that device. A student then gives their year group and subjects; a tutor goes on to [their profile](tutor-profiles.md).

### Rules

- One account per email address. Signing up with an email that already has an account sends a sign-in link instead.
- A used or expired link fails with `unauthenticated` (401), and the app offers to send a new one.

### Done when

- API tests sign a student and a tutor up and in with a link.
- A used or expired link is refused.

## Implementation

| Endpoint | Does |
| --- | --- |
| `POST /v1/auth/link` | Takes `{email, role}` and emails a sign-in link. Always answers 202, so it never reveals whether an account exists. |
| `POST /v1/auth/verify` | Takes `{token}` from the link and returns `{session_token, user}`. Fails with `unauthenticated` (401) when the token is used or expired. |
