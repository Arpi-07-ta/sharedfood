# FoodShare AI Frontend

This directory contains the React + Vite frontend for FoodShare AI.

## Stack
- React
- Vite
- JavaScript
- Tailwind CSS
- React Router
- Axios
- Recharts
- Lucide React
- React Hot Toast

## Folder structure

```text
frontend/
├── README.md
├── .env.example
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   ├── index.css
│   ├── api/
│   │   └── client.js
│   ├── components/
│   │   ├── auth/
│   │   │   ├── ProtectedRoute.jsx
│   │   │   └── RoleBasedRoute.jsx
│   │   ├── layout/
│   │   │   ├── Footer.jsx
│   │   │   ├── Navbar.jsx
│   │   │   └── Sidebar.jsx
│   │   └── ui/
│   │       ├── Button.jsx
│   │       ├── EmptyState.jsx
│   │       ├── ErrorMessage.jsx
│   │       ├── Input.jsx
│   │       ├── LoadingSpinner.jsx
│   │       ├── Modal.jsx
│   │       ├── Select.jsx
│   │       ├── StatusBadge.jsx
│   │       └── Button.jsx
│   ├── contexts/
│   │   └── AuthContext.jsx
│   ├── hooks/
│   │   └── useAuth.js
│   ├── pages/
│   │   ├── AboutPage.jsx
│   │   ├── AdminPage.jsx
│   │   ├── ContactPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── HomePage.jsx
│   │   ├── HowItWorksPage.jsx
│   │   ├── LoginPage.jsx
│   │   ├── NotFoundPage.jsx
│   │   └── RegisterPage.jsx
│   ├── routes/
│   │   └── AppRoutes.jsx
│   └── utils/
└── public/
```

## Installation

```bash
cd frontend
npm install
```

## Local environment setup

```bash
cp .env.example .env
```

Set the browser-facing API URL as needed:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Start development server

```bash
npm run dev
```

## Production build

```bash
npm run build
```

## Notes
- This frontend is a clean UI scaffold for the initial project phase.
- The pages intentionally avoid claiming backend functionality that is not yet implemented.
- Validation, loading states, routing, and reusable components are included as a base layer for the next implementation stages.
