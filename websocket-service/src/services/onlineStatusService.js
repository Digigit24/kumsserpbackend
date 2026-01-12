/**
 * Online Status Service
 * Tracks user online/offline status using Redis
 */

const { redisClient } = require('../config/redis');
const logger = require('../utils/logger');

class OnlineStatusService {
  constructor() {
    this.ONLINE_KEY = 'online_users';
    this.USER_SOCKET_PREFIX = 'user_sockets:';
    this.DEFAULT_TTL = 300; // 5 minutes
  }

  /**
   * Mark user as online
   */
  async setUserOnline(userId, socketId) {
    try {
      // Add user to online users set
      await redisClient.sAdd(this.ONLINE_KEY, String(userId));

      // Store socket ID for the user (allows multiple sockets per user)
      await redisClient.sAdd(`${this.USER_SOCKET_PREFIX}${userId}`, socketId);

      // Set TTL for user online status
      await redisClient.setEx(
        `online:user:${userId}`,
        this.DEFAULT_TTL,
        '1'
      );

      logger.debug(`User ${userId} marked as online (socket: ${socketId})`);
      return true;
    } catch (error) {
      logger.error(`Error setting user ${userId} online:`, error);
      return false;
    }
  }

  /**
   * Mark user as offline (remove specific socket)
   */
  async setUserOffline(userId, socketId) {
    try {
      // Remove socket ID
      await redisClient.sRem(`${this.USER_SOCKET_PREFIX}${userId}`, socketId);

      // Check if user has any other active sockets
      const socketCount = await redisClient.sCard(`${this.USER_SOCKET_PREFIX}${userId}`);

      if (socketCount === 0) {
        // No more active sockets, mark user as offline
        await redisClient.sRem(this.ONLINE_KEY, String(userId));
        await redisClient.del(`online:user:${userId}`);
        logger.info(`User ${userId} marked as offline`);
      } else {
        logger.debug(`User ${userId} still has ${socketCount} active socket(s)`);
      }

      return true;
    } catch (error) {
      logger.error(`Error setting user ${userId} offline:`, error);
      return false;
    }
  }

  /**
   * Check if user is online
   */
  async isUserOnline(userId) {
    try {
      const exists = await redisClient.exists(`online:user:${userId}`);
      return exists === 1;
    } catch (error) {
      logger.error(`Error checking if user ${userId} is online:`, error);
      return false;
    }
  }

  /**
   * Get all online users
   */
  async getOnlineUsers() {
    try {
      const users = await redisClient.sMembers(this.ONLINE_KEY);
      return users;
    } catch (error) {
      logger.error('Error getting online users:', error);
      return [];
    }
  }

  /**
   * Get socket IDs for a user
   */
  async getUserSockets(userId) {
    try {
      const sockets = await redisClient.sMembers(`${this.USER_SOCKET_PREFIX}${userId}`);
      return sockets;
    } catch (error) {
      logger.error(`Error getting sockets for user ${userId}:`, error);
      return [];
    }
  }

  /**
   * Refresh user's online status TTL
   */
  async refreshUserOnline(userId) {
    try {
      await redisClient.expire(`online:user:${userId}`, this.DEFAULT_TTL);
      return true;
    } catch (error) {
      logger.error(`Error refreshing online status for user ${userId}:`, error);
      return false;
    }
  }

  /**
   * Get online status for multiple users
   */
  async getOnlineStatusBulk(userIds) {
    try {
      const pipeline = redisClient.multi();

      userIds.forEach((userId) => {
        pipeline.exists(`online:user:${userId}`);
      });

      const results = await pipeline.exec();

      const onlineStatus = {};
      userIds.forEach((userId, index) => {
        onlineStatus[userId] = results[index] === 1;
      });

      return onlineStatus;
    } catch (error) {
      logger.error('Error getting bulk online status:', error);
      return {};
    }
  }
}

module.exports = new OnlineStatusService();
