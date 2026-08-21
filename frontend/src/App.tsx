import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { RedirectToSignIn, useAuth } from '@clerk/clerk-react';
import LoadingSpinner from './components/LoadingSpinner';
import ClerkTokenProvider from './components/ClerkTokenProvider';
import Layout from './components/Layout';
import AdminLayout from './components/AdminLayout';
import ProtectedRoute from './components/ProtectedRoute';

// Customer Pages
import HomePage from './pages/HomePage';
import ThemeGalleryPage from './pages/ThemeGalleryPage';
import UploadPage from './pages/UploadPage';
import GenerationProgressPage from './pages/GenerationProgressPage';
import PreviewPage from './pages/PreviewPage';
import ProductOptionsPage from './pages/ProductOptionsPage';
import CheckoutPage from './pages/CheckoutPage';
import ConfirmationPage from './pages/ConfirmationPage';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import TermsPage from './pages/TermsPage';
import NotFoundPage from './pages/NotFoundPage';

// Admin Pages
import AdminLoginPage from './pages/admin/AdminLoginPage';
import AdminOrdersPage from './pages/admin/AdminOrdersPage';
import AdminOrderDetailPage from './pages/admin/AdminOrderDetailPage';
import AdminThemesPage from './pages/admin/AdminThemesPage';
import AdminCostsPage from './pages/admin/AdminCostsPage';
import AdminUsersPage from './pages/admin/AdminUsersPage';

/** Wraps customer routes that require Clerk sign-in */
function RequireAuth({ children }: { children: React.ReactNode }) {
  const { isLoaded, isSignedIn } = useAuth();
  
  if (!isLoaded) {
    // Clerk still loading — show spinner instead of redirecting
    return (
      <div className="flex justify-center items-center py-24">
        <LoadingSpinner size="lg" />
      </div>
    );
  }
  
  if (!isSignedIn) {
    return <RedirectToSignIn />;
  }
  
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <ClerkTokenProvider>
      <Routes>
        {/* Customer routes inside Layout (navbar + footer) */}
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="themes" element={<ThemeGalleryPage />} />
          <Route path="privacy" element={<PrivacyPolicyPage />} />
          <Route path="terms" element={<TermsPage />} />
          
          {/* These routes require Clerk sign-in */}
          <Route path="upload" element={<RequireAuth><UploadPage /></RequireAuth>} />
          <Route path="order/:id/progress" element={<RequireAuth><GenerationProgressPage /></RequireAuth>} />
          <Route path="order/:id/preview" element={<RequireAuth><PreviewPage /></RequireAuth>} />
          <Route path="order/:id/options" element={<RequireAuth><ProductOptionsPage /></RequireAuth>} />
          <Route path="order/:id/checkout" element={<RequireAuth><CheckoutPage /></RequireAuth>} />
          <Route path="order/:id/confirmation" element={<RequireAuth><ConfirmationPage /></RequireAuth>} />
        </Route>
        
        {/* Admin routes (separate auth system) */}
        <Route path="/admin/login" element={<AdminLoginPage />} />
        <Route path="/admin" element={<ProtectedRoute><AdminLayout /></ProtectedRoute>}>
          <Route index element={<Navigate to="/admin/orders" replace />} />
          <Route path="orders" element={<AdminOrdersPage />} />
          <Route path="orders/:id" element={<AdminOrderDetailPage />} />
          <Route path="themes" element={<AdminThemesPage />} />
          <Route path="costs" element={<AdminCostsPage />} />
          <Route path="users" element={<AdminUsersPage />} />
        </Route>
        
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
      </ClerkTokenProvider>
    </BrowserRouter>
  );
}
