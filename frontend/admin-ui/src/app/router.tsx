import { Routes, Route } from "react-router-dom";
import { AppLayout } from "./layout";
import { ProtectedRoute, PublicOnlyRoute } from "../features/auth/route-guards";
import { LoginPage } from "../features/auth/login-page";
import { UsersPage } from "../features/users/users-page";
import { RecordsPage } from "../features/records/records-page";
import { ActivityLogsPage } from "../features/activity/activity-logs-page";
import { JobsPage } from "../features/jobs/jobs-page";
import { DashboardPage } from "../features/dashboard/dashboard-page";

export function AppRouter() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <PublicOnlyRoute>
            <LoginPage />
          </PublicOnlyRoute>
        }
      />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="users" element={<UsersPage />} />
        <Route path="records" element={<RecordsPage />} />
        <Route path="activity-logs" element={<ActivityLogsPage />}/>
        <Route path="jobs" element={<JobsPage/>} />
      </Route>
    </Routes>
  );
}