import React, { useState, useContext } from 'react';
import { Link, Navigate } from 'react-router-dom';
import AuthContext from '../contexts/AuthContext';

const RegisterPage = () => {
  const { register, isAuthenticated } = useContext(AuthContext);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
  });
  const [error, setError] = useState('');

  const { username, email, password, password2 } = formData;

  const onChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    setError(''); // Clear previous errors
    if (password !== password2) {
      setError('Passwords do not match');
    } else {
      try {
        await register({
          username,
          email,
          password,
        });
      } catch (err) {
        setError(err.response?.data?.msg || 'Registration failed. Please try again.');
      }
    }
  };

  if (isAuthenticated) {
    return <Navigate to="/" />;
  }

  return (
    <div className="auth-page">
      <div className="auth-form">
        <h1>Register</h1>
        {error && <p className="error-message">{error}</p>}
        <form onSubmit={onSubmit}>
          <div>
            <input
              type="text"
              placeholder="Username"
              name="username"
              value={username}
              onChange={onChange}
              required
            />
          </div>
          <div>
            <input
              type="email"
              placeholder="Email Address"
              name="email"
              value={email}
              onChange={onChange}
              required
            />
          </div>
          <div>
            <input
              type="password"
              placeholder="Password"
              name="password"
              value={password}
              onChange={onChange}
              minLength="6"
            />
          </div>
          <div>
            <input
              type="password"
              placeholder="Confirm Password"
              name="password2"
              value={password2}
              onChange={onChange}
              minLength="6"
            />
          </div>
          <input type="submit" value="Register" className="btn-primary" />
        </form>
        <p>
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;