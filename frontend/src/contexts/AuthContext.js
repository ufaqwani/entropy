import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState({
    token: localStorage.getItem('token'),
    isAuthenticated: null,
    loading: true,
    user: null,
  });

  useEffect(() => {
    const loadUser = async () => {
      if (localStorage.token) {
        axios.defaults.headers.common['x-auth-token'] = localStorage.token;
        try {
          const res = await axios.get('/api/auth/user');
          setAuth({
            token: localStorage.token,
            isAuthenticated: true,
            loading: false,
            user: res.data,
          });
        } catch (err) {
          localStorage.removeItem('token');
          setAuth({
            token: null,
            isAuthenticated: false,
            loading: false,
            user: null,
          });
        }
      } else {
        setAuth({
          token: null,
          isAuthenticated: false,
          loading: false,
          user: null,
        });
      }
    };
    loadUser();
  }, []);

  const login = async (formData) => {
    try {
      const res = await axios.post('/api/auth/login', formData);
      localStorage.setItem('token', res.data.token);
      axios.defaults.headers.common['x-auth-token'] = res.data.token;
      const userRes = await axios.get('/api/auth/user');
      setAuth({
        token: res.data.token,
        isAuthenticated: true,
        loading: false,
        user: userRes.data,
      });
    } catch (err) {
      logout();
      throw err;
    }
  };

  const register = async (formData) => {
    try {
      const res = await axios.post('/api/auth/register', formData);
      localStorage.setItem('token', res.data.token);
      axios.defaults.headers.common['x-auth-token'] = res.data.token;
      const userRes = await axios.get('/api/auth/user');
      setAuth({
        token: res.data.token,
        isAuthenticated: true,
        loading: false,
        user: userRes.data,
      });
    } catch (err) {
      logout();
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['x-auth-token'];
    setAuth({
      token: null,
      isAuthenticated: false,
      loading: false,
      user: null,
    });
  };

  return (
    <AuthContext.Provider value={{ ...auth, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
