---
ships_in: mvp
decisions: [D-002]
---

# Listings

## Behavior

A user lists a book they'd swap, up to `limits.json → free.listings` at a time.

### Done when

- A new listing shows up for neighbours.

## Implementation

| Endpoint | Does |
| --- | --- |
| `POST /v1/listings` | Creates a listing; past the cap it's `listing_full` (409) |
