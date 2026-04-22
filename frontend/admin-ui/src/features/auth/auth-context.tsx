import { createContext, useContext, useState, useEffect } from "react";
import { api } from "../../lib/api";
import { loginRequest } from "./api";
import { setToken as storeToken, clearToken, getAccessToken } from "../../lib/token";

type User = {
  email: string;
};

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(null);
  const [isAuthLoading, setIsAuthLoading] = useState(true);

  useEffect(() => {
    async function hydrate() {
      const token = getAccessToken();

      if (!token) {
        setIsAuthLoading(false);
        return;
      }

      try {
        const res = await api.get("/users/me");

        setUser(res.data);
        setTokenState(token);
      } catch {
        clearToken();
        setUser(null);
        setTokenState(null);
      } finally {
        setIsAuthLoading(false);
      }
    }

    hydrate();
  }, []);

  async function login(email: string, password: string) {
    const data = await loginRequest(email, password);

    setUser(data.user ?? { email });
    setTokenState(data.access_token);

    storeToken(data.access_token, data.refresh_token);
  }

  function logout() {
    setUser(null);
    setTokenState(null);
    clearToken();
  }

  return (
    <AuthContext.Provider value={{user, token, isAuthLoading, login, logout, }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}