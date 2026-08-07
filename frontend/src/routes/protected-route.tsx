import { Navigate, Outlet, useLocation } from "react-router-dom";

import { Loader } from "@/components/loader";
import { useAuth } from "@/hooks/use-auth";

export function ProtectedRoute() {
  const { isReady, user } = useAuth();
  const location = useLocation();

  if (!isReady) {
    return <main className="grid min-h-screen place-items-center"><Loader className="size-7" /></main>;
  }

  return user ? <Outlet /> : <Navigate replace state={{ from: location }} to="/login" />;
}
