import { createContext, useContext, useEffect, useState } from "react";
import { api, getTokens, setTokens } from "../lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(getTokens()));

  useEffect(() => {
    let active = true;
    async function loadUser() {
      if (!getTokens()) {
        if (active) {
          setUser(null);
          setLoading(false);
        }
        return;
      }
      try {
        const me = await api("/auth/me");
        if (active) setUser(me);
      } catch {
        if (active) setUser(null);
      } finally {
        if (active) setLoading(false);
      }
    }
    loadUser();
    window.addEventListener("eventdesk:auth", loadUser);
    return () => {
      active = false;
      window.removeEventListener("eventdesk:auth", loadUser);
    };
  }, []);

  async function signIn(email, password) {
    const tokens = await api("/auth/login", {
      method: "POST",
      body: { email, password },
      auth: false,
    });
    setTokens(tokens);
    const me = await api("/auth/me");
    setUser(me);
    return me;
  }

  async function register(details) {
    const tokens = await api("/auth/register", {
      method: "POST",
      body: details,
      auth: false,
    });
    setTokens(tokens);
    const me = await api("/auth/me");
    setUser(me);
    return me;
  }

  async function signOut() {
    const refreshToken = getTokens()?.refresh_token;
    try {
      if (refreshToken)
        await api("/auth/logout", {
          method: "POST",
          body: { refresh_token: refreshToken },
          auth: false,
        });
    } finally {
      setTokens(null);
      setUser(null);
    }
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, signIn, register, signOut, setUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
