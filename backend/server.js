// backend/server.js
const express = require('express');
const mongoose = require('mongoose');
const helmet = require('helmet');
const morgan = require('morgan');

// Do NOT rely on dotenv in production on Render; envs are injected by the platform.
// require('dotenv').config();

const taskRoutes = require('./routes/tasks');
const progressRoutes = require('./routes/progress');
const completedTasksRoutes = require('./routes/completedTasks');
const categoryRoutes = require('./routes/categories');
const templateRoutes = require('./routes/templates');
const analyticsRoutes = require('./routes/analytics');
const authRoutes = require('./routes/auth');
// const templateScheduler = require('./services/templateScheduler'); // comment on Render Free (sleeping dyno)

const app = express();
const PORT = process.env.PORT || 5000;

// Loud boot logs
console.log('[BOOT] starting entropy-backend');
console.log('[BOOT] NODE_ENV =', process.env.NODE_ENV);
console.log('[BOOT] PORT (from env) =', process.env.PORT);

try {
  const u = new URL(process.env.MONGODB_URI || 'mongodb://missing');
  console.log('[BOOT] MONGO host =', u.host, ' dbname =', u.pathname || '(none)');
} catch (e) {
  console.log('[BOOT] MONGO uri not set or invalid');
}

// Security & logging
app.use(helmet({ contentSecurityPolicy: false })); // enable CSP later once sources are finalized
app.use(morgan(process.env.NODE_ENV === 'production' ? 'combined' : 'dev'));

// ===== Manual CORS (exact origin, credentials, preflight-safe) =====
const allowedOrigins = (process.env.FRONTEND_ORIGIN || '')
  .split(',')
  .map(s => s.trim())
  .filter(Boolean);

app.use((req, res, next) => {
  const origin = req.headers.origin;

  // Debug: see incoming Origin on Render
  if (process.env.NODE_ENV === 'production' && origin) {
    console.log('[CORS] Origin:', origin);
  }

  if (origin && allowedOrigins.includes(origin)) {
    // Reflect exact allowed origin and allow credentials
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Vary', 'Origin'); // cache safety
    res.setHeader('Access-Control-Allow-Credentials', 'true');
    res.setHeader(
      'Access-Control-Allow-Headers',
      'Content-Type, Authorization, Accept, Origin, X-Requested-With'
    );
    res.setHeader(
      'Access-Control-Allow-Methods',
      'GET,POST,PUT,PATCH,DELETE,OPTIONS'
    );
  }

  // Always answer preflight quickly; do NOT fall through to routes
  if (req.method === 'OPTIONS') {
    return res.sendStatus(204);
  }

  next();
});

// Body parsing
app.use(express.json({ limit: '1mb' })); // raise if you truly need larger payloads
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/tasks', taskRoutes);
app.use('/api/progress', progressRoutes);
app.use('/api/tasks', completedTasksRoutes);
app.use('/api/categories', categoryRoutes);
app.use('/api/templates', templateRoutes);
app.use('/api/analytics', analyticsRoutes);
app.use('/api/auth', authRoutes);

// Health check (public)
app.get('/health', (req, res) => {
  res.status(200).json({ ok: true, message: 'Entropy API is running!' });
});

// Global error handler (keep last)
app.use((err, req, res, next) => {
  console.error('[ERR]', (err && err.stack) || err);
  res.status(500).json({ error: 'Something went wrong!' });
});

// Boot: connect DB then listen
async function start() {
  try {
    if (!process.env.MONGODB_URI) {
      throw new Error('MONGODB_URI env var is required');
    }
    await mongoose.connect(process.env.MONGODB_URI, {
      maxPoolSize: 10,
      serverSelectionTimeoutMS: 5000, // fail fast if cluster unreachable
      socketTimeoutMS: 10000
      // No deprecated options (useNewUrlParser/useUnifiedTopology) on driver v4+
    });
    console.log('[BOOT] Mongo connected');

    console.log('[BOOT] starting HTTP server on', PORT);
    app.listen(PORT, () => {
      console.log('[BOOT] HTTP server listening on', PORT);
    });
  } catch (e) {
    console.error('[FATAL] startup failed:', e);
    process.exit(1);
  }
}

process.on('unhandledRejection', (r) => { console.error('[FATAL] unhandledRejection', r); process.exit(1); });
process.on('uncaughtException', (e) => { console.error('[FATAL] uncaughtException', e); process.exit(1); });

start();

module.exports = app;
