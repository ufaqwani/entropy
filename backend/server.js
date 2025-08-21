// backend/server.js
const cookieParser = require('cookie-parser');
const express = require('express');
const mongoose = require('mongoose');
const helmet = require('helmet');
const morgan = require('morgan');

// Routes
const taskRoutes = require('./routes/tasks');
const progressRoutes = require('./routes/progress');
const completedTasksRoutes = require('./routes/completedTasks');
const categoryRoutes = require('./routes/categories');
const templateRoutes = require('./routes/templates');
const analyticsRoutes = require('./routes/analytics');
const authRoutes = require('./routes/auth');

const app = express();
// Make Express trust Render/Cloudflare proxy so secure cookies work
app.set('trust proxy', 1);
const PORT = process.env.PORT || 5000;

// Boot logs
console.log('[BOOT] starting entropy-backend');
console.log('[BOOT] NODE_ENV =', process.env.NODE_ENV);
console.log('[BOOT] PORT (from env) =', process.env.PORT);

try {
  const u = new URL(process.env.MONGODB_URI || 'mongodb://missing');
  console.log('[BOOT] MONGO host =', u.host, ' dbname =', u.pathname || '(none)');
} catch {
  console.log('[BOOT] MONGO uri not set or invalid');
}

// Security & logging
app.use(helmet({ contentSecurityPolicy: false }));
app.use(morgan(process.env.NODE_ENV === 'production' ? 'combined' : 'dev'));

// ===== Manual CORS (normalized origin, credentials, preflight-safe) =====
function normOrigin(input) {
  if (!input) return '';
  try {
    const u = new URL(input);
    // normalize to "protocol://host" (no trailing slash, no path)
    return `${u.protocol}//${u.host}`;
  } catch {
    // fallback: just strip trailing slashes
    return String(input).replace(/\/+$/, '');
  }
}

const allowedOriginsRaw = (process.env.FRONTEND_ORIGIN || '')
  .split(',')
  .map(s => s.trim())
  .filter(Boolean);

const allowedOrigins = allowedOriginsRaw.map(normOrigin);

// Boot log for diagnostics
console.log('[CORS] Allowed origins (normalized):', allowedOrigins);

app.use((req, res, next) => {
  const reqOrigin = req.headers.origin || '';
  const normReqOrigin = normOrigin(reqOrigin);

  // Debug incoming origin
  if (reqOrigin) {
    console.log('[CORS] Incoming Origin:', reqOrigin, '-> normalized:', normReqOrigin);
  }

  if (reqOrigin && allowedOrigins.includes(normReqOrigin)) {
    // Reflect exact original origin and allow credentials
    res.setHeader('Access-Control-Allow-Origin', reqOrigin);
    res.setHeader('Vary', 'Origin');
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

  if (req.method === 'OPTIONS') {
    // Send 204 with headers intact
    return res.status(204).end();
  }

  next();
});



// Body parsing
app.use(cookieParser());
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/tasks', taskRoutes);
app.use('/api/progress', progressRoutes);
app.use('/api/tasks', completedTasksRoutes);
app.use('/api/categories', categoryRoutes);
app.use('/api/templates', templateRoutes);
app.use('/api/analytics', analyticsRoutes);
app.use('/api/auth', authRoutes);

// Health check
app.get('/health', (req, res) => {
  res.status(200).json({ ok: true, message: 'Entropy API is running!' });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('[ERR]', (err && err.stack) || err);
  res.status(500).json({ error: 'Something went wrong!' });
});

// Boot DB + server
async function start() {
  try {
    if (!process.env.MONGODB_URI) {
      throw new Error('MONGODB_URI env var is required');
    }
    await mongoose.connect(process.env.MONGODB_URI, {
      maxPoolSize: 10,
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 10000,
    });
    console.log('[BOOT] Mongo connected');

    app.listen(PORT, () => {
      console.log('[BOOT] HTTP server listening on', PORT);
    });
  } catch (e) {
    console.error('[FATAL] startup failed:', e);
    process.exit(1);
  }
}

process.on('unhandledRejection', (r) => {
  console.error('[FATAL] unhandledRejection', r);
  process.exit(1);
});
process.on('uncaughtException', (e) => {
  console.error('[FATAL] uncaughtException', e);
  process.exit(1);
});

start();

module.exports = app;
