# Frontend Integration Guide - Real-Time Chat API

> **Complete guide for React/JavaScript frontend developers**
> **Everything you need to integrate the chat API into your frontend application**

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [API Base Configuration](#api-base-configuration)
4. [All API Endpoints](#all-api-endpoints)
5. [Server-Sent Events (SSE)](#server-sent-events-sse)
6. [Complete React Implementation](#complete-react-implementation)
7. [Error Handling](#error-handling)
8. [Testing](#testing)
9. [Common Patterns](#common-patterns)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Installation

```bash
npm install axios
# or
yarn add axios
```

### Environment Setup

Create `.env` file in your React project:

```env
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_WS_BASE_URL=http://localhost:8000/api/v1
```

For production:
```env
REACT_APP_API_BASE_URL=https://yourdomain.com/api/v1
REACT_APP_WS_BASE_URL=https://yourdomain.com/api/v1
```

---

## Authentication

### 1. Login to Get Token

**Endpoint:** `POST /auth/login/`

**Request Headers:**
```javascript
{
  "Content-Type": "application/json"
}
```

**Request Payload:**
```javascript
{
  "username": "john_doe",
  "password": "securePassword123"
}
```

**Response (200 OK):**
```javascript
{
  "key": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",  // This is your auth token
  "user": {
    "id": 789,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "user_type": "student",
    "avatar": "https://s3.amazonaws.com/avatars/john.jpg",
    "college": 1,
    "college_name": "Sample University",
    "is_verified": true
  },
  "college_id": 1,
  "accessible_colleges": [1, 2]
}
```

**Complete React Example:**

```javascript
// src/api/auth.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

export const login = async (username, password) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/auth/login/`, {
      username,
      password
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Save token to localStorage
    localStorage.setItem('authToken', response.data.key);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    localStorage.setItem('collegeId', response.data.college_id);

    return response.data;
  } catch (error) {
    console.error('Login failed:', error.response?.data);
    throw error;
  }
};

export const logout = () => {
  localStorage.removeItem('authToken');
  localStorage.removeItem('user');
  localStorage.removeItem('collegeId');
};

export const getAuthToken = () => {
  return localStorage.getItem('authToken');
};

export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

export const isAuthenticated = () => {
  return !!getAuthToken();
};
```

**Login Component Example:**

```javascript
// src/components/Login.jsx
import React, { useState } from 'react';
import { login } from '../api/auth';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await login(username, password);
      console.log('Logged in as:', data.user.username);
      navigate('/chat');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      {error && <div className="error">{error}</div>}
      <form onSubmit={handleLogin}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
};

export default Login;
```

---

## API Base Configuration

### Axios Instance Setup

```javascript
// src/api/client.js
import axios from 'axios';
import { getAuthToken } from './auth';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token to all requests
apiClient.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }

    // Add college ID if available
    const collegeId = localStorage.getItem('collegeId');
    if (collegeId) {
      config.headers['X-College-ID'] = collegeId;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      localStorage.clear();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

---

## All API Endpoints

### 1. Get Conversations List

**Endpoint:** `GET /communication/chats/conversations/`

**Request Headers:**
```javascript
{
  "Authorization": "Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "Content-Type": "application/json"
}
```

**Request Payload:** None (GET request)

**Response (200 OK):**
```javascript
[
  {
    "conversation_id": 1,
    "other_user": {
      "id": 123,
      "username": "jane_smith",
      "full_name": "Jane Smith",
      "avatar": "https://s3.amazonaws.com/avatars/jane.jpg",
      "is_online": true
    },
    "last_message": "Hey, how are you?",
    "last_message_at": "2026-01-09T10:30:00Z",
    "last_message_by_me": false,
    "unread_count": 3,
    "updated_at": "2026-01-09T10:30:00Z"
  },
  {
    "conversation_id": 2,
    "other_user": {
      "id": 456,
      "username": "bob_jones",
      "full_name": "Bob Jones",
      "avatar": null,
      "is_online": false
    },
    "last_message": "See you tomorrow!",
    "last_message_at": "2026-01-08T15:20:00Z",
    "last_message_by_me": true,
    "unread_count": 0,
    "updated_at": "2026-01-08T15:20:00Z"
  }
]
```

**Implementation:**

```javascript
// src/api/chatService.js
import apiClient from './client';

export const chatAPI = {
  // Get all conversations
  getConversations: async () => {
    try {
      const response = await apiClient.get('/communication/chats/conversations/');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
      throw error;
    }
  },
};
```

**Usage in Component:**

```javascript
// src/components/ConversationsList.jsx
import React, { useState, useEffect } from 'react';
import { chatAPI } from '../api/chatService';

const ConversationsList = ({ onSelectConversation }) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await chatAPI.getConversations();
      setConversations(data);
    } catch (err) {
      setError('Failed to load conversations');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading conversations...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="conversations-list">
      {conversations.map(conv => (
        <div
          key={conv.conversation_id}
          className="conversation-item"
          onClick={() => onSelectConversation(conv.other_user)}
        >
          <img
            src={conv.other_user.avatar || '/default-avatar.png'}
            alt={conv.other_user.full_name}
            className="avatar"
          />
          <div className="conversation-info">
            <h4>{conv.other_user.full_name}</h4>
            <p className={conv.unread_count > 0 ? 'unread' : ''}>
              {conv.last_message_by_me ? 'You: ' : ''}
              {conv.last_message}
            </p>
          </div>
          {conv.unread_count > 0 && (
            <span className="unread-badge">{conv.unread_count}</span>
          )}
          {conv.other_user.is_online && (
            <span className="online-indicator"></span>
          )}
        </div>
      ))}
    </div>
  );
};

export default ConversationsList;
```

---

### 2. Get Conversation Messages

**Endpoint:** `GET /communication/chats/conversation/{user_id}/`

**URL Parameters:**
- `user_id` (required): ID of the other user in the conversation

**Query Parameters:**
- `limit` (optional, default: 50): Number of messages to return
- `offset` (optional, default: 0): Pagination offset
- `before_id` (optional): Get messages before this message ID (for infinite scroll)

**Request Headers:**
```javascript
{
  "Authorization": "Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "Content-Type": "application/json"
}
```

**Example Requests:**

```javascript
// Get first 50 messages
GET /communication/chats/conversation/123/

// Get next 50 messages
GET /communication/chats/conversation/123/?limit=50&offset=50

// Infinite scroll - get messages before message ID 999
GET /communication/chats/conversation/123/?limit=50&before_id=999
```

**Response (200 OK):**
```javascript
{
  "conversation_id": 1,
  "other_user": {
    "id": 123,
    "username": "jane_smith",
    "full_name": "Jane Smith",
    "avatar": "https://s3.amazonaws.com/avatars/jane.jpg",
    "is_online": true
  },
  "messages": [
    {
      "id": 456,
      "sender": 789,
      "sender_name": "John Doe",
      "sender_username": "john_doe",
      "sender_avatar": "https://s3.amazonaws.com/avatars/john.jpg",
      "receiver": 123,
      "receiver_name": "Jane Smith",
      "receiver_username": "jane_smith",
      "receiver_avatar": "https://s3.amazonaws.com/avatars/jane.jpg",
      "conversation": 1,
      "message": "Hello! How are you?",
      "attachment": null,
      "attachment_url": null,
      "attachment_type": null,
      "is_read": true,
      "read_at": "2026-01-09T10:31:00Z",
      "delivered_at": "2026-01-09T10:30:30Z",
      "timestamp": "2026-01-09T10:30:00Z",
      "created_at": "2026-01-09T10:30:00Z",
      "updated_at": "2026-01-09T10:31:00Z",
      "is_active": true
    },
    {
      "id": 457,
      "sender": 123,
      "sender_name": "Jane Smith",
      "sender_username": "jane_smith",
      "sender_avatar": "https://s3.amazonaws.com/avatars/jane.jpg",
      "receiver": 789,
      "receiver_name": "John Doe",
      "receiver_username": "john_doe",
      "receiver_avatar": "https://s3.amazonaws.com/avatars/john.jpg",
      "conversation": 1,
      "message": "I'm great, thanks! How about you?",
      "attachment": null,
      "attachment_url": null,
      "attachment_type": null,
      "is_read": false,
      "read_at": null,
      "delivered_at": "2026-01-09T10:32:00Z",
      "timestamp": "2026-01-09T10:32:00Z",
      "created_at": "2026-01-09T10:32:00Z",
      "updated_at": "2026-01-09T10:32:00Z",
      "is_active": true
    }
  ],
  "has_more": true  // true if there are more messages to load
}
```

**Implementation:**

```javascript
// src/api/chatService.js (continued)
export const chatAPI = {
  // ... previous methods

  // Get messages in a conversation
  getMessages: async (userId, options = {}) => {
    const { limit = 50, offset = 0, before_id } = options;

    const params = {
      limit,
      offset,
      ...(before_id && { before_id })
    };

    try {
      const response = await apiClient.get(
        `/communication/chats/conversation/${userId}/`,
        { params }
      );
      return response.data;
    } catch (error) {
      console.error('Failed to fetch messages:', error);
      throw error;
    }
  },
};
```

**Usage with Infinite Scroll:**

```javascript
// src/components/ChatWindow.jsx
import React, { useState, useEffect, useRef } from 'react';
import { chatAPI } from '../api/chatService';

const ChatWindow = ({ otherUser, currentUser }) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const messagesContainerRef = useRef(null);

  useEffect(() => {
    loadInitialMessages();
  }, [otherUser.id]);

  const loadInitialMessages = async () => {
    setLoading(true);
    try {
      const data = await chatAPI.getMessages(otherUser.id, { limit: 50 });
      setMessages(data.messages.reverse()); // Reverse for chronological order
      setHasMore(data.has_more);
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMoreMessages = async () => {
    if (!hasMore || loading) return;

    setLoading(true);
    try {
      const oldestMessageId = messages[0]?.id;
      const data = await chatAPI.getMessages(otherUser.id, {
        limit: 50,
        before_id: oldestMessageId
      });

      setMessages(prev => [...data.messages.reverse(), ...prev]);
      setHasMore(data.has_more);
    } catch (error) {
      console.error('Failed to load more messages:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle scroll for infinite loading
  const handleScroll = () => {
    const container = messagesContainerRef.current;
    if (container.scrollTop === 0 && hasMore) {
      loadMoreMessages();
    }
  };

  return (
    <div className="chat-window">
      <div
        className="messages-container"
        ref={messagesContainerRef}
        onScroll={handleScroll}
      >
        {loading && messages.length === 0 && <div>Loading...</div>}
        {messages.map(msg => (
          <Message key={msg.id} message={msg} currentUser={currentUser} />
        ))}
      </div>
    </div>
  );
};
```

---

### 3. Send Message

**Endpoint:** `POST /communication/chats/`

**Request Headers:**
```javascript
{
  "Authorization": "Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "Content-Type": "application/json"
}
```

**For text message:**

**Request Payload:**
```javascript
{
  "receiver_id": 123,
  "message": "Hello! How are you?"
}
```

**For message with attachment:**

**Request Headers:**
```javascript
{
  "Authorization": "Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "Content-Type": "multipart/form-data"
}
```

**Request Payload (FormData):**
```javascript
// FormData format
receiver_id: 123
message: "Check out this image!"
attachment: [File object]
```

**Response (201 Created):**
```javascript
{
  "id": 458,
  "sender": 789,
  "sender_name": "John Doe",
  "sender_username": "john_doe",
  "sender_avatar": "https://s3.amazonaws.com/avatars/john.jpg",
  "receiver": 123,
  "receiver_name": "Jane Smith",
  "receiver_username": "jane_smith",
  "receiver_avatar": "https://s3.amazonaws.com/avatars/jane.jpg",
  "conversation": 1,
  "message": "Hello! How are you?",
  "attachment": null,
  "attachment_url": null,
  "attachment_type": null,
  "is_read": false,
  "read_at": null,
  "delivered_at": null,
  "timestamp": "2026-01-09T10:35:00Z",
  "created_at": "2026-01-09T10:35:00Z",
  "updated_at": "2026-01-09T10:35:00Z",
  "is_active": true
}
```

**Error Responses:**

**400 Bad Request:**
```javascript
{
  "error": "receiver_id is required"
}
// or
{
  "error": "message or attachment is required"
}
```

**404 Not Found:**
```javascript
{
  "error": "Receiver not found"
}
```

**Implementation:**

```javascript
// src/api/chatService.js (continued)
export const chatAPI = {
  // ... previous methods

  // Send a text message
  sendMessage: async (receiverId, message, attachment = null) => {
    try {
      let response;

      if (attachment) {
        // Send with attachment using FormData
        const formData = new FormData();
        formData.append('receiver_id', receiverId);
        formData.append('message', message);
        formData.append('attachment', attachment);

        response = await apiClient.post('/communication/chats/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      } else {
        // Send text message
        response = await apiClient.post('/communication/chats/', {
          receiver_id: receiverId,
          message: message,
        });
      }

      return response.data;
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    }
  },
};
```

**Usage in Component:**

```javascript
// src/components/MessageInput.jsx
import React, { useState } from 'react';
import { chatAPI } from '../api/chatService';

const MessageInput = ({ receiverId, onMessageSent }) => {
  const [message, setMessage] = useState('');
  const [attachment, setAttachment] = useState(null);
  const [sending, setSending] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!message.trim() && !attachment) return;

    setSending(true);
    try {
      const sentMessage = await chatAPI.sendMessage(
        receiverId,
        message,
        attachment
      );

      setMessage('');
      setAttachment(null);
      onMessageSent(sentMessage);
    } catch (error) {
      alert('Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file size (e.g., max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('File too large. Max 10MB.');
        return;
      }
      setAttachment(file);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="message-input-form">
      {attachment && (
        <div className="attachment-preview">
          {attachment.name}
          <button onClick={() => setAttachment(null)}>×</button>
        </div>
      )}

      <input
        type="file"
        id="file-input"
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />

      <button
        type="button"
        onClick={() => document.getElementById('file-input').click()}
      >
        📎
      </button>

      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type a message..."
        disabled={sending}
      />

      <button type="submit" disabled={sending}>
        {sending ? '...' : 'Send'}
      </button>
    </form>
  );
};

export default MessageInput;
```

---

### 4. Mark Messages as Read

**Endpoint:** `POST /communication/chats/mark-read/`

**Request Headers:**
```javascript
{
  "Authorization": "Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "Content-Type": "application/json"
}
```

**Option 1: Mark specific messages**

**Request Payload:**
```javascript
{
  "message_ids": [456, 457, 458]
}
```

**Option 2: Mark all messages in a conversation**

**Request Payload:**
```javascript
{
  "conversation_id": 1
}
```

**Option 3: Mark all messages from a sender**

**Request Payload:**
```javascript
{
  "sender_id": 123
}
```

**Response (200 OK):**
```javascript
{
  "success": true,
  "marked_count": 3,
  "read_at": "2026-01-09T10:40:00Z"
}
```

**Error Response (400 Bad Request):**
```javascript
{
  "error": "Provide message_ids, conversation_id, or sender_id"
}
```

**Implementation:**

```javascript
// src/api/chatService.js (continued)
export const chatAPI = {
  // ... previous methods

  // Mark messages as read
  markAsRead: async (options) => {
    try {
      const response = await apiClient.post(
        '/communication/chats/mark-read/',
        options
      );
      return response.data;
    } catch (error) {
      console.error('Failed to mark messages as read:', error);
      throw error;
    }
  },

  // Convenience methods
  markConversationAsRead: async (conversationId) => {
    return chatAPI.markAsRead({ conversation_id: conversationId });
  },

  markMessagesAsRead: async (messageIds) => {
    return chatAPI.markAsRead({ message_ids: messageIds });
  },
};
```

**Usage:**

```javascript
// When opening a conversation, mark all as read
useEffect(() => {
  if (conversationId) {
    chatAPI.markConversationAsRead(conversationId);
  }
}, [conversationId]);

// Or mark specific messages
const handleMarkRead = async (messageIds) => {
  try {
    await chatAPI.markMessagesAsRead(messageIds);
    console.log('Messages marked as read');
  } catch (error) {
    console.error('Failed to mark as read:', error);
  }
};
```

---

### 5. Send Typing Indicator

**Endpoint:** `POST /communication/chats/typing/`

**Request Headers:**
```javascript
{
  "Authorization": "Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "Content-Type": "application/json"
}
```

**Request Payload:**
```javascript
{
  "receiver_id": 123,
  "is_typing": true  // or false when stopped typing
}
```

**Response (200 OK):**
```javascript
{
  "success": true
}
```

**Error Response (400 Bad Request):**
```javascript
{
  "error": "receiver_id is required"
}
```

**Implementation:**

```javascript
// src/api/chatService.js (continued)
export const chatAPI = {
  // ... previous methods

  // Send typing indicator
  sendTyping: async (receiverId, isTyping) => {
    try {
      const response = await apiClient.post('/communication/chats/typing/', {
        receiver_id: receiverId,
        is_typing: isTyping,
      });
      return response.data;
    } catch (error) {
      console.error('Failed to send typing indicator:', error);
      throw error;
    }
  },
};
```

**Usage with Debounce:**

```javascript
// src/hooks/useTypingIndicator.js
import { useRef, useCallback } from 'react';
import { chatAPI } from '../api/chatService';

export const useTypingIndicator = (receiverId) => {
  const typingTimeoutRef = useRef(null);
  const isTypingRef = useRef(false);

  const sendTyping = useCallback((isTyping) => {
    if (isTyping && !isTypingRef.current) {
      // Start typing
      chatAPI.sendTyping(receiverId, true);
      isTypingRef.current = true;
    }

    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Stop typing after 3 seconds of inactivity
    typingTimeoutRef.current = setTimeout(() => {
      if (isTypingRef.current) {
        chatAPI.sendTyping(receiverId, false);
        isTypingRef.current = false;
      }
    }, 3000);
  }, [receiverId]);

  const stopTyping = useCallback(() => {
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    if (isTypingRef.current) {
      chatAPI.sendTyping(receiverId, false);
      isTypingRef.current = false;
    }
  }, [receiverId]);

  return { sendTyping, stopTyping };
};
```

**Usage in Component:**

```javascript
// In MessageInput component
import { useTypingIndicator } from '../hooks/useTypingIndicator';

const MessageInput = ({ receiverId }) => {
  const [message, setMessage] = useState('');
  const { sendTyping, stopTyping } = useTypingIndicator(receiverId);

  const handleChange = (e) => {
    setMessage(e.target.value);

    // Send typing indicator
    if (e.target.value.trim()) {
      sendTyping(true);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Send message
    // ...
    stopTyping();
  };

  return (
    <input
      value={message}
      onChange={handleChange}
      onBlur={stopTyping}
    />
  );
};
```

---

### 6. Get Unread Count

**Endpoint:** `GET /communication/chats/unread-count/`

**Request Headers:**
```javascript
{
  "Authorization": "Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "Content-Type": "application/json"
}
```

**Request Payload:** None (GET request)

**Response (200 OK):**
```javascript
{
  "total_unread": 42,
  "conversations": [
    {
      "conversation_id": 1,
      "unread_count": 5,
      "other_user_id": 123,
      "other_user_name": "Jane Smith"
    },
    {
      "conversation_id": 2,
      "unread_count": 37,
      "other_user_id": 456,
      "other_user_name": "Bob Jones"
    }
  ]
}
```

**Implementation:**

```javascript
// src/api/chatService.js (continued)
export const chatAPI = {
  // ... previous methods

  // Get unread message count
  getUnreadCount: async () => {
    try {
      const response = await apiClient.get('/communication/chats/unread-count/');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
      throw error;
    }
  },
};
```

**Usage for Badge:**

```javascript
// src/components/UnreadBadge.jsx
import React, { useState, useEffect } from 'react';
import { chatAPI } from '../api/chatService';

const UnreadBadge = () => {
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    loadUnreadCount();

    // Refresh every 30 seconds
    const interval = setInterval(loadUnreadCount, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadUnreadCount = async () => {
    try {
      const data = await chatAPI.getUnreadCount();
      setUnreadCount(data.total_unread);
    } catch (error) {
      console.error('Failed to load unread count:', error);
    }
  };

  if (unreadCount === 0) return null;

  return (
    <span className="unread-badge">
      {unreadCount > 99 ? '99+' : unreadCount}
    </span>
  );
};

export default UnreadBadge;
```

---

### 7. Get Online Users

**Endpoint:** `GET /communication/chats/online-users/`

**Request Headers:**
```javascript
{
  "Authorization": "Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "Content-Type": "application/json"
}
```

**Request Payload:** None (GET request)

**Response (200 OK):**
```javascript
{
  "online_users": [123, 456, 789]
}
```

**Implementation:**

```javascript
// src/api/chatService.js (continued)
export const chatAPI = {
  // ... previous methods

  // Get online users
  getOnlineUsers: async () => {
    try {
      const response = await apiClient.get('/communication/chats/online-users/');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch online users:', error);
      throw error;
    }
  },
};
```

**Usage:**

```javascript
// src/hooks/useOnlineStatus.js
import { useState, useEffect } from 'react';
import { chatAPI } from '../api/chatService';

export const useOnlineStatus = (userId) => {
  const [isOnline, setIsOnline] = useState(false);

  useEffect(() => {
    const checkOnlineStatus = async () => {
      try {
        const data = await chatAPI.getOnlineUsers();
        setIsOnline(data.online_users.includes(userId));
      } catch (error) {
        console.error('Failed to check online status:', error);
      }
    };

    checkOnlineStatus();
    const interval = setInterval(checkOnlineStatus, 10000); // Check every 10s

    return () => clearInterval(interval);
  }, [userId]);

  return isOnline;
};
```

---

## Server-Sent Events (SSE)

### SSE Connection

**Endpoint:** `GET /communication/sse/events/`

**Authentication:** Token passed as query parameter

**URL Format:**
```
GET /communication/sse/events/?token=YOUR_AUTH_TOKEN
```

**Example:**
```
http://localhost:8000/api/v1/communication/sse/events/?token=9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### Event Types

#### 1. Connected Event

Sent immediately upon successful connection.

```javascript
{
  event: "connected",
  data: {
    status: "connected",
    user_id: 789
  }
}
```

#### 2. Message Event

New message received.

```javascript
{
  event: "message",
  data: {
    id: 456,
    sender_id: 123,
    sender_name: "Jane Smith",
    receiver_id: 789,
    message: "Hello! How are you?",
    attachment: null,
    attachment_type: null,
    timestamp: "2026-01-09T10:30:00Z",
    is_read: false,
    conversation_id: 1
  }
}
```

#### 3. Typing Event

Someone is typing.

```javascript
{
  event: "typing",
  data: {
    sender_id: 123,
    sender_name: "Jane Smith",
    is_typing: true
  }
}
```

#### 4. Read Receipt Event

Your message was read.

```javascript
{
  event: "read_receipt",
  data: {
    message_id: 456,
    reader_id: 123,
    reader_name: "Jane Smith",
    read_at: "2026-01-09T10:35:00Z"
  }
}
```

#### 5. Notification Event

System notification.

```javascript
{
  event: "notification",
  data: {
    title: "New Notice",
    message: "Class cancelled tomorrow",
    notification_type: "notice",
    // ... additional data
  }
}
```

#### 6. Heartbeat Event

Keep-alive ping (every 30 seconds).

```javascript
{
  event: "heartbeat",
  data: {
    timestamp: 1736419800.123
  }
}
```

### SSE Implementation

**Custom Hook:**

```javascript
// src/hooks/useSSE.js
import { useEffect, useCallback, useRef, useState } from 'react';
import { getAuthToken } from '../api/auth';

const SSE_BASE_URL = process.env.REACT_APP_WS_BASE_URL;

export const useSSE = (onMessage, enabled = true) => {
  const eventSourceRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const reconnectTimeoutRef = useRef(null);

  const connect = useCallback(() => {
    if (!enabled) {
      console.log('SSE disabled');
      return;
    }

    const token = getAuthToken();
    if (!token) {
      setError('No auth token');
      console.error('Cannot connect to SSE: No auth token');
      return;
    }

    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const url = `${SSE_BASE_URL}/communication/sse/events/?token=${token}`;
    console.log('Connecting to SSE:', url);

    const eventSource = new EventSource(url);

    eventSource.onopen = () => {
      console.log('✅ SSE Connected');
      setIsConnected(true);
      setError(null);
    };

    eventSource.onerror = (err) => {
      console.error('❌ SSE Error:', err);
      setIsConnected(false);
      setError('Connection error');

      // Close the connection
      eventSource.close();

      // Auto-reconnect after 5 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        console.log('🔄 Reconnecting to SSE...');
        connect();
      }, 5000);
    };

    // Handle all event types
    const eventTypes = [
      'connected',
      'message',
      'typing',
      'read_receipt',
      'notification',
      'heartbeat',
      'disconnected'
    ];

    eventTypes.forEach(eventType => {
      eventSource.addEventListener(eventType, (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log(`📨 SSE Event [${eventType}]:`, data);
          onMessage({ event: eventType, data });
        } catch (err) {
          console.error('Failed to parse SSE data:', err, event.data);
        }
      });
    });

    eventSourceRef.current = eventSource;
  }, [enabled, onMessage]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [connect]);

  return {
    isConnected,
    error,
    reconnect: connect
  };
};
```

**Usage in Component:**

```javascript
// src/components/Chat/ChatContainer.jsx
import React, { useState, useCallback } from 'react';
import { useSSE } from '../../hooks/useSSE';
import { getCurrentUser } from '../../api/auth';

const ChatContainer = () => {
  const [messages, setMessages] = useState([]);
  const [typingUsers, setTypingUsers] = useState({});
  const currentUser = getCurrentUser();

  // Handle SSE events
  const handleSSEMessage = useCallback((event) => {
    const { event: eventType, data } = event;

    switch (eventType) {
      case 'connected':
        console.log('Connected to chat server');
        break;

      case 'message':
        // Add new message
        setMessages(prev => [...prev, data]);

        // Mark as read if we're the receiver
        if (data.receiver_id === currentUser.id) {
          chatAPI.markMessagesAsRead([data.id]);
        }
        break;

      case 'typing':
        // Update typing indicators
        setTypingUsers(prev => ({
          ...prev,
          [data.sender_id]: data.is_typing
        }));

        // Auto-clear after 5 seconds
        if (data.is_typing) {
          setTimeout(() => {
            setTypingUsers(prev => ({
              ...prev,
              [data.sender_id]: false
            }));
          }, 5000);
        }
        break;

      case 'read_receipt':
        // Update message read status
        setMessages(prev =>
          prev.map(msg =>
            msg.id === data.message_id
              ? { ...msg, is_read: true, read_at: data.read_at }
              : msg
          )
        );
        break;

      case 'notification':
        // Show notification
        showNotification(data.title, data.message);
        break;

      case 'heartbeat':
        // Connection is alive
        console.log('Heartbeat received');
        break;

      default:
        console.log('Unknown event:', eventType, data);
    }
  }, [currentUser.id]);

  // Connect to SSE
  const { isConnected, error, reconnect } = useSSE(handleSSEMessage);

  return (
    <div className="chat-container">
      <div className="connection-status">
        {isConnected ? (
          <span className="online">🟢 Connected</span>
        ) : error ? (
          <span className="error">
            🔴 Disconnected - <button onClick={reconnect}>Reconnect</button>
          </span>
        ) : (
          <span className="connecting">🟡 Connecting...</span>
        )}
      </div>

      {/* Rest of your chat UI */}
    </div>
  );
};

export default ChatContainer;
```

---

## Complete React Implementation

### File Structure

```
src/
├── api/
│   ├── auth.js              # Authentication functions
│   ├── client.js            # Axios instance
│   └── chatService.js       # Chat API functions
├── hooks/
│   ├── useSSE.js            # SSE connection hook
│   ├── useTypingIndicator.js
│   └── useOnlineStatus.js
├── components/
│   ├── Chat/
│   │   ├── ChatContainer.jsx
│   │   ├── ConversationsList.jsx
│   │   ├── ChatWindow.jsx
│   │   ├── MessageList.jsx
│   │   ├── Message.jsx
│   │   └── MessageInput.jsx
│   ├── Login.jsx
│   └── UnreadBadge.jsx
└── App.jsx
```

### Complete chatService.js

```javascript
// src/api/chatService.js - COMPLETE VERSION
import apiClient from './client';

export const chatAPI = {
  // Get all conversations
  getConversations: async () => {
    const response = await apiClient.get('/communication/chats/conversations/');
    return response.data;
  },

  // Get messages in a conversation
  getMessages: async (userId, options = {}) => {
    const { limit = 50, offset = 0, before_id } = options;
    const params = { limit, offset, ...(before_id && { before_id }) };
    const response = await apiClient.get(
      `/communication/chats/conversation/${userId}/`,
      { params }
    );
    return response.data;
  },

  // Send a message
  sendMessage: async (receiverId, message, attachment = null) => {
    let response;
    if (attachment) {
      const formData = new FormData();
      formData.append('receiver_id', receiverId);
      formData.append('message', message);
      formData.append('attachment', attachment);
      response = await apiClient.post('/communication/chats/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    } else {
      response = await apiClient.post('/communication/chats/', {
        receiver_id: receiverId,
        message: message,
      });
    }
    return response.data;
  },

  // Mark messages as read
  markAsRead: async (options) => {
    const response = await apiClient.post(
      '/communication/chats/mark-read/',
      options
    );
    return response.data;
  },

  // Convenience: Mark conversation as read
  markConversationAsRead: async (conversationId) => {
    return chatAPI.markAsRead({ conversation_id: conversationId });
  },

  // Convenience: Mark specific messages as read
  markMessagesAsRead: async (messageIds) => {
    return chatAPI.markAsRead({ message_ids: messageIds });
  },

  // Send typing indicator
  sendTyping: async (receiverId, isTyping) => {
    const response = await apiClient.post('/communication/chats/typing/', {
      receiver_id: receiverId,
      is_typing: isTyping,
    });
    return response.data;
  },

  // Get unread count
  getUnreadCount: async () => {
    const response = await apiClient.get('/communication/chats/unread-count/');
    return response.data;
  },

  // Get online users
  getOnlineUsers: async () => {
    const response = await apiClient.get('/communication/chats/online-users/');
    return response.data;
  },
};
```

### Complete ChatWindow Component

```javascript
// src/components/Chat/ChatWindow.jsx - COMPLETE VERSION
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { chatAPI } from '../../api/chatService';
import { useSSE } from '../../hooks/useSSE';
import { useTypingIndicator } from '../../hooks/useTypingIndicator';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

const ChatWindow = ({ otherUser, currentUser }) => {
  const [messages, setMessages] = useState([]);
  const [isOtherUserTyping, setIsOtherUserTyping] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const messagesEndRef = useRef(null);

  // Load initial messages
  useEffect(() => {
    loadMessages();
  }, [otherUser.id]);

  const loadMessages = async () => {
    setIsLoading(true);
    try {
      const data = await chatAPI.getMessages(otherUser.id, { limit: 50 });
      setMessages(data.messages.reverse());
      setHasMore(data.has_more);

      // Mark conversation as read
      if (data.conversation_id) {
        await chatAPI.markConversationAsRead(data.conversation_id);
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle SSE events
  const handleSSEMessage = useCallback((event) => {
    const { event: eventType, data } = event;

    switch (eventType) {
      case 'message':
        // Only add if relevant to this conversation
        if (
          (data.sender_id === otherUser.id && data.receiver_id === currentUser.id) ||
          (data.sender_id === currentUser.id && data.receiver_id === otherUser.id)
        ) {
          setMessages(prev => [...prev, data]);

          // Auto mark as read if we're the receiver
          if (data.receiver_id === currentUser.id) {
            chatAPI.markMessagesAsRead([data.id]);
          }
        }
        break;

      case 'typing':
        if (data.sender_id === otherUser.id) {
          setIsOtherUserTyping(data.is_typing);
          if (data.is_typing) {
            setTimeout(() => setIsOtherUserTyping(false), 5000);
          }
        }
        break;

      case 'read_receipt':
        setMessages(prev =>
          prev.map(msg =>
            msg.id === data.message_id
              ? { ...msg, is_read: true, read_at: data.read_at }
              : msg
          )
        );
        break;

      default:
        break;
    }
  }, [otherUser.id, currentUser.id]);

  // Connect to SSE
  const { isConnected } = useSSE(handleSSEMessage);

  // Scroll to bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleMessageSent = (sentMessage) => {
    // Message will be added via SSE, but add optimistically
    setMessages(prev => [...prev, sentMessage]);
  };

  return (
    <div className="chat-window">
      <div className="chat-header">
        <div className="user-info">
          <img
            src={otherUser.avatar || '/default-avatar.png'}
            alt={otherUser.full_name}
            className="avatar"
          />
          <div>
            <h3>{otherUser.full_name}</h3>
            <span className={`status ${otherUser.is_online ? 'online' : 'offline'}`}>
              {otherUser.is_online ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>
        <div className="connection-indicator">
          {isConnected ? '🟢' : '🔴'}
        </div>
      </div>

      <MessageList
        messages={messages}
        currentUser={currentUser}
        isLoading={isLoading}
        isOtherUserTyping={isOtherUserTyping}
        otherUserName={otherUser.full_name}
        messagesEndRef={messagesEndRef}
      />

      <MessageInput
        receiverId={otherUser.id}
        onMessageSent={handleMessageSent}
      />
    </div>
  );
};

export default ChatWindow;
```

---

## Error Handling

### Common Error Responses

#### 401 Unauthorized
```javascript
{
  "detail": "Authentication credentials were not provided."
}
// or
{
  "detail": "Invalid token."
}
```

**Handling:**
```javascript
// In axios interceptor
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.clear();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

#### 400 Bad Request
```javascript
{
  "error": "receiver_id is required"
}
```

**Handling:**
```javascript
try {
  await chatAPI.sendMessage(receiverId, message);
} catch (error) {
  if (error.response?.status === 400) {
    alert(error.response.data.error);
  }
}
```

#### 404 Not Found
```javascript
{
  "error": "Receiver not found"
}
```

#### 500 Internal Server Error
```javascript
{
  "detail": "Internal server error"
}
```

### Error Boundary Component

```javascript
// src/components/ErrorBoundary.jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

---

## Testing

### Test SSE Connection

```javascript
// src/utils/testSSE.js
export const testSSEConnection = (token) => {
  const url = `http://localhost:8000/api/v1/communication/sse/test/`;
  const eventSource = new EventSource(url);

  eventSource.addEventListener('test', (event) => {
    console.log('Test event:', JSON.parse(event.data));
  });

  eventSource.addEventListener('complete', (event) => {
    console.log('Test complete:', JSON.parse(event.data));
    eventSource.close();
  });

  eventSource.onerror = (error) => {
    console.error('SSE test error:', error);
    eventSource.close();
  };

  // Auto-close after 10 seconds
  setTimeout(() => {
    console.log('Closing test connection');
    eventSource.close();
  }, 10000);
};

// Usage:
// import { testSSEConnection } from './utils/testSSE';
// testSSEConnection();
```

### Test API Endpoints

```javascript
// src/utils/testAPI.js
import { chatAPI } from '../api/chatService';

export const testChatAPI = async () => {
  console.log('Testing Chat API...');

  try {
    // Test 1: Get conversations
    console.log('1. Getting conversations...');
    const conversations = await chatAPI.getConversations();
    console.log('✅ Conversations:', conversations);

    // Test 2: Get messages (if conversations exist)
    if (conversations.length > 0) {
      const firstConv = conversations[0];
      console.log('2. Getting messages...');
      const messages = await chatAPI.getMessages(firstConv.other_user.id);
      console.log('✅ Messages:', messages);
    }

    // Test 3: Get unread count
    console.log('3. Getting unread count...');
    const unreadCount = await chatAPI.getUnreadCount();
    console.log('✅ Unread count:', unreadCount);

    // Test 4: Get online users
    console.log('4. Getting online users...');
    const onlineUsers = await chatAPI.getOnlineUsers();
    console.log('✅ Online users:', onlineUsers);

    console.log('✅ All tests passed!');
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
};

// Usage in browser console:
// import { testChatAPI } from './utils/testAPI';
// testChatAPI();
```

---

## Common Patterns

### Pattern 1: Message Optimistic Updates

```javascript
const sendMessage = async (message) => {
  // Create optimistic message
  const optimisticMessage = {
    id: Date.now(), // Temporary ID
    sender: currentUser.id,
    receiver: otherUser.id,
    message: message,
    timestamp: new Date().toISOString(),
    is_read: false,
    sending: true, // Custom flag
  };

  // Add to UI immediately
  setMessages(prev => [...prev, optimisticMessage]);

  try {
    // Send to server
    const sentMessage = await chatAPI.sendMessage(otherUser.id, message);

    // Replace optimistic with real message
    setMessages(prev =>
      prev.map(msg =>
        msg.id === optimisticMessage.id ? { ...sentMessage, sending: false } : msg
      )
    );
  } catch (error) {
    // Mark as failed
    setMessages(prev =>
      prev.map(msg =>
        msg.id === optimisticMessage.id ? { ...msg, failed: true } : msg
      )
    );
  }
};
```

### Pattern 2: Auto-scroll to Bottom

```javascript
const MessagesContainer = ({ messages }) => {
  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);
  const [autoScroll, setAutoScroll] = useState(true);

  // Detect if user scrolled up
  const handleScroll = () => {
    const container = containerRef.current;
    const isAtBottom =
      container.scrollHeight - container.scrollTop === container.clientHeight;
    setAutoScroll(isAtBottom);
  };

  // Auto-scroll on new message if at bottom
  useEffect(() => {
    if (autoScroll) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, autoScroll]);

  return (
    <div ref={containerRef} onScroll={handleScroll}>
      {messages.map(msg => <Message key={msg.id} message={msg} />)}
      <div ref={messagesEndRef} />
    </div>
  );
};
```

### Pattern 3: Debounced Search

```javascript
// Search conversations
const [searchTerm, setSearchTerm] = useState('');
const [filteredConversations, setFilteredConversations] = useState([]);

useEffect(() => {
  const timer = setTimeout(() => {
    const filtered = conversations.filter(conv =>
      conv.other_user.full_name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredConversations(filtered);
  }, 300);

  return () => clearTimeout(timer);
}, [searchTerm, conversations]);
```

---

## Troubleshooting

### Issue 1: SSE Not Connecting

**Symptoms:**
- `isConnected` stays false
- Console shows connection errors

**Checklist:**
1. ✅ Check auth token exists: `localStorage.getItem('authToken')`
2. ✅ Check URL is correct: `http://localhost:8000/api/v1/communication/sse/events/`
3. ✅ Check CORS settings on backend
4. ✅ Check browser console for errors
5. ✅ Test with SSE test endpoint: `/communication/sse/test/`

**Debug:**
```javascript
console.log('Token:', localStorage.getItem('authToken'));
console.log('SSE URL:', `${SSE_BASE_URL}/communication/sse/events/`);
```

### Issue 2: Messages Not Appearing

**Checklist:**
1. ✅ SSE connected: `isConnected === true`
2. ✅ Event handler registered correctly
3. ✅ User IDs match in event handler
4. ✅ Check browser console for SSE events
5. ✅ Check Network tab → EventStream

**Debug:**
```javascript
const handleSSEMessage = (event) => {
  console.log('SSE Event:', event); // Add this
  // ... rest of handler
};
```

### Issue 3: CORS Errors

**Error:**
```
Access to XMLHttpRequest at 'http://localhost:8000/api/...' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

**Solution:**
Backend needs to allow your frontend origin in `CORS_ALLOWED_ORIGINS`:

```python
# In Django settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### Issue 4: Token Expired

**Symptoms:**
- 401 errors
- Automatic logout

**Solution:**
Implement token refresh or re-login:

```javascript
// Check token periodically
useEffect(() => {
  const checkAuth = async () => {
    try {
      await apiClient.get('/auth/user/');
    } catch (error) {
      if (error.response?.status === 401) {
        logout();
        navigate('/login');
      }
    }
  };

  checkAuth();
  const interval = setInterval(checkAuth, 5 * 60 * 1000); // Every 5 minutes
  return () => clearInterval(interval);
}, []);
```

---

## Complete Example App

### App.jsx

```javascript
// src/App.jsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { isAuthenticated } from './api/auth';
import Login from './components/Login';
import ChatContainer from './components/Chat/ChatContainer';
import ErrorBoundary from './components/ErrorBoundary';

const ProtectedRoute = ({ children }) => {
  return isAuthenticated() ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/chat"
            element={
              <ProtectedRoute>
                <ChatContainer />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/chat" />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
```

---

## Summary Checklist

### Setup ✅
- [ ] Install axios
- [ ] Create `.env` with API URLs
- [ ] Set up authentication (login, token storage)
- [ ] Create axios instance with interceptors
- [ ] Create chatService.js with all API methods

### SSE Integration ✅
- [ ] Create useSSE hook
- [ ] Handle all event types
- [ ] Implement auto-reconnection
- [ ] Add connection status indicator

### Components ✅
- [ ] ConversationsList - show all chats
- [ ] ChatWindow - main chat interface
- [ ] MessageList - display messages
- [ ] MessageInput - send messages
- [ ] UnreadBadge - notification badge

### Features ✅
- [ ] Real-time messaging
- [ ] Typing indicators
- [ ] Read receipts
- [ ] Unread counts
- [ ] Online status
- [ ] File attachments
- [ ] Infinite scroll
- [ ] Error handling

---

**You're all set!** 🚀

This guide contains everything you need to integrate the chat API into your React frontend. All request/response formats are documented, headers are specified, and complete working examples are provided.

**Next Steps:**
1. Copy the code examples
2. Test with your backend
3. Customize UI/styling
4. Add additional features as needed

For backend setup, see **SERVER_SETUP_GUIDE.md**
