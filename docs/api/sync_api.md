# Sync API Documentation

## Endpoints

### POST /api/sync
- Accepts: Encrypted payload (Fernet)
- Headers: Authorization: Bearer <JWT>
- Body: Encrypted bytes (see encryption wrapper)
- Role: Rep only (must match JWT user)

#### Example Payload (before encryption)
```json
{
  "route_id": "r1",
  "stores": [1,2],
  "tasks": ["visit"]
}
```

#### Response
```json
{
  "status": "ok"
}
```

### Error Responses
- 400: Malformed encryption blob
- 401/403: Invalid or missing JWT, role mismatch
- 409: Conflict (duplicate or out-of-order sync)

### Notes
- All data in transit and at rest is encrypted
- Use Fernet key from .env
- Never commit real payloads or keys
