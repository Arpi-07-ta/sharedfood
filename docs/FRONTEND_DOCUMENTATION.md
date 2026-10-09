# Frontend Documentation

## Purpose
The frontend delivers the user-facing product experience for FoodShare AI, with a sustainability-focused design, public marketing pages, and protected application routes for operational workflows.

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

## Actual component library
The current implementation includes reusable components for a production-style interface:

- Navbar
- Footer
- Sidebar
- DashboardLayout
- SummaryCard
- ChartCard
- FilterBar
- DataTable
- Button
- Input
- Select
- Modal
- LoadingSpinner
- ErrorMessage
- EmptyState
- StatusBadge
- ProtectedRoute
- RoleBasedRoute

## Folder structure
- `src/components/layout/` — shared app shell and navigation layout elements
- `src/components/dashboard/` — reusable dashboard widgets and layout composition blocks
- `src/components/ui/` — reusable control and content blocks
- `src/components/auth/` — route protection and role-based access guards
- `src/pages/` — landing, auth, dashboard, and error pages
- `src/api/` — centralized Axios client configuration
- `src/routes/` — route registration
- `src/contexts/` — auth state management
- `src/hooks/` — custom hooks
- `src/utils/` — helper functions and shared data

## Public pages
- HomePage
- AboutPage
- HowItWorksPage
- ContactPage
- LoginPage
- RegisterPage
- NotFoundPage

## Dashboard route map
- `/dashboard` — redirect logic based on the authenticated role
- `/dashboard/user` — UserDashboard
- `/dashboard/donor` — DonorDashboard
- `/dashboard/ngo` — NGODashboard
- `/dashboard/volunteer` — VolunteerDashboard
- `/dashboard/admin` — AdminDashboard
- `/admin` — admin-only legacy route wrapper

## Dashboard layout structure
The dashboard layout is composed as follows:
- `DashboardLayout` wraps the page in a consistent shell with:
  - a left sidebar
  - a top navigation row
  - notification badge
  - profile menu and logout control
  - responsive content panel
- `Sidebar` receives role-specific navigation items and keeps the left navigation consistent across all dashboard variants.
- `SummaryCard` presents role-specific status highlights.
- `ChartCard` handles chart panels and consistent spacing.
- `FilterBar` provides quick status segmentation.
- `DataTable` displays the current placeholder or live table rows in a consistent format.
- `StatusBadge` keeps labels and state colors aligned across all roles.

## Role-specific dashboard responsibilities
- UserDashboard: donation requests, pickups, notifications, and tracking views
- DonorDashboard: live donation and NGO matching recommendations
- NGODashboard: needs, matches, route coordination, and allocation planning placeholders
- VolunteerDashboard: pickup schedules, route assignments, and field updates placeholders
- AdminDashboard: governance overview with a link to the live fraud-alert review queue
- AdminFraudAlertsPage: paginated admin-only risk alerts, explanations, and human review outcomes

## Security and backend state guidance
- Frontend route guards are implemented for access control, but they are not a substitute for server-side authorization.
- Fraud scores and signal details are fetched only from backend endpoints protected by the admin role; donor and NGO dashboards do not display those internal signals.
- Fraud alerts are rule-based review aids and the UI explicitly states that a flag never automatically bans or restricts an account.
- All dashboard pages intentionally show a clear loading, empty, or backend-unavailable state when the API is not connected.
- The interface does not claim real statistics or fake API success responses before backend data exists.

## Design principles
- keep UI components reusable and modular
- separate layout, business logic, and page content
- keep environment-driven configuration in `.env`
- provide accessible forms, validation, loading, and error states
- avoid claiming backend connectivity when the app is only a frontend shell

## Local development commands
```bash
cd frontend
npm install
npm run dev
```

## Production build validation
```bash
cd frontend
npm run build
```

## Environment variables
The frontend uses the `VITE_API_BASE_URL` variable for the API client base URL. A local example file is provided in `frontend/.env.example`.
