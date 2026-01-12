# React Integration Guide

Complete guide for integrating WebSocket chat and notifications in React applications.

## Table of Contents

- [Installation](#installation)
- [Custom Hooks](#custom-hooks)
- [Components](#components)
- [Complete Examples](#complete-examples)
- [State Management](#state-management)

---

## Installation

No additional packages required! Use native WebSocket API.

```bash
# Already included in React
# WebSocket is a browser API
```

---

## Custom Hooks

### useWebSocket Hook

Generic WebSocket hook with reconnection.

```javascript
// hooks/useWebSocket.js
import { useEffect, useRef, useState, useCallback } from 'react';

export const useWebSocket = (url, options = {}) => {
  const {
    onMessage,
    onOpen,
    onClose,
    onError,
    reconnectAttempts = 5,
    reconnectInterval = 2000,
  } = options;

  const wsRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [reconnectCount, setReconnectCount] = useState(0);
  const messageQueueRef = useRef([]);

  const connect = useCallback(() => {
    if (!url) return;

    const ws = new WebSocket(url);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      setReconnectCount(0);
      onOpen?.();

      // Send queued messages
      while (messageQueueRef.current.length > 0) {
        const msg = messageQueueRef.current.shift();
        ws.send(JSON.stringify(msg));
      }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage?.(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onclose = (event) => {
      console.log('WebSocket disconnected', event.code);
      setIsConnected(false);
      onClose?.(event);

      // Reconnect
      if (reconnectCount < reconnectAttempts) {
        const delay = reconnectInterval * Math.pow(2, reconnectCount);
        setTimeout(() => {
          setReconnectCount((c) => c + 1);
          connect();
        }, delay);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      onError?.(error);
    };

    wsRef.current = ws;
  }, [url, onMessage, onOpen, onClose, onError, reconnectCount, reconnectAttempts, reconnectInterval]);

  useEffect(() => {
    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const sendMessage = useCallback((data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      // Queue message
      messageQueueRef.current.push(data);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  return {
    sendMessage,
    disconnect,
    isConnected,
  };
};
```

---

### useChatWebSocket Hook

Specific hook for chat WebSocket.

```javascript
// hooks/useChatWebSocket.js
import { useCallback, useState } from 'react';
import { useWebSocket } from './useWebSocket';

export const useChatWebSocket = (authToken) => {
  const [messages, setMessages] = useState({});
  const [typingUsers, setTypingUsers] = useState({});
  const [onlineUsers, setOnlineUsers] = useState(new Set());

  const wsUrl = authToken
    ? `ws://localhost:8000/ws/chat/?token=${authToken}`
    : null;

  const handleMessage = useCallback((data) => {
    switch (data.type) {
      case 'connection':
        console.log('Chat connected', data);
        break;

      case 'message':
        // Add message to conversation
        setMessages((prev) => {
          const conversationId = data.conversation_id;
          const messages = prev[conversationId] || [];
          return {
            ...prev,
            [conversationId]: [...messages, data],
          };
        });
        break;

      case 'message_sent':
        console.log('Message sent confirmation', data);
        break;

      case 'typing_indicator':
        setTypingUsers((prev) => ({
          ...prev,
          [data.sender_id]: data.is_typing,
        }));

        // Auto-remove after 5 seconds
        if (data.is_typing) {
          setTimeout(() => {
            setTypingUsers((prev) => ({
              ...prev,
              [data.sender_id]: false,
            }));
          }, 5000);
        }
        break;

      case 'read_receipt':
        // Update message read status
        setMessages((prev) => {
          const newMessages = { ...prev };
          Object.keys(newMessages).forEach((convId) => {
            newMessages[convId] = newMessages[convId].map((msg) =>
              msg.id === data.message_id
                ? { ...msg, is_read: true, read_at: data.read_at }
                : msg
            );
          });
          return newMessages;
        });
        break;

      case 'delivery_receipt':
        // Update message delivery status
        setMessages((prev) => {
          const newMessages = { ...prev };
          Object.keys(newMessages).forEach((convId) => {
            newMessages[convId] = newMessages[convId].map((msg) =>
              msg.id === data.message_id
                ? { ...msg, delivered_at: data.delivered_at }
                : msg
            );
          });
          return newMessages;
        });
        break;

      case 'online_status_changed':
        setOnlineUsers((prev) => {
          const newSet = new Set(prev);
          if (data.is_online) {
            newSet.add(data.user_id);
          } else {
            newSet.delete(data.user_id);
          }
          return newSet;
        });
        break;

      case 'error':
        console.error('WebSocket error:', data.error);
        break;

      default:
        console.log('Unknown message type:', data.type);
    }
  }, []);

  const { sendMessage, isConnected } = useWebSocket(wsUrl, {
    onMessage: handleMessage,
  });

  // Helper functions
  const sendChatMessage = useCallback(
    (receiverId, message, tempId) => {
      sendMessage({
        type: 'message',
        receiver_id: receiverId,
        message,
        temp_id: tempId || Date.now().toString(),
      });
    },
    [sendMessage]
  );

  const sendTypingIndicator = useCallback(
    (receiverId, isTyping) => {
      sendMessage({
        type: 'typing',
        receiver_id: receiverId,
        is_typing: isTyping,
      });
    },
    [sendMessage]
  );

  const markAsRead = useCallback(
    (messageIds) => {
      sendMessage({
        type: 'read_receipt',
        message_ids: Array.isArray(messageIds) ? messageIds : [messageIds],
      });
    },
    [sendMessage]
  );

  const markConversationAsRead = useCallback(
    (conversationId) => {
      sendMessage({
        type: 'read_receipt',
        conversation_id: conversationId,
      });
    },
    [sendMessage]
  );

  return {
    isConnected,
    messages,
    typingUsers,
    onlineUsers,
    sendChatMessage,
    sendTypingIndicator,
    markAsRead,
    markConversationAsRead,
  };
};
```

---

### useNotificationWebSocket Hook

Specific hook for notifications.

```javascript
// hooks/useNotificationWebSocket.js
import { useCallback, useState } from 'react';
import { useWebSocket } from './useWebSocket';

export const useNotificationWebSocket = (authToken) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const wsUrl = authToken
    ? `ws://localhost:8000/ws/notifications/?token=${authToken}`
    : null;

  const handleMessage = useCallback((data) => {
    switch (data.type) {
      case 'connection':
        setUnreadCount(data.unread_count);
        break;

      case 'notification':
        // Add new notification
        setNotifications((prev) => [data.notification, ...prev]);
        setUnreadCount((count) => count + 1);

        // Show toast/banner
        showNotificationToast(data.notification);
        break;

      case 'notification_update':
        if (data.event === 'notification_read') {
          // Update notification status
          setNotifications((prev) =>
            prev.map((n) =>
              n.id === data.notification_id
                ? { ...n, is_read: true, read_at: data.read_at }
                : n
            )
          );
          setUnreadCount((count) => Math.max(0, count - 1));
        } else if (data.event === 'all_read') {
          // Mark all as read
          setNotifications((prev) =>
            prev.map((n) => ({ ...n, is_read: true, read_at: data.read_at }))
          );
          setUnreadCount(0);
        }
        break;

      case 'unread_count':
        setUnreadCount(data.count);
        break;

      default:
        console.log('Unknown notification message:', data.type);
    }
  }, []);

  const { sendMessage, isConnected } = useWebSocket(wsUrl, {
    onMessage: handleMessage,
  });

  const markNotificationAsRead = useCallback(
    (notificationId) => {
      sendMessage({
        type: 'mark_read',
        notification_id: notificationId,
      });
    },
    [sendMessage]
  );

  const markAllAsRead = useCallback(() => {
    sendMessage({
      type: 'mark_all_read',
    });
  }, [sendMessage]);

  const getUnreadCount = useCallback(() => {
    sendMessage({
      type: 'get_unread_count',
    });
  }, [sendMessage]);

  return {
    isConnected,
    notifications,
    unreadCount,
    markNotificationAsRead,
    markAllAsRead,
    getUnreadCount,
  };
};

// Helper function to show notification toast
function showNotificationToast(notification) {
  // Use your toast library (react-toastify, react-hot-toast, etc.)
  console.log('New notification:', notification);
}
```

---

### useTypingIndicator Hook

Hook for typing indicator with debounce.

```javascript
// hooks/useTypingIndicator.js
import { useEffect, useRef, useState } from 'react';

export const useTypingIndicator = (sendTypingFn, receiverId) => {
  const [isTyping, setIsTyping] = useState(false);
  const typingTimeoutRef = useRef(null);

  const startTyping = () => {
    if (!isTyping) {
      setIsTyping(true);
      sendTypingFn(receiverId, true);
    }

    // Reset timeout
    clearTimeout(typingTimeoutRef.current);
    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
      sendTypingFn(receiverId, false);
    }, 3000); // Stop after 3 seconds of inactivity
  };

  const stopTyping = () => {
    clearTimeout(typingTimeoutRef.current);
    if (isTyping) {
      setIsTyping(false);
      sendTypingFn(receiverId, false);
    }
  };

  useEffect(() => {
    return () => {
      clearTimeout(typingTimeoutRef.current);
    };
  }, []);

  return { startTyping, stopTyping };
};
```

---

## Components

### ChatComponent

Complete chat component with WebSocket.

```javascript
// components/ChatComponent.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useChatWebSocket } from '../hooks/useChatWebSocket';
import { useTypingIndicator } from '../hooks/useTypingIndicator';

export const ChatComponent = ({ authToken, currentUserId, otherUserId }) => {
  const [messageInput, setMessageInput] = useState('');
  const [conversationMessages, setConversationMessages] = useState([]);
  const messagesEndRef = useRef(null);

  const {
    isConnected,
    messages,
    typingUsers,
    onlineUsers,
    sendChatMessage,
    sendTypingIndicator,
    markConversationAsRead,
  } = useChatWebSocket(authToken);

  const { startTyping, stopTyping } = useTypingIndicator(
    sendTypingIndicator,
    otherUserId
  );

  // Load conversation messages from REST API
  useEffect(() => {
    fetch(`/api/v1/communication/chats/conversation/${otherUserId}/`, {
      headers: {
        Authorization: `Token ${authToken}`,
      },
    })
      .then((res) => res.json())
      .then((data) => {
        setConversationMessages(data.messages.reverse());
        // Mark as read
        markConversationAsRead(data.conversation_id);
      });
  }, [otherUserId, authToken, markConversationAsRead]);

  // Update with new WebSocket messages
  useEffect(() => {
    const conversationId = Object.keys(messages).find((key) =>
      messages[key].some(
        (msg) =>
          (msg.sender_id === currentUserId && msg.receiver_id === otherUserId) ||
          (msg.sender_id === otherUserId && msg.receiver_id === currentUserId)
      )
    );

    if (conversationId && messages[conversationId]) {
      const newMessages = messages[conversationId].filter(
        (msg) =>
          !conversationMessages.some(
            (existingMsg) => existingMsg.id === msg.id
          )
      );

      if (newMessages.length > 0) {
        setConversationMessages((prev) => [...prev, ...newMessages]);
      }
    }
  }, [messages, currentUserId, otherUserId, conversationMessages]);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversationMessages]);

  const handleSendMessage = (e) => {
    e.preventDefault();

    if (!messageInput.trim()) return;

    sendChatMessage(otherUserId, messageInput);
    setMessageInput('');
    stopTyping();
  };

  const handleInputChange = (e) => {
    setMessageInput(e.target.value);
    startTyping();
  };

  const isOnline = onlineUsers.has(otherUserId);
  const isOtherUserTyping = typingUsers[otherUserId];

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <h3>Chat with User {otherUserId}</h3>
        <span className={`status ${isOnline ? 'online' : 'offline'}`}>
          {isOnline ? '🟢 Online' : '⚫ Offline'}
        </span>
        {!isConnected && <span className="disconnected">🔴 Disconnected</span>}
      </div>

      {/* Messages */}
      <div className="messages">
        {conversationMessages.map((msg) => (
          <div
            key={msg.id}
            className={`message ${
              msg.sender_id === currentUserId ? 'sent' : 'received'
            }`}
          >
            <div className="message-content">{msg.message}</div>
            <div className="message-meta">
              <span className="timestamp">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </span>
              {msg.sender_id === currentUserId && (
                <span className="status">
                  {msg.is_read ? '✓✓' : msg.delivered_at ? '✓' : '⏱'}
                </span>
              )}
            </div>
          </div>
        ))}

        {isOtherUserTyping && (
          <div className="typing-indicator">
            <span>User is typing...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form className="message-input" onSubmit={handleSendMessage}>
        <input
          type="text"
          value={messageInput}
          onChange={handleInputChange}
          onBlur={stopTyping}
          placeholder="Type a message... (emojis supported 😊)"
          disabled={!isConnected}
        />
        <button type="submit" disabled={!isConnected || !messageInput.trim()}>
          Send
        </button>
      </form>
    </div>
  );
};
```

---

### NotificationBell

Notification bell with unread count.

```javascript
// components/NotificationBell.jsx
import React, { useState } from 'react';
import { useNotificationWebSocket } from '../hooks/useNotificationWebSocket';

