// backend/routes/auth.js
const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const router = express.Router();

const User = require('../models/User');
const auth = require('../middleware/auth'); // must read cookie/authorization as updated

// --- helpers ---------------------------------------------------------------

function getJwtSecret() {
  const secret = process.env.JWT_SECRET;
  if (!secret) {
    // Fail fast: the server is misconfigured
    throw new Error('JWT_SECRET env var is required');
  }
  return secret;
}

function signToken(payload) {
  return jwt.sign(payload, getJwtSecret(), { expiresIn: '7d' });
}

function setAuthCookie(res, token) {
  // Cross-site cookie so Netlify (frontend) -> Render (backend) works
  res.cookie('jwt', token, {
    httpOnly: true,
    secure: true,     // requires HTTPS; Render is HTTPS, Netlify is HTTPS
    sameSite: 'none', // critical for cross-site
    path: '/',
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
  });
}

// --- routes ----------------------------------------------------------------

// @route   POST /api/auth/register
// @desc    Register a new user and set auth cookie
// @access  Public
router.post('/register', async (req, res) => {
  try {
    let { username, email, password } = req.body || {};

    if (!email || !password) {
      return res.status(400).json({ msg: 'Email and password are required' });
    }

    email = String(email).toLowerCase().trim();
    if (username) username = String(username).trim();

    let user = await User.findOne({ email });
    if (user) {
      return res.status(409).json({ msg: 'User already exists' });
    }

    const salt = await bcrypt.genSalt(10);
    const hash = await bcrypt.hash(password, salt);

    user = await User.create({ username, email, password: hash });

    const token = signToken({ user: { id: user._id, email: user.email } });
    setAuthCookie(res, token);

    return res.status(201).json({
      ok: true,
      user: { id: user._id, email: user.email, username: user.username || null },
    });
  } catch (err) {
    console.error('[AUTH register]', err);
    return res.status(500).json({ msg: 'Registration failed' });
  }
});

// @route   POST /api/auth/login
// @desc    Authenticate user, set auth cookie
// @access  Public
router.post('/login', async (req, res) => {
  try {
    let { email, password } = req.body || {};
    if (!email || !password) {
      return res.status(400).json({ msg: 'Email and password are required' });
    }

    email = String(email).toLowerCase().trim();

    const user = await User.findOne({ email });
    if (!user) {
      return res.status(400).json({ msg: 'Invalid credentials' });
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(400).json({ msg: 'Invalid credentials' });
    }

    const token = signToken({ user: { id: user._id, email: user.email } });
    setAuthCookie(res, token);

    return res.status(200).json({
      ok: true,
      user: { id: user._id, email: user.email, username: user.username || null },
    });
  } catch (err) {
    console.error('[AUTH login]', err);
    return res.status(500).json({ msg: 'Login failed' });
  }
});

// @route   GET /api/auth/user
// @desc    Get current user from cookie/JWT (auth middleware must populate req.user)
// @access  Private
router.get('/user', auth, async (req, res) => {
  try {
    const userId = req.user?.id || req.user?._id;
    if (!userId) {
      return res.status(401).json({ msg: 'Token invalid' });
    }

    const user = await User.findById(userId).select('_id email username');
    if (!user) return res.status(404).json({ msg: 'User not found' });

    return res.json({ ok: true, user: { id: user._id, email: user.email, username: user.username || null } });
  } catch (err) {
    console.error('[AUTH user]', err);
    return res.status(500).json({ msg: 'Server error' });
  }
});

// @route   POST /api/auth/logout
// @desc    Clear auth cookie
// @access  Public (idempotent)
router.post('/logout', (req, res) => {
  // Mirror cookie attributes to ensure the browser actually removes it
  res.clearCookie('jwt', { path: '/', sameSite: 'none', secure: true });
  return res.json({ ok: true });
});

module.exports = router;
