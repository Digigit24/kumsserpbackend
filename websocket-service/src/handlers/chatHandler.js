/**
 * Chat Event Handlers
 * Handles Socket.io events for chat functionality
 */

const chatService = require('../services/chatService');
const onlineStatusService = require('../services/onlineStatusService');
const logger = require('../utils/logger');

class ChatHandler {
  /**
   * Initialize chat event handlers
   */
  init(io, socket) {
    const user = socket.user;

    // Send message
    socket.on('chat:send', async (data, callback) => {
      try {
        const { receiverId, message, attachmentUrl } = data;

        if (!receiverId || (!message && !attachmentUrl)) {
          return callback({
            success: false,
            error: 'receiverId and message/attachment are required',
          });
        }

        // Save message to database
        const savedMessage = await chatService.saveMessage(
          user.id,
          receiverId,
          message || '',
          attachmentUrl
        );

        // Increment unread count
        await chatService.incrementUnreadCount(
          savedMessage.conversation_id,
          receiverId
        );

        // Format message for client
        const messageData = {
          id: savedMessage.id,
          senderId: user.id,
          senderName: user.fullName,
          receiverId: receiverId,
          message: savedMessage.message,
          attachment: savedMessage.attachment,
          attachmentType: savedMessage.attachment_type,
          timestamp: savedMessage.timestamp,
          isRead: false,
          conversationId: savedMessage.conversation_id,
        };

        // Send to receiver's sockets
        const receiverSockets = await onlineStatusService.getUserSockets(receiverId);
        receiverSockets.forEach((socketId) => {
          io.to(socketId).emit('chat:message', messageData);
        });

        // Send confirmation to sender
        callback({ success: true, message: messageData });

        logger.info(`Message sent from ${user.id} to ${receiverId}`);
      } catch (error) {
        logger.error('Error sending message:', error);
        callback({ success: false, error: 'Failed to send message' });
      }
    });

    // Typing indicator
    socket.on('chat:typing', async (data) => {
      try {
        const { receiverId, isTyping } = data;

        if (!receiverId) return;

        const typingData = {
          senderId: user.id,
          senderName: user.fullName,
          isTyping: isTyping,
        };

        // Send to receiver's sockets
        const receiverSockets = await onlineStatusService.getUserSockets(receiverId);
        receiverSockets.forEach((socketId) => {
          io.to(socketId).emit('chat:typing', typingData);
        });

        logger.debug(`Typing indicator from ${user.id} to ${receiverId}: ${isTyping}`);
      } catch (error) {
        logger.error('Error handling typing indicator:', error);
      }
    });

    // Mark messages as read
    socket.on('chat:markRead', async (data, callback) => {
      try {
        const { messageIds, conversationId } = data;

        if (!messageIds || !Array.isArray(messageIds) || messageIds.length === 0) {
          return callback({ success: false, error: 'messageIds array is required' });
        }

        // Mark messages as read
        const readMessages = await chatService.markMessagesAsRead(messageIds);

        // Reset unread count if conversation ID provided
        if (conversationId) {
          await chatService.resetUnreadCount(conversationId, user.id);
        }

        // Send read receipts to senders
        const senderIds = [...new Set(readMessages.map((m) => m.sender_id))];

        for (const senderId of senderIds) {
          const senderSockets = await onlineStatusService.getUserSockets(senderId);
          senderSockets.forEach((socketId) => {
            io.to(socketId).emit('chat:readReceipt', {
              messageIds: readMessages
                .filter((m) => m.sender_id === senderId)
                .map((m) => m.id),
              readerId: user.id,
              readerName: user.fullName,
              readAt: new Date(),
            });
          });
        }

        callback({ success: true, count: readMessages.length });

        logger.info(`User ${user.id} marked ${readMessages.length} messages as read`);
      } catch (error) {
        logger.error('Error marking messages as read:', error);
        callback({ success: false, error: 'Failed to mark messages as read' });
      }
    });

    // Get conversation messages
    socket.on('chat:getMessages', async (data, callback) => {
      try {
        const { conversationId, limit = 50, offset = 0 } = data;

        if (!conversationId) {
          return callback({ success: false, error: 'conversationId is required' });
        }

        const messages = await chatService.getConversationMessages(
          conversationId,
          limit,
          offset
        );

        callback({ success: true, messages });
      } catch (error) {
        logger.error('Error fetching conversation messages:', error);
        callback({ success: false, error: 'Failed to fetch messages' });
      }
    });

    // Get online status
    socket.on('chat:getOnlineStatus', async (data, callback) => {
      try {
        const { userIds } = data;

        if (!userIds || !Array.isArray(userIds)) {
          return callback({ success: false, error: 'userIds array is required' });
        }

        const onlineStatus = await onlineStatusService.getOnlineStatusBulk(userIds);

        callback({ success: true, onlineStatus });
      } catch (error) {
        logger.error('Error getting online status:', error);
        callback({ success: false, error: 'Failed to get online status' });
      }
    });
  }
}

module.exports = new ChatHandler();
