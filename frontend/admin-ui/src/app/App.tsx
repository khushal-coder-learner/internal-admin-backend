import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "../lib/query-client";
import { AuthProvider } from "../features/auth/auth-context";
import { AppRouter } from "./router";

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AppRouter />
      </AuthProvider>
    </QueryClientProvider>
  );
}