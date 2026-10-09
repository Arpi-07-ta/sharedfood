import { Navigate, Route, Routes } from 'react-router-dom';

import ProtectedRoute from '../components/auth/ProtectedRoute';
import RoleBasedRoute from '../components/auth/RoleBasedRoute';
import AboutPage from '../pages/AboutPage';
import AdminDashboard from '../pages/AdminDashboard';
import AdminFraudAlertsPage from '../pages/AdminFraudAlertsPage';
import AdminNGOVerificationsPage from '../pages/AdminNGOVerificationsPage';
import AdminPage from '../pages/AdminPage';
import ContactPage from '../pages/ContactPage';
import CreateDonationPage from '../pages/CreateDonationPage';
import DonationDetailsPage from '../pages/DonationDetailsPage';
import DonationHistoryPage from '../pages/DonationHistoryPage';
import DonorDashboard from '../pages/DonorDashboard';
import HomePage from '../pages/HomePage';
import HowItWorksPage from '../pages/HowItWorksPage';
import LoginPage from '../pages/LoginPage';
import MyDonationsPage from '../pages/MyDonationsPage';
import NGODashboard from '../pages/NGODashboard';
import NotFoundPage from '../pages/NotFoundPage';
import RegisterPage from '../pages/RegisterPage';
import UserDashboard from '../pages/UserDashboard';
import VolunteerDashboard from '../pages/VolunteerDashboard';
import VolunteerAssignmentsPage from '../pages/VolunteerAssignmentsPage';
import PickupDetailsPage from '../pages/PickupDetailsPage';
import { useAuth } from '../hooks/useAuth';

function DashboardHome() {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const redirectMap = {
    user: '/dashboard/user',
    donor: '/dashboard/donor',
    ngo: '/dashboard/ngo',
    volunteer: '/dashboard/volunteer',
    admin: '/dashboard/admin',
  };

  return <Navigate to={redirectMap[user.role] || '/dashboard/user'} replace />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/how-it-works" element={<HowItWorksPage />} />
      <Route path="/contact" element={<ContactPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardHome />
          </ProtectedRoute>
        }
      />

      <Route
        path="/dashboard/user"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['user']}>
              <UserDashboard />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />

      <Route
        path="/dashboard/donor"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['donor']}>
              <DonorDashboard />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />

      <Route
        path="/donations/create"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['donor']}>
              <CreateDonationPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />

      <Route
        path="/donations/my"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['donor']}>
              <MyDonationsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />

      <Route
        path="/donations/:id"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['donor']}>
              <DonationDetailsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />

      <Route
        path="/donations/:id/history"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['donor']}>
              <DonationHistoryPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />

      <Route
        path="/dashboard/ngo"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['ngo']}>
              <NGODashboard />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />

      <Route
        path="/dashboard/volunteer"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['volunteer']}>
              <VolunteerDashboard />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />

      <Route
        path="/volunteer/pickups"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['volunteer']}>
              <VolunteerAssignmentsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />

      <Route
        path="/volunteer/pickups/:id"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['volunteer']}>
              <PickupDetailsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />

      <Route
        path="/dashboard/admin"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['admin']}>
              <AdminDashboard />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin"
        element={
          <RoleBasedRoute allowedRoles={['admin']}>
            <AdminPage />
          </RoleBasedRoute>
        }
      />

      <Route
        path="/admin/fraud-alerts"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['admin']}>
              <AdminFraudAlertsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />

      <Route
        path="/admin/ngo-verifications"
        element={
          <ProtectedRoute>
            <RoleBasedRoute allowedRoles={['admin']}>
              <AdminNGOVerificationsPage />
            </RoleBasedRoute>
          </ProtectedRoute>
        }
      />

      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
}

export default AppRoutes;
