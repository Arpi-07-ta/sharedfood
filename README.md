# FoodShare AI

AI-Based Food Wastage Reduction & Donation Tracking System.

## Project goal
FoodShare AI is designed to reduce food waste by predicting surplus patterns, tracking donation flow, and connecting food donors, recipients, and operations teams through a consistent digital workflow.

## Architecture overview
This repository is organized into separate domains:

- `frontend/` — React + Vite + Tailwind single-page application for user dashboards and administration
- `backend/` — Django + Django REST Framework + JWT-based API layer
- `ml/` — Python ML pipeline for forecasting and donation optimization
- `docs/` — system design, API, database, testing, and rollout documentation

## Repository structure

```text
.
├── README.md
├── .gitignore
├── .env.example
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── backend/
│   ├── apps/
│   ├── config/
│   ├── utils/
│   ├── requirements.txt
│   └── manage.py
├── ml/
│   ├── src/
│   ├── data/
│   ├── models/
│   ├── notebooks/
│   ├── scripts/
│   └── requirements.txt
├── docs/
│   ├── PROJECT_DOCUMENTATION.md
│   ├── FRONTEND_DOCUMENTATION.md
│   ├── BACKEND_DOCUMENTATION.md
│   ├── API_DOCUMENTATION.md
│   ├── DATABASE_DOCUMENTATION.md
│   ├── AI_ML_DOCUMENTATION.md
│   └── TESTING_DOCUMENTATION.md
└── .env
```

## Purpose of each directory

- `frontend/`: user-facing web interfaces, interactive dashboards, and client-side API integration
- `backend/`: authentication, business logic, API endpoints, and database access
- `ml/`: data preparation, feature engineering, model training, evaluation, and inference logic
- `docs/`: architecture and operations references for planning, implementation, and maintenance

## Tech stack

### Frontend
- React
- Vite
- JavaScript
- Tailwind CSS
- React Router
- Axios
- Recharts
- Lucide React

### Backend
- Python
- Django
- Django REST Framework
- Simple JWT
- PostgreSQL (production)
- SQLite (local development)

### AI / ML
- Python
- Pandas
- NumPy
- scikit-learn
- Joblib

## Implementation phases checklist

- [ ] Phase 1: project scaffolding and documentation
- [ ] Phase 2: frontend base app and design system setup
- [ ] Phase 3: backend Django project and app module scaffolding
- [ ] Phase 4: PostgreSQL and SQLite configuration strategy
- [ ] Phase 5: authentication and authorization foundation
- [ ] Phase 6: inventory, donation, and waste tracking modules
- [ ] Phase 7: AI prediction pipeline and model training flow
- [ ] Phase 8: dashboard analytics and reporting views
- [ ] Phase 9: API integration and environment configuration
- [ ] Phase 10: testing, validation, and deployment readiness

## Development setup

### 1. Clone and enter the repository

```bash
git clone <repository-url>
cd "final food shared project"
```

### 2. Create the environment files

```bash
cp .env.example .env
```

### 3. Install frontend dependencies

```bash
cd frontend
npm install
```

### 4. Install backend dependencies

```bash
cd ../backend
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 5. Install ML dependencies

```bash
cd ../ml
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 6. Run development servers

```bash
# Frontend
cd frontend
npm run dev

# Backend
cd ../backend
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 7. Train the ML model

```bash
cd ../ml
python scripts/train_model.py
```

## Notes

- This repository is intentionally scaffolded only for the initial architecture and setup phase.
- Business features and production workflows will be implemented in later phases.
- No passwords, secrets, or API keys are committed to version control.
- This project is not claimed as fully working yet; runtime verification will happen after the required dependencies are installed and the application is launched.
