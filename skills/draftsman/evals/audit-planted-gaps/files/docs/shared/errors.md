# Error codes

Every error the product returns carries one of these codes. This file is each code's one home; other docs name a code with its status, as [the docs rules](../AGENTS.md#error-codes) show.

| Code | Status | Meaning | The client |
| --- | --- | --- | --- |
| `unauthenticated` | 401 | The request has no valid session, or the sign-in link is used or expired | Sends the user to sign in |
| `not_found` | 404 | The resource doesn't exist, or the caller may not see it | Says the item is gone and goes back |
