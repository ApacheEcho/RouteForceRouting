# RouteForce Routing API — Developer Quickstart

## Overview
This guide helps you authenticate and test the RouteForce Routing API using curl and pytest. It covers login, token refresh, logout, and accessing protected endpoints.

---

## 1. Authentication Flow Summary
1. **Login:** Obtain access and refresh tokens via `/api/login`.
2. **Access Protected Endpoint:** Use the access token in the `Authorization` header.
3. **Refresh Token:** Get a new access token via `/api/refresh` using the refresh token.
4. **Logout:** Revoke the access token via `/api/logout`.

---

## 2. Example curl Commands

### Login
```
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "Secret123!"}'
```

### Access Protected Endpoint
```
curl -X GET http://localhost:5000/v1/routes \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Refresh Token
```
curl -X POST http://localhost:5000/api/refresh \
  -H "Authorization: Bearer <REFRESH_TOKEN>"
```

### Logout
```
curl -X POST http://localhost:5000/api/logout \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

## 3. Running the Pytest Suite

1. **Install dependencies:**
   ```
   pip install -r requirements.txt -r requirements-dev.txt
   ```
2. **Run tests:**
   ```
   pytest -v tests/test_auth_flow.py
   ```

---

## 4. Troubleshooting
- **401/403 errors:** Check token validity, user activation, and credentials.
- **Token expired:** Use `/api/refresh` to get a new access token.
- **Database errors:** Ensure the test database is configured and migrations are applied.
- **Redis errors:** Make sure Redis is running for JWT blocklist support.
- **CORS issues:** Confirm frontend and backend are on allowed origins.

---

## 5. Additional Notes
- **Environment Variables:**
  - `RFP_PROTECTED_PATH`: Override the protected endpoint path (default: `/v1/routes`).
  - `TEST_DATABASE_URI`: Set a custom test database URI.
- **Security:**
  - Always use HTTPS in production.
  - Tokens are short-lived; refresh as needed.
  - Logout revokes the access token (JWT blocklist).

---

For more details, see the code and test suite in the repository.
