/**
 * WebSocket Microservice Server
 * Main entry point for the Socket.io server
 */

require('dotenv').config();

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const helmet = require('helmet');

const logger = require('./utils/logger');
const { connectRedis } = require('./config/redis');
const { pool } = require('./config/database');
const { socketAuthMiddleware } = require('./middleware/auth');
const chatHandler = require('./handlers/chatHandler');
const notificationHandler = require('./handlers/notificationHandler');
const onlineStatusService = require('./services/onlineStatusService');

// Configuration
const PORT = process.env.PORT || 3001;
const ALLOWED_ORIGINS = process.env.ALLOWED_ORIGINS
  ? process.env.ALLOWED_ORIGINS.split(',')
  : ['http://localhost:3000', 'http://localhost:8000'];

// Create Express app
const app = express();
const server = http.createServer(app);

// Middleware
app.use(helmet());
app.use(cors({ origin: ALLOWED_ORIGINS }));
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'websocket-service',
    timestamp: new Date().toISOString(),
  });
});

// API endpoint to send notification from Django backend
app.post('/api/notify', async (req, res) => {
  try {
    const { recipientId, type, title, message, metadata } = req.body;

    if (!recipientId || !title || !message) {
      return res.status(400).json({
        success: false,
        error: 'recipientId, title, and message are required',
      });
    }

    const result = await notificationHandler.sendNotificationFromBackend(
      io,
      recipientId,
      { type, title, message, metadata }
    );

    res.json(result);
  } catch (error) {
    logger.error('Error in /api/notify:', error);
    res.status(500).json({ success: false, error: 'Internal server error' });
  }
});

// API endpoint to broadcast notification to college
app.post('/api/broadcast', async (req, res) => {
  try {
    const { collegeId, type, title, message, metadata } = req.body;

    if (!collegeId || !title || !message) {
      return res.status(400).json({
        success: false,
        error: 'collegeId, title, and message are required',
      });
    }

    const result = await notificationHandler.broadcastNotificationFromBackend(
      io,
      collegeId,
      { type, title, message, metadata }
    );

    res.json(result);
  } catch (error) {
    logger.error('Error in /api/broadcast:', error);
    res.status(500).json({ success: false, error: 'Internal server error' });
  }
});

// API endpoint to get online users
app.get('/api/online-users', async (req, res) => {
  try {
    const onlineUsers = await onlineStatusService.getOnlineUsers();
    res.json({ success: true, onlineUsers });
  } catch (error) {
    logger.error('Error in /api/online-users:', error);
    res.status(500).json({ success: false, error: 'Internal server error' });
  }
});

// Initialize Socket.io
const io = new Server(server, {
  cors: {
    origin: ALLOWED_ORIGINS,
    methods: ['GET', 'POST'],
    credentials: true,
  },
  pingTimeout: 60000,
  pingInterval: 25000,
});

// Socket.io authentication middleware
io.use(socketAuthMiddleware);

// Socket.io connection handler
io.on('connection', async (socket) => {
  const user = socket.user;

  logger.info(`User connected: ${user.username} (ID: ${user.id}, Socket: ${socket.id})`);

  // Mark user as online
  await onlineStatusService.setUserOnline(user.id, socket.id);

  // Join user's personal room
  socket.join(`user:${user.id}`);

  // Join college room if user has college
  if (user.collegeId) {
    socket.join(`college:${user.collegeId}`);
    logger.debug(`User ${user.id} joined college room: ${user.collegeId}`);
  }

  // Initialize event handlers
  chatHandler.init(io, socket);
  notificationHandler.init(io, socket);

  // Send online status update to all connected users
  io.emit('user:online', {
    userId: user.id,
    username: user.username,
    fullName: user.fullName,
  });

  // Handle heartbeat
  socket.on('heartbeat', async () => {
    await onlineStatusService.refreshUserOnline(user.id);
    socket.emit('heartbeat:ack', { timestamp: new Date() });
  });

  // Handle disconnection
  socket.on('disconnect', async (reason) => {
    logger.info(`User disconnected: ${user.username} (Socket: ${socket.id}, Reason: ${reason})`);

    // Mark user as offline (or check if they have other active sockets)
    await onlineStatusService.setUserOffline(user.id, socket.id);

    // Check if user is still online (has other sockets)
    const isStillOnline = await onlineStatusService.isUserOnline(user.id);

    if (!isStillOnline) {
      // Send offline status update
      io.emit('user:offline', {
        userId: user.id,
        username: user.username,
      });
    }
  });

  // Error handler
  socket.on('error', (error) => {
    logger.error(`Socket error for user ${user.id}:`, error);
  });
});

// Initialize connections and start server
async function startServer() {
  try {
    // Connect to Redis
    await connectRedis();
    logger.info('Redis connected successfully');

    // Test database connection
    await pool.query('SELECT NOW()');
    logger.info('Database connected successfully');

    // Start server
    server.listen(PORT, () => {
      logger.info(`WebSocket service running on port ${PORT}`);
      logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
      logger.info(`Allowed origins: ${ALLOWED_ORIGINS.join(', ')}`);
    });
  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM signal received: closing HTTP server');
  server.close(() => {
    logger.info('HTTP server closed');
    pool.end();
    process.exit(0);
  });
});

process.on('SIGINT', async () => {
  logger.info('SIGINT signal received: closing HTTP server');
  server.close(() => {
    logger.info('HTTP server closed');
    pool.end();
    process.exit(0);
  });
});

// Start the server
startServer();

module.exports = { app, server, io };
