# Build order

The platform's own milestones. The template's repository builds them; a project waits for a step with `platform` before its id.

## 1. Sign-in

Done when a user signs in with a code from a real email.

Backend:

- [x] **1.1** Sign-in codes, sent to a stub mailbox ([sign-in](sign-in.md))
- [ ] **1.2** Sign-in codes sent through the email provider (after 1.1; P-004)
  - Done when: an API test sends a code through the provider's sandbox.

Team:

- [ ] **1.3** Confirm milestone 1's done-when (team)
  - Done when: the team confirms the milestone's done-when holds.
