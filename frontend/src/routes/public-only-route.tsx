import { Navigate, Outlet } from "react-router-dom";

import { Loader } from "@/components/loader";
import { useAuth } from "@/hooks/use-auth";

export function PublicOnlyRoute() {
  const { isReady, user } = useAuth();

  if (!isReady) {
    return <main className="grid min-h-screen place-items-center"><Loader className="size-7" /></main>;
  }

  return user ? <Navigate replace to="/dashboard" /> : <Outlet />;
}
