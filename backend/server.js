// backend/server.js
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
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

// ===== CORS (preflight-safe, strict to FRONTEND_ORIGIN) =====
const allowedOrigins = (process.env.FRONTEND_ORIGIN || '')
  .split(',')
  .map(s => s.trim())
  .filter(Boolean);

// Optional debug to see incoming Origin on Render
app.use((req, _res, next) => {
  if (process.env.NODE_ENV === 'production' && req.headers.origin) {
    console.log('[CORS] Origin:', req.headers.origin);
  }
  next();
});

app.use(cors({
  origin: function (origin, cb) {
    // Allow server-to-server (no Origin) like curl or health checks
    if (!origin) return cb(null, true);
    // Allow exact matches from env
    if (allowedOrigins.includes(origin)) return cb(null, true);
    // Do NOT throw — respond without CORS so browser blocks it
    return cb(null, false);
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'Accept', 'Origin', 'X-Requested-With']
}));

// Ensure Express answers OPTIONS for all routes with proper headers
app.options('*', cors());

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
  // If CORS origin was not allowed, cors() may have set no headers; we still return 500 JSON for server-side callers.
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
