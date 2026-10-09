import { createContext, useEffect, useMemo, useState } from 'react';

import { authApi, tokenStorage } from '../api/client';

export const AuthContext = createContext(null);

function readStoredUser() {
  try {
    const savedUser = localStorage.getItem('foodshare_user');
    return savedUser ? JSON.parse(savedUser) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => readStoredUser());

  useEffect(() => {
    const accessToken = tokenStorage.getAccessToken();

    if (!accessToken) {
      setUser(null);
      return;
    }

    authApi
      .profile()
      .then(({ data }) => {
        setUser(data);
        localStorage.setItem('foodshare_user', JSON.stringify(data));
      })
      .catch(() => {
        tokenStorage.clearAuth();
        setUser(null);
      });
  }, []);

  const setSession = ({ access, refresh, user: nextUser }) => {
    tokenStorage.persistAuth({ access, refresh, user: nextUser });
    setUser(nextUser);
    return nextUser;
  };

  const login = async (credentials) => {
    const response = await authApi.login(credentials);
    const nextUser = response.data.user;
    setSession({ access: response.data.access, refresh: response.data.refresh, user: nextUser });
    return response;
  };

  const register = async (payload) => {
    const response = await authApi.register(payload);
    const nextUser = response.data.user;
    setSession({ access: response.data.access, refresh: response.data.refresh, user: nextUser });
    return response;
  };

  const logout = () => {
    tokenStorage.clearAuth();
    setUser(null);
  };

  const value = useMemo(
    () => ({
      user,
      setUser,
      login,
      register,
      logout,
    }),
    [user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
