/**
 * Notification Service
 * Handles notification operations
 */

const { query } = require('../config/database');
const logger = require('../utils/logger');

class NotificationService {
  /**
   * Create a new notification
   */
  async createNotification(recipientId, type, title, message, metadata = {}) {
    try {
      const result = await query(
        `INSERT INTO notification
         (recipient_id, notification_type, title, message, metadata,
          is_read, is_sent, priority, created_at, updated_at, is_active)
         VALUES ($1, $2, $3, $4, $5, false, false, 'medium', NOW(), NOW(), true)
         RETURNING id, recipient_id, notification_type, title, message, metadata,
                   priority, created_at`,
        [recipientId, type, title, message, JSON.stringify(metadata)]
      );

      logger.info(`Notification created: ${result.rows[0].id} for user ${recipientId}`);
      return result.rows[0];
    } catch (error) {
      logger.error('Error creating notification:', error);
      throw error;
    }
  }

  /**
   * Get unread notifications for a user
   */
  async getUnreadNotifications(userId, limit = 50) {
    try {
      const result = await query(
        `SELECT id, notification_type, title, message, metadata, priority, created_at
         FROM notification
         WHERE recipient_id = $1 AND is_read = false AND is_active = true
         ORDER BY created_at DESC
         LIMIT $2`,
        [userId, limit]
      );

      return result.rows;
    } catch (error) {
      logger.error('Error fetching unread notifications:', error);
      throw error;
    }
  }

  /**
   * Mark notifications as read
   */
  async markNotificationsAsRead(notificationIds) {
    try {
      const result = await query(
        `UPDATE notification
         SET is_read = true, read_at = NOW()
         WHERE id = ANY($1::uuid[]) AND is_read = false
         RETURNING id`,
        [notificationIds]
      );

      logger.info(`Marked ${result.rowCount} notifications as read`);
      return result.rowCount;
    } catch (error) {
      logger.error('Error marking notifications as read:', error);
      throw error;
    }
  }

  /**
   * Get notification count for a user
   */
  async getUnreadCount(userId) {
    try {
      const result = await query(
        `SELECT COUNT(*) as count
         FROM notification
         WHERE recipient_id = $1 AND is_read = false AND is_active = true`,
        [userId]
      );

      return parseInt(result.rows[0].count, 10);
    } catch (error) {
      logger.error('Error getting unread notification count:', error);
      return 0;
    }
  }

  /**
   * Broadcast notification to all users in a college
   */
  async broadcastToCollege(collegeId, type, title, message, metadata = {}) {
    try {
      // Get all active users in the college
      const users = await query(
        `SELECT id FROM accounts_user
         WHERE college_id = $1 AND is_active = true`,
        [collegeId]
      );

      const notifications = [];

      for (const user of users.rows) {
        const notification = await this.createNotification(
          user.id,
          type,
          title,
          message,
          metadata
        );
        notifications.push(notification);
      }

      logger.info(`Broadcasted notification to ${notifications.length} users in college ${collegeId}`);
      return notifications;
    } catch (error) {
      logger.error('Error broadcasting to college:', error);
      throw error;
    }
  }
}

module.exports = new NotificationService();
