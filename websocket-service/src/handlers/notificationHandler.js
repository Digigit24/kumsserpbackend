/**
 * Notification Event Handlers
 * Handles Socket.io events for notifications
 */

const notificationService = require('../services/notificationService');
const onlineStatusService = require('../services/onlineStatusService');
const logger = require('../utils/logger');

class NotificationHandler {
  /**
   * Initialize notification event handlers
   */
  init(io, socket) {
    const user = socket.user;

    // Send notification to specific user
    socket.on('notification:send', async (data, callback) => {
      try {
        const { recipientId, type, title, message, metadata } = data;

        if (!recipientId || !title || !message) {
          return callback({
            success: false,
            error: 'recipientId, title, and message are required',
          });
        }

        // Create notification in database
        const notification = await notificationService.createNotification(
          recipientId,
          type || 'general',
          title,
          message,
          metadata || {}
        );

        // Send to recipient's sockets
        const recipientSockets = await onlineStatusService.getUserSockets(recipientId);
        recipientSockets.forEach((socketId) => {
          io.to(socketId).emit('notification:new', {
            id: notification.id,
            type: notification.notification_type,
            title: notification.title,
            message: notification.message,
            metadata: notification.metadata,
            priority: notification.priority,
            createdAt: notification.created_at,
          });
        });

        callback({ success: true, notification });

        logger.info(`Notification sent to user ${recipientId}`);
      } catch (error) {
        logger.error('Error sending notification:', error);
        callback({ success: false, error: 'Failed to send notification' });
      }
    });

    // Broadcast notification to college
    socket.on('notification:broadcast', async (data, callback) => {
      try {
        const { collegeId, type, title, message, metadata } = data;

        if (!collegeId || !title || !message) {
          return callback({
            success: false,
            error: 'collegeId, title, and message are required',
          });
        }

        // Create notifications for all users in college
        const notifications = await notificationService.broadcastToCollege(
          collegeId,
          type || 'general',
          title,
          message,
          metadata || {}
        );

        // Broadcast to all sockets in the college room
        io.to(`college:${collegeId}`).emit('notification:new', {
          type: type || 'general',
          title: title,
          message: message,
          metadata: metadata || {},
          priority: 'medium',
          createdAt: new Date(),
        });

        callback({ success: true, count: notifications.length });

        logger.info(`Broadcasted notification to college ${collegeId}`);
      } catch (error) {
        logger.error('Error broadcasting notification:', error);
        callback({ success: false, error: 'Failed to broadcast notification' });
      }
    });

    // Get unread notifications
    socket.on('notification:getUnread', async (data, callback) => {
      try {
        const { limit = 50 } = data || {};

        const notifications = await notificationService.getUnreadNotifications(
          user.id,
          limit
        );

        callback({ success: true, notifications });
      } catch (error) {
        logger.error('Error fetching unread notifications:', error);
        callback({ success: false, error: 'Failed to fetch notifications' });
      }
    });

    // Mark notifications as read
    socket.on('notification:markRead', async (data, callback) => {
      try {
        const { notificationIds } = data;

        if (!notificationIds || !Array.isArray(notificationIds)) {
          return callback({
            success: false,
            error: 'notificationIds array is required',
          });
        }

        const count = await notificationService.markNotificationsAsRead(
          notificationIds
        );

        callback({ success: true, count });

        logger.info(`User ${user.id} marked ${count} notifications as read`);
      } catch (error) {
        logger.error('Error marking notifications as read:', error);
        callback({ success: false, error: 'Failed to mark notifications as read' });
      }
    });

    // Get unread count
    socket.on('notification:getUnreadCount', async (data, callback) => {
      try {
        const count = await notificationService.getUnreadCount(user.id);

        callback({ success: true, count });
      } catch (error) {
        logger.error('Error getting unread count:', error);
        callback({ success: false, error: 'Failed to get unread count' });
      }
    });
  }

  /**
   * Send notification from Django backend (via HTTP API)
   */
  async sendNotificationFromBackend(io, recipientId, notificationData) {
    try {
      const { type, title, message, metadata } = notificationData;

      // Create notification in database
      const notification = await notificationService.createNotification(
        recipientId,
        type || 'general',
        title,
        message,
        metadata || {}
      );

      // Send to recipient's sockets
      const recipientSockets = await onlineStatusService.getUserSockets(recipientId);
      recipientSockets.forEach((socketId) => {
        io.to(socketId).emit('notification:new', {
          id: notification.id,
          type: notification.notification_type,
          title: notification.title,
          message: notification.message,
          metadata: notification.metadata,
          priority: notification.priority,
          createdAt: notification.created_at,
        });
      });

      logger.info(`Notification sent from backend to user ${recipientId}`);
      return { success: true, notification };
    } catch (error) {
      logger.error('Error sending notification from backend:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Broadcast notification from Django backend (via HTTP API)
   */
  async broadcastNotificationFromBackend(io, collegeId, notificationData) {
    try {
      const { type, title, message, metadata } = notificationData;

      // Create notifications for all users in college
      const notifications = await notificationService.broadcastToCollege(
        collegeId,
        type || 'general',
        title,
        message,
        metadata || {}
      );

      // Broadcast to all sockets in the college room
      io.to(`college:${collegeId}`).emit('notification:new', {
        type: type || 'general',
        title: title,
        message: message,
        metadata: metadata || {},
        priority: 'medium',
        createdAt: new Date(),
      });

      logger.info(`Broadcasted notification from backend to college ${collegeId}`);
      return { success: true, count: notifications.length };
    } catch (error) {
      logger.error('Error broadcasting notification from backend:', error);
      return { success: false, error: error.message };
    }
  }
}

module.exports = new NotificationHandler();
