# Platform decisions

The decisions of the template this project is built from. Only the template changes them.

| ID | Date | Status | Decision | Why | Supersedes |
| --- | --- | --- | --- | --- | --- |
| P-001 | 2026-10-01 | superseded | Users sign in with a password | The starter shipped with it | D-010 |
| P-002 | 2026-10-05 | accepted | Users sign in with a one-time code sent by email | Passwords get reused and leaked | P-001 |
| P-003 | 2026-11-04 | accepted | Every API error carries a code from an error table | Clients branch on codes, not on messages | D-004 |
