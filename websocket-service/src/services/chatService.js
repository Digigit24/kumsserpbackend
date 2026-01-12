/**
 * Chat Service
 * Handles chat message operations
 */

const { query } = require('../config/database');
const logger = require('../utils/logger');

class ChatService {
  /**
   * Save a new chat message to database
   */
  async saveMessage(senderId, receiverId, message, attachmentUrl = null) {
    try {
      // Get or create conversation
      const conversation = await this.getOrCreateConversation(senderId, receiverId);

      // Insert message
      const result = await query(
        `INSERT INTO chat_message
         (sender_id, receiver_id, conversation_id, message, attachment, is_read, timestamp, created_at, updated_at, is_active)
         VALUES ($1, $2, $3, $4, $5, false, NOW(), NOW(), NOW(), true)
         RETURNING id, sender_id, receiver_id, conversation_id, message, attachment, attachment_type, is_read, timestamp, created_at`,
        [senderId, receiverId, conversation.id, message, attachmentUrl]
      );

      const savedMessage = result.rows[0];

      // Update conversation metadata
      await this.updateConversation(conversation.id, senderId, message);

      logger.info(`Message saved: ${savedMessage.id} from ${senderId} to ${receiverId}`);
      return savedMessage;
    } catch (error) {
      logger.error('Error saving message:', error);
      throw error;
    }
  }

  /**
   * Get or create conversation between two users
   */
  async getOrCreateConversation(user1Id, user2Id) {
    try {
      // Ensure consistent ordering (smaller ID first)
      const [smallerId, largerId] = [user1Id, user2Id].sort((a, b) =>
        String(a).localeCompare(String(b))
      );

      // Try to find existing conversation
      let result = await query(
        `SELECT id, user1_id, user2_id FROM conversation
         WHERE user1_id = $1 AND user2_id = $2 AND is_active = true`,
        [smallerId, largerId]
      );

      if (result.rows.length > 0) {
        return result.rows[0];
      }

      // Create new conversation
      result = await query(
        `INSERT INTO conversation
         (user1_id, user2_id, unread_count_user1, unread_count_user2, created_at, updated_at, is_active)
         VALUES ($1, $2, 0, 0, NOW(), NOW(), true)
         RETURNING id, user1_id, user2_id`,
        [smallerId, largerId]
      );

      logger.info(`New conversation created: ${result.rows[0].id}`);
      return result.rows[0];
    } catch (error) {
      logger.error('Error getting/creating conversation:', error);
      throw error;
    }
  }

  /**
   * Update conversation metadata after new message
   */
  async updateConversation(conversationId, senderId, messageContent) {
    try {
      const lastMessage = messageContent.substring(0, 100);

      await query(
        `UPDATE conversation
         SET last_message = $1,
             last_message_at = NOW(),
             last_message_by_id = $2,
             updated_at = NOW()
         WHERE id = $3`,
        [lastMessage, senderId, conversationId]
      );

      // Increment unread count for receiver
      // This requires knowing which user is the receiver
      // We'll handle this in the socket event handler
    } catch (error) {
      logger.error('Error updating conversation:', error);
      throw error;
    }
  }

  /**
   * Increment unread count for receiver
   */
  async incrementUnreadCount(conversationId, receiverId) {
    try {
      // Determine which unread count to increment
      const conv = await query(
        `SELECT user1_id, user2_id FROM conversation WHERE id = $1`,
        [conversationId]
      );

      if (conv.rows.length === 0) return;

      const isUser1 = String(conv.rows[0].user1_id) === String(receiverId);
      const unreadField = isUser1 ? 'unread_count_user1' : 'unread_count_user2';

      await query(
        `UPDATE conversation
         SET ${unreadField} = ${unreadField} + 1
         WHERE id = $1`,
        [conversationId]
      );
    } catch (error) {
      logger.error('Error incrementing unread count:', error);
    }
  }

  /**
   * Mark messages as read
   */
  async markMessagesAsRead(messageIds) {
    try {
      const result = await query(
        `UPDATE chat_message
         SET is_read = true, read_at = NOW()
         WHERE id = ANY($1::uuid[]) AND is_read = false
         RETURNING id, sender_id`,
        [messageIds]
      );

      logger.info(`Marked ${result.rowCount} messages as read`);
      return result.rows;
    } catch (error) {
      logger.error('Error marking messages as read:', error);
      throw error;
    }
  }

  /**
   * Reset unread count for a user in a conversation
   */
  async resetUnreadCount(conversationId, userId) {
    try {
      const conv = await query(
        `SELECT user1_id, user2_id FROM conversation WHERE id = $1`,
        [conversationId]
      );

      if (conv.rows.length === 0) return;

      const isUser1 = String(conv.rows[0].user1_id) === String(userId);
      const unreadField = isUser1 ? 'unread_count_user1' : 'unread_count_user2';

      await query(
        `UPDATE conversation SET ${unreadField} = 0 WHERE id = $1`,
        [conversationId]
      );
    } catch (error) {
      logger.error('Error resetting unread count:', error);
    }
  }

  /**
   * Get conversation messages
   */
  async getConversationMessages(conversationId, limit = 50, offset = 0) {
    try {
      const result = await query(
        `SELECT m.id, m.sender_id, m.receiver_id, m.message, m.attachment,
                m.attachment_type, m.is_read, m.read_at, m.timestamp,
                s.username as sender_username, s.first_name as sender_first_name,
                s.last_name as sender_last_name
         FROM chat_message m
         JOIN accounts_user s ON m.sender_id = s.id
         WHERE m.conversation_id = $1 AND m.is_active = true
         ORDER BY m.timestamp DESC
         LIMIT $2 OFFSET $3`,
        [conversationId, limit, offset]
      );

      return result.rows;
    } catch (error) {
      logger.error('Error fetching conversation messages:', error);
      throw error;
    }
  }
}

module.exports = new ChatService();
