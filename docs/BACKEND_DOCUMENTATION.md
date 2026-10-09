# Backend Documentation

## Purpose
The backend provides the application API, business rules, persistence layer, security policies, and integration points for FoodShare AI.

## Stack
- Python 3.11+
- Django 5.0
- Django REST Framework
- django-cors-headers
- djangorestframework-simplejwt
- SQLite for local development
- PostgreSQL support through `DATABASE_URL`

## Project structure
- `config/` — Django settings, project routing, health endpoint
- `apps/accounts/` — user and role management, JWT auth endpoints
- `apps/donations/` — donation lifecycle, validation, status transitions, image uploads
- `apps/matching/` — donation-to-need matching logic
- `apps/tracking/` — fulfillment and logistic tracking
- `apps/notifications/` — user and system notifications
- `apps/feedback/` — reviews and feedback management
- `apps/fraud_detection/` — suspicious activity and risk checks
- `apps/analytics/` — reporting and metrics aggregation
- `apps/ai_engine/` — ML and AI integration layer

## Settings and configuration
The Django settings are environment-driven and support the following:
- `.env` file loading with `python-dotenv`
- `DATABASE_URL` support for PostgreSQL and SQLite fallback
- `CORS_ALLOWED_ORIGINS` for the local Vite frontend
- `JWTAuthentication` with `SimpleJWT`
- media and static file settings
- versioned API defaults via request header-based versioning
- logging to console and file
- transaction-based update routines for donation lifecycle transitions

## Donation module
The donation module implements donor lifecycle management and history tracking for listing, editing, cancellation, validation, and image handling.

### Donation endpoints
```http
GET /api/donations/
GET /api/donations/my/
POST /api/donations/
GET /api/donations/{id}/
PATCH /api/donations/{id}/
POST /api/donations/{id}/cancel/
GET /api/donations/{id}/status-history/
GET /api/donations/categories/
```

### Validation rules
- only authenticated donors can create donations
- donors can edit only donations they own and only while the donation remains editable
- quantity must be greater than zero
- asset expiry must be in the future
- preparation time must not be after expiry time
- invalid images are rejected
- expired items are excluded from the available list
- completed or picked-up donations cannot be reset to `AVAILABLE`
- invalid transitions raise a `400 Bad Request` with a clear status error

### Donation lifecycle model
The donation lifecycle relies on the `FoodDonation` model and a companion `DonationStatusHistory` model for tracing every status change.

## Health endpoint
The backend exposes a health check endpoint:

```http
GET /api/health/
```

Response example:
```json
{
  "status": "ok",
  "message": "FoodShare AI API is running.",
  "service": "foodshare-ai",
  "environment": "development",
  "timestamp": "2026-10-09T00:00:00+00:00",
  "version": "v1"
}
```

## Local development
```powershell
cd "A:\final food shared project\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py check
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## Security guidance
- Keep secrets in `.env` and never commit the real file.
- Use Django settings and DRF permissions for production authorization.
- Frontend checks are not a replacement for backend access control.
- Sensitive fields such as password values are not returned from authenticated profile endpoints.
- Fraud alert list/detail/review APIs require the backend `IsAdmin` permission; frontend route guards are only navigation controls.
- Internal fraud scores, reasons, and deduplication keys are omitted from ordinary donor/NGO responses.
- Rule-based fraud flags are for human review only. They never automatically ban, suspend, or block users or donations.
- Admin review outcomes are recorded in `AuditLog`; audit entries are read-only in Django Admin.

## Fraud and risk review
Donation creation, updates, and cancellations call a separate rule-based fraud service. The scoring service records deduplicated alerts but does not block the donation operation. Thresholds and scoring windows are configurable through `FRAUD_*` environment variables. Complaint signals count open/reviewing complaints attached to a donor's donations, not complaints filed by the donor. See the API documentation for the restricted review endpoints and [AI_ML_DOCUMENTATION.md](AI_ML_DOCUMENTATION.md) for rule limitations.
Detailed signal definitions and operating guidance are in [FRAUD_DETECTION_DOCUMENTATION.md](FRAUD_DETECTION_DOCUMENTATION.md).

## API versioning
The project uses DRF header-based API versioning with the default version set to `v1`.
