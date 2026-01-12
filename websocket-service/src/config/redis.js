/**
 * Redis Configuration
 * Used for pub/sub and online status tracking
 */

const redis = require('redis');
const logger = require('../utils/logger');

const redisUrl = process.env.REDIS_URL || 'redis://localhost:6379';

// Create Redis clients
const redisClient = redis.createClient({
  url: redisUrl,
  socket: {
    reconnectStrategy: (retries) => {
      if (retries > 10) {
        logger.error('Redis reconnection failed after 10 attempts');
        return new Error('Redis reconnection failed');
      }
      return Math.min(retries * 100, 3000);
    },
  },
});

const redisPubClient = redis.createClient({
  url: redisUrl,
});

const redisSubClient = redis.createClient({
  url: redisUrl,
});

// Error handlers
redisClient.on('error', (err) => logger.error('Redis Client Error:', err));
redisPubClient.on('error', (err) => logger.error('Redis Pub Client Error:', err));
redisSubClient.on('error', (err) => logger.error('Redis Sub Client Error:', err));

// Connection handlers
redisClient.on('connect', () => logger.info('Redis client connected'));
redisPubClient.on('connect', () => logger.info('Redis pub client connected'));
redisSubClient.on('connect', () => logger.info('Redis sub client connected'));

// Connect all clients
const connectRedis = async () => {
  try {
    await Promise.all([
      redisClient.connect(),
      redisPubClient.connect(),
      redisSubClient.connect(),
    ]);
    logger.info('All Redis clients connected successfully');
  } catch (error) {
    logger.error('Failed to connect to Redis:', error);
    throw error;
  }
};

module.exports = {
  redisClient,
  redisPubClient,
  redisSubClient,
  connectRedis,
};
