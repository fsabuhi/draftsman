---
decisions: [D-002]
---

# Product

## Vision

**One line:** swap books with your neighbours.

## Roadmap

[Listings](features/listings.md) ship first and [swaps](features/swaps.md) after launch.

### Phases and gates

| Phase | Ships | Gate to move on |
| --- | --- | --- |
| `mvp` | Listings | 100 listings in the first month |
| `after-launch` | Swaps | 20 swaps a week |

### Build order

#### 1. Foundation

Done when a tester can list a book on staging.

Backend:

- [x] **1.1** The API skeleton and CI
- [ ] **1.2** Creating listings (after 1.1; D-002)
  - Done when: an API test creates a listing and gets `listing_full` (409) past the cap.

Team:

- [ ] **1.3** Sign up for the hosting account (team)
  - Done when: the account is in the team's password manager.
