/**
 * Authentication Middleware
 * Validates Django REST Framework tokens
 */

const { query } = require('../config/database');
const logger = require('../utils/logger');

/**
 * Authenticate user from Django token
 * @param {string} token - Django REST Framework token
 * @returns {Object|null} User object or null
 */
async function authenticateToken(token) {
  if (!token) {
    logger.warn('No token provided');
    return null;
  }

  try {
    // Query Django's authtoken_token table
    const result = await query(
      `SELECT t.key, t.user_id, u.id, u.username, u.first_name, u.last_name, u.email, u.college_id
       FROM authtoken_token t
       JOIN accounts_user u ON t.user_id = u.id
       WHERE t.key = $1 AND u.is_active = true`,
      [token]
    );

    if (result.rows.length === 0) {
      logger.warn('Invalid token or inactive user');
      return null;
    }

    const user = result.rows[0];
    logger.debug(`User authenticated: ${user.username} (ID: ${user.id})`);

    return {
      id: user.id,
      username: user.username,
      firstName: user.first_name,
      lastName: user.last_name,
      email: user.email,
      collegeId: user.college_id,
      fullName: `${user.first_name} ${user.last_name}`.trim() || user.username,
    };
  } catch (error) {
    logger.error('Error authenticating token:', error);
    return null;
  }
}

/**
 * Socket.io authentication middleware
 */
function socketAuthMiddleware(socket, next) {
  const token = socket.handshake.auth.token || socket.handshake.query.token;

  if (!token) {
    logger.warn('Socket connection attempt without token');
    return next(new Error('Authentication token required'));
  }

  authenticateToken(token)
    .then((user) => {
      if (!user) {
        return next(new Error('Invalid authentication token'));
      }

      socket.user = user;
      logger.info(`Socket authenticated for user: ${user.username} (ID: ${user.id})`);
      next();
    })
    .catch((error) => {
      logger.error('Socket authentication error:', error);
      next(new Error('Authentication failed'));
    });
}

module.exports = {
  authenticateToken,
  socketAuthMiddleware,
};
