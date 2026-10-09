# API Documentation

## Purpose
The API layer manages communication between the React frontend and the Django backend for authentication, donation workflows, inventory operations, and prediction features.

## Base contract
- Base path: `/api`
- JSON request/response format
- JWT-based authentication for protected routes
- Standard HTTP status codes for creation, validation, auth, and authorization errors
- Role-based permission checks enforced on the backend

## Authentication endpoints

### POST /api/auth/register/
Creates a new user while rejecting privileged admin assignment through public registration.

Request example:
```json
{
  "username": "janedonor",
  "email": "jane@example.com",
  "first_name": "Jane",
  "last_name": "Donor",
  "phone_number": "+1234567890",
  "role": "DONOR",
  "password": "StrongPass123!",
  "confirm_password": "StrongPass123!"
}
```

Successful response (201):
```json
{
  "user": {
    "id": 3,
    "username": "janedonor",
    "email": "jane@example.com",
    "first_name": "Jane",
    "last_name": "Donor",
    "phone_number": "+1234567890",
    "role": "donor",
    "is_verified": false
  },
  "email": "jane@example.com",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Validation errors:
- 400 if password mismatch, weak password, duplicate email, unsupported public role, or malformed payload.
- 400 with `role` if an admin role is attempted through public registration.

### POST /api/auth/login/
Authenticates a user by email/password and returns a JWT pair.

Request example:
```json
{
  "email": "jane@example.com",
  "password": "StrongPass123!"
}
```

Successful response (200):
```json
{
  "refresh": "eyJ...",
  "access": "eyJ...",
  "user": {
    "id": 3,
    "username": "janedonor",
    "email": "jane@example.com",
    "first_name": "Jane",
    "last_name": "Donor",
    "phone_number": "+1234567890",
    "role": "donor",
    "is_verified": false
  }
}
```

Error cases:
- 401 for invalid credentials
- 401 for disabled account

### POST /api/auth/refresh/
Refreshes an expired or near-expiry access token using the refresh token.

Request example:
```json
{
  "refresh": "eyJ..."
}
```

Successful response (200):
```json
{
  "access": "eyJ...",
  "refresh": "eyJ..."
}
```

Error cases:
- 401 for invalid or expired refresh token

### GET /api/auth/profile/
Returns the authenticated user profile without exposing passwords or sensitive hashes.

Successful response (200):
```json
{
  "id": 3,
  "username": "janedonor",
  "email": "jane@example.com",
  "first_name": "Jane",
  "last_name": "Donor",
  "phone_number": "+1234567890",
  "role": "donor",
  "is_verified": false
}
```

### PATCH /api/auth/profile/
Updates editable profile fields.

Request example:
```json
{
  "first_name": "Jane",
  "last_name": "Donor",
  "phone_number": "+15557654321"
}
```

Successful response (200):
```json
{
  "id": 3,
  "username": "janedonor",
  "email": "jane@example.com",
  "first_name": "Jane",
  "last_name": "Donor",
  "phone_number": "+15557654321",
  "role": "donor",
  "is_verified": false
}
```

## Protected route behavior
The frontend stores JWT tokens in browser localStorage and attaches the access token to every private request. If the token expires, the client attempts a refresh and redirects to `/login` when refresh fails.

## Role protection endpoints
- `GET /api/auth/role/donor-only/`
- `GET /api/auth/role/verified-ngo-only/`
- `GET /api/auth/role/volunteer-only/`
- `GET /api/auth/role/admin-only/`

Authentication failures return `401 Unauthorized` with a DRF error payload.
Authorization failures return `403 Forbidden`.

## Security considerations
- Passwords are hashed by Django’s authentication backend.
- Public registration cannot create admin users.
- Password hashes and sensitive credentials are not returned in API payloads.
- Role-specific endpoints use backend permission classes instead of client-only checks.

## API groups
- authentication
- donation lifecycle
- matching and routing
- fulfillment tracking
- notifications
- feedback and complaints
- fraud monitoring
- analytics and AI recommendations

## NGO matching endpoints
All matching endpoints require JWT authentication. NGO endpoints are scoped to the signed-in NGO; donors can only generate or retrieve recommendations for their own donations.

- `GET /api/matching/profile/` — retrieve or initialize the NGO matching profile.
- `PATCH /api/matching/profile/` — update accepted category IDs, optional coordinate pair, capacity in kilograms, and current demand score (0–100). Reliability and activation are administrator-managed.
- `POST /api/matching/donations/{donation_id}/generate/?limit=10` — donor-only ranked recommendation generation; `limit` must be 1–50. Response labels `score_type` as `weighted_ranking_score` (not a probability).
- `GET /api/matching/donations/{donation_id}/matches/` — retrieve active matches for an owned donation (donor) or the caller's own match (NGO).
- `GET /api/matching/my/` — list active matches for the current donor's donations or the current NGO.
- `POST /api/matching/matches/{recommendation_id}/accept/` — accept an NGO recommendation; validates and transitions the donation transactionally.
- `POST /api/matching/matches/{recommendation_id}/decline/` — decline an NGO recommendation.

Recommendations include NGO name, weighted score (0–100), category compatibility, distance when known, factor scores/weights, explanations, and status. See [MATCHING_ENGINE_DOCUMENTATION.md](MATCHING_ENGINE_DOCUMENTATION.md) for eligibility, scoring formula, configuration, and limitations.

## Admin fraud-alert endpoints
All fraud-alert routes require an authenticated administrator (`role=ADMIN`). Requests from donors, NGOs, and other users receive `403 Forbidden`; unauthenticated requests receive `401 Unauthorized`. Fraud fields are not added to ordinary donation or user responses.

- `GET /api/fraud-detection/alerts/` — paginated alert queue. Optional filters: `status` (`OPEN`, `REVIEWING`, `RESOLVED`), `risk_level` (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), and `search`.
- `GET /api/fraud-detection/alerts/{alert_id}/` — alert details and structured reasons; does not include private pickup addresses or full nested user/donation records.
- `POST /api/fraud-detection/alerts/{alert_id}/review/` — record an outcome and optional note; ordinary outcomes resolve the alert, while `ESCALATED` keeps it in `REVIEWING` for continued human follow-up.

Review request:
```json
{
  "outcome": "FALSE_POSITIVE",
  "note": "Reviewed source information; no policy issue found."
}
```

Allowed outcomes are `NO_ACTION`, `FALSE_POSITIVE`, `POLICY_VIOLATION`, and `ESCALATED`. Re-review of a resolved alert returns `409 Conflict`. Review actions are written to the fraud audit log. Risk scores are rule-based triage signals, not probabilities, and no account restriction is applied automatically.

See [FRAUD_DETECTION_DOCUMENTATION.md](FRAUD_DETECTION_DOCUMENTATION.md) for the rule definitions, score thresholds, and privacy safeguards.
