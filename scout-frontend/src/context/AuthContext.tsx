import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { User, TokenResponse } from "@/types";
import { api } from "@/lib/api";

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => void;
  updateUser: (data: Record<string, unknown>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("scout_token")
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      api
        .getMe()
        .then((u) => setUser(u as User))
        .catch(() => {
          localStorage.removeItem("scout_token");
          setToken(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (email: string, password: string) => {
    const res = (await api.login({ email, password })) as TokenResponse;
    localStorage.setItem("scout_token", res.access_token);
    setToken(res.access_token);
    setUser(res.user);
  };

  const register = async (email: string, password: string, name?: string) => {
    const res = (await api.register({ email, password, name })) as TokenResponse;
    localStorage.setItem("scout_token", res.access_token);
    setToken(res.access_token);
    setUser(res.user);
  };

  const logout = () => {
    localStorage.removeItem("scout_token");
    setToken(null);
    setUser(null);
  };

  const updateUser = async (data: Record<string, unknown>) => {
    const updated = (await api.updateMe(data)) as User;
    setUser(updated);
  };

  return (
    <AuthContext.Provider
      value={{ user, token, loading, login, register, logout, updateUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
