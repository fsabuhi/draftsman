# API

## POST /v1/scans

Upload a receipt image (multipart, field `image`, JPEG or PNG, max 10 MB).

Response 201:

```json
{ "scan_id": "...", "line_items": [{ "name": "...", "price_pence": 1250 }], "total_pence": 4830 }
```

Free users get 5 scans per day; after that the endpoint returns 429.

## POST /v1/splits

Create a split from a scan. Body: `{ "scan_id": "..." }`. Response 201: `{ "split_id": "...", "join_url": "..." }`

## GET /v1/splits/{id}

Returns the split with its items and who claimed them.
