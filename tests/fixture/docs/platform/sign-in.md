---
decisions: [P-002]
---

# Sign-in

A user signs in with a one-time code sent by email. The code works for `platform.json → sign_in.code_minutes` minutes, as [the data file](../data/platform.json) sets; after that, sign-in fails with `code_expired` (401), which [the error table](errors.md#platform-error-codes) lists.
