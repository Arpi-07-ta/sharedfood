# FoodShare AI Backend

This directory contains the Django REST API for FoodShare AI.

## Stack
- Python 3.11+
- Django 5.0
- Django REST Framework
- Simple JWT
- django-cors-headers
- SQLite for local development
- PostgreSQL support via `DATABASE_URL`

## Project structure
- `config/` — project settings, URL routing, and application entry points
- `apps/accounts/` — account and role management
- `apps/donations/` — donation workflows
- `apps/matching/` — partner matching logic
- `apps/tracking/` — fulfillment and delivery tracking
- `apps/notifications/` — notification workflows
- `apps/feedback/` — user feedback and review flow
- `apps/fraud_detection/` — fraud and integrity checks
- `apps/analytics/` — analytics and reporting
- `apps/ai_engine/` — AI-based reasoning and prediction hooks

## Quick start

### 1. Create a virtual environment
Windows PowerShell:
```powershell
cd "A:\final food shared project\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies
```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables
Copy the example file and update values as needed:
```powershell
Copy-Item .env.example .env
```

### 4. Run system checks
```powershell
python manage.py check
```

### 5. Run migrations
```powershell
python manage.py migrate
```

### 6. Start the development server
```powershell
python manage.py runserver 0.0.0.0:8000
```

## Health check
The API exposes a simple health endpoint:

```http
GET /api/health/
```

Example response:
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

## Security notes
- Do not commit a real `.env` file.
- Keep `DJANGO_SECRET_KEY` and `JWT_SECRET_KEY` in environment variables.
- Frontend route checks are only a UX layer; server-side authorization remains required.