export const NotificationBell = ({ authToken }) => {
  const [isOpen, setIsOpen] = useState(false);

  const {
    isConnected,
    notifications,
    unreadCount,
    markNotificationAsRead,
    markAllAsRead,
  } = useNotificationWebSocket(authToken);

  const handleNotificationClick = (notification) => {
    markNotificationAsRead(notification.id);

    // Navigate to link
    if (notification.link) {
      window.location.href = notification.link;
    }
  };

  return (
    <div className="notification-bell">
      <button
        className="bell-icon"
        onClick={() => setIsOpen(!isOpen)}
      >
        🔔
        {unreadCount > 0 && (
          <span className="badge">{unreadCount}</span>
        )}
        {!isConnected && <span className="disconnected">!</span>}
      </button>

      {isOpen && (
        <div className="notification-dropdown">
          <div className="dropdown-header">
            <h4>Notifications</h4>
            {unreadCount > 0 && (
              <button onClick={markAllAsRead}>Mark all as read</button>
            )}
          </div>

          <div className="notification-list">
            {notifications.length === 0 && (
              <p className="empty">No notifications</p>
            )}

            {notifications.map((notification) => (
              <div
                key={notification.id}
                className={`notification-item ${
                  notification.is_read ? 'read' : 'unread'
                }`}
                onClick={() => handleNotificationClick(notification)}
              >
                <div className="icon">{notification.icon || '📢'}</div>
                <div className="content">
                  <h5>{notification.title}</h5>
                  <p>{notification.message}</p>
                  <span className="time">{notification.time_ago}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
```

---

## Complete App Example

```javascript
// App.jsx
import React, { useState, useEffect } from 'react';
import { ChatComponent } from './components/ChatComponent';
import { NotificationBell } from './components/NotificationBell';

function App() {
  const [authToken, setAuthToken] = useState(null);
  const [currentUserId, setCurrentUserId] = useState(null);

  useEffect(() => {
    // Get auth token from localStorage or login
    const token = localStorage.getItem('authToken');
    const userId = localStorage.getItem('userId');

    if (token && userId) {
      setAuthToken(token);
      setCurrentUserId(parseInt(userId));
    }
  }, []);

  if (!authToken) {
    return <LoginPage onLogin={setAuthToken} />;
  }

  return (
    <div className="app">
      <header>
        <h1>KUMSS ERP Chat</h1>
        <NotificationBell authToken={authToken} />
      </header>

      <main>
        <ChatComponent
          authToken={authToken}
          currentUserId={currentUserId}
          otherUserId={2} // Example: chat with user 2
        />
      </main>
    </div>
  );
}

export default App;
```

---

## State Management (Redux/Context)

### With Redux Toolkit

```javascript
// store/chatSlice.js
import { createSlice } from '@reduxjs/toolkit';

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: {},
    conversations: [],
    typingUsers: {},
    onlineUsers: [],
    isConnected: false,
  },
  reducers: {
    setConnected: (state, action) => {
      state.isConnected = action.payload;
    },
    addMessage: (state, action) => {
      const { conversationId, message } = action.payload;
      if (!state.messages[conversationId]) {
        state.messages[conversationId] = [];
      }
      state.messages[conversationId].push(message);
    },
    updateTypingUser: (state, action) => {
      const { userId, isTyping } = action.payload;
      state.typingUsers[userId] = isTyping;
    },
    setOnlineUsers: (state, action) => {
      state.onlineUsers = action.payload;
    },
  },
});

export const { setConnected, addMessage, updateTypingUser, setOnlineUsers } =
  chatSlice.actions;
export default chatSlice.reducer;
```

---

## CSS Styles

```css
/* styles/chat.css */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 600px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.chat-header {
  padding: 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status.online {
  color: #4caf50;
}

.status.offline {
  color: #999;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.message {
  margin-bottom: 12px;
  max-width: 70%;
}

.message.sent {
  margin-left: auto;
  text-align: right;
}

.message-content {
  background: #007bff;
  color: white;
  padding: 8px 12px;
  border-radius: 16px;
  display: inline-block;
}

.message.received .message-content {
  background: #e9ecef;
  color: #333;
}

.message-meta {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.typing-indicator {
  font-style: italic;
  color: #999;
}

.message-input {
  display: flex;
  padding: 16px;
  border-top: 1px solid #ddd;
}

.message-input input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 20px;
  margin-right: 8px;
}

.message-input button {
  padding: 8px 24px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.notification-bell {
  position: relative;
}

.bell-icon {
  position: relative;
  font-size: 24px;
  background: none;
  border: none;
  cursor: pointer;
}

.badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: red;
  color: white;
  border-radius: 50%;
  padding: 2px 6px;
  font-size: 12px;
}

.notification-dropdown {
  position: absolute;
  top: 40px;
  right: 0;
  width: 320px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}

.notification-item.unread {
  background: #f0f8ff;
}

.notification-item:hover {
  background: #f5f5f5;
}
```

---

**Last Updated:** January 12, 2026
