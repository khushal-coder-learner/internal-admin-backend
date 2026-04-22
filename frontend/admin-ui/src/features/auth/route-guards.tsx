import { Navigate } from "react-router-dom";
import { useAuth } from "./auth-context";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isAuthLoading } = useAuth();

  if (isAuthLoading) return <div>Loading...</div>;

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export function PublicOnlyRoute({ children }: { children: React.ReactNode }) {
  const { user, isAuthLoading } = useAuth();

  if (isAuthLoading) return null;
  
  if (user) {
    return <Navigate to="/" replace />;
  }

  return children;
}