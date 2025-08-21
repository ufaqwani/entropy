// backend/middleware/auth.js
const jwt = require('jsonwebtoken');

module.exports = function requireAuth(req, res, next) {
  // Accept token from cookie, Authorization: Bearer, or legacy x-auth-token
  const authHeader = req.headers.authorization || '';
  const bearer = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : null;
  const token = req.cookies?.jwt || req.header('x-auth-token') || bearer;

  if (!token) {
    return res.status(401).json({ msg: 'No token, authorization denied' });
  }

  const secret = process.env.JWT_SECRET;
  if (!secret) {
    // Misconfiguration — backend env must have JWT_SECRET set
    return res.status(500).json({ msg: 'Server misconfigured: JWT_SECRET missing' });
  }

  try {
    const decoded = jwt.verify(token, secret);
    // Some code signs { user: {...} }, others sign the user directly
    req.user = decoded.user || decoded;
    return next();
  } catch (err) {
    return res.status(401).json({ msg: 'Token is not valid' });
  }
};
