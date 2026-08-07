import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AuthProvider } from "@/context/auth-context";
import { AppLayout } from "@/layouts/app-layout";
import { AuthLayout } from "@/layouts/auth-layout";
import { DashboardPage } from "@/pages/dashboard-page";
import { CreateTripPage } from "@/pages/create-trip-page";
import { EditTripPage } from "@/pages/edit-trip-page";
import { LandingPage } from "@/pages/landing-page";
import { LoginPage } from "@/pages/login-page";
import { RegisterPage } from "@/pages/register-page";
import { TripDetailsPage } from "@/pages/trip-details-page";
import { TripsPage } from "@/pages/trips-page";
import { ProtectedRoute } from "@/routes/protected-route";
import { PublicOnlyRoute } from "@/routes/public-only-route";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route element={<LandingPage />} path="/" />
            <Route element={<PublicOnlyRoute />}>
              <Route element={<AuthLayout />}>
                <Route element={<LoginPage />} path="/login" />
                <Route element={<RegisterPage />} path="/register" />
              </Route>
            </Route>
            <Route element={<ProtectedRoute />}>
              <Route element={<AppLayout />}>
                <Route element={<DashboardPage />} path="/dashboard" />
                <Route element={<TripsPage />} path="/trips" />
                <Route element={<CreateTripPage />} path="/trips/new" />
                <Route element={<TripDetailsPage />} path="/trips/:tripId" />
                <Route element={<EditTripPage />} path="/trips/:tripId/edit" />
              </Route>
            </Route>
            <Route element={<Navigate replace to="/" />} path="*" />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
