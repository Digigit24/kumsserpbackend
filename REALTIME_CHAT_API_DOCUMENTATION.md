# Real-Time Chat API Documentation
## Server-Sent Events (SSE) + Redis Pub/Sub

> **Version:** 2.0
> **Last Updated:** January 2026
> **Architecture:** SSE + Redis Pub/Sub (Replaced WebSocket)

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Quick Start](#quick-start)
5. [API Endpoints](#api-endpoints)
6. [Real-Time Events (SSE)](#real-time-events-sse)
7. [React Integration](#react-integration)
8. [Complete React Chat Component](#complete-react-chat-component)
9. [Database Models](#database-models)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)

---

## Overview

This chat system provides **real-time messaging** with the following features:

✅ **Real-time messaging** via Server-Sent Events (SSE)
✅ **Typing indicators** - See when someone is typing
✅ **Read receipts** - Know when messages are read
✅ **Unread message counts** - Badge notifications
✅ **Online/Offline status** - See who's online
✅ **Message delivery status** - Delivered and read timestamps
✅ **Conversation management** - Organized message threads
✅ **File attachments** - Send images, documents, etc.
✅ **Low latency** - Sub-second message delivery
✅ **Scalable** - Redis Pub/Sub for horizontal scaling

### Why SSE Instead of WebSocket?

- ✅ **Simpler deployment** - Works over standard HTTP/HTTPS
- ✅ **Better with proxies** - No special proxy configuration needed
- ✅ **Automatic reconnection** - Built into EventSource API
- ✅ **Lower resource usage** - One-way communication when needed
- ✅ **Standard HTTP** - Works with all load balancers
- ✅ **Easier debugging** - Standard HTTP tools work

---

## Prerequisites

### Backend Requirements

1. **Redis Server** (Required for real-time features)
2. **PostgreSQL** (For data persistence)
3. **Python 3.11+** with Django 5.2+

### Frontend Requirements

1. **Modern Browser** with EventSource API support
2. **React 18+** (or any frontend framework)
3. **Token-based authentication**

---

## Architecture

```
┌─────────────┐
│   React     │
│  Frontend   │
└──────┬──────┘
       │
       │ HTTP REST API (Send messages, mark read, typing)
       │ SSE (Receive real-time events)
       │
       ▼
┌─────────────────────────────────────────┐
│         Django Backend                   │
│                                          │
│  ┌──────────┐         ┌──────────┐     │
│  │   REST   │◄───────►│  Redis   │     │
│  │    API   │         │ Pub/Sub  │     │
│  └──────────┘         └──────────┘     │
│       │                     │           │
│       ▼                     ▼           │
│  ┌──────────┐         ┌──────────┐     │
│  │PostgreSQL│         │   SSE    │     │
│  │ Database │         │  Stream  │     │
│  └──────────┘         └──────────┘     │
└─────────────────────────────────────────┘
```

### Message Flow

1. **Sending Messages:**
   - Frontend → POST /api/v1/communication/chats/
   - Backend saves to PostgreSQL
   - Backend publishes to Redis channel `user:{receiver_id}`
   - SSE stream delivers to receiver in real-time

2. **Receiving Messages:**
   - Frontend connects to SSE endpoint
   - Backend subscribes to Redis channel `user:{current_user_id}`
   - Events stream to frontend in real-time

---

## Quick Start

### 1. Install and Start Redis

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
redis-cli ping  # Should return PONG
```

#### macOS:
```bash
brew install redis
brew services start redis
redis-cli ping  # Should return PONG
```

#### Windows (WSL):
```bash
wsl --install  # If WSL not installed
sudo apt-get install redis-server
sudo service redis-server start
redis-cli ping  # Should return PONG
```

#### Using Docker (All platforms):
```bash
docker run -d -p 6379:6379 --name redis redis:latest
docker ps  # Verify container is running
```

### 2. Configure Django

Add to `.env` file:
```env
REDIS_URL=redis://127.0.0.1:6379
```

### 3. Run Migrations

```bash
python manage.py migrate communication
```

### 4. Check Redis Connection

```bash
python manage.py check_redis
```

### 5. Start Django Server

```bash
python manage.py runserver
```

---

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1/communication/
```

### Authentication
All endpoints require authentication via Token:
```
Authorization: Token YOUR_AUTH_TOKEN
```

---

### 1. Get Conversations List

**Endpoint:** `GET /api/v1/communication/chats/conversations/`

**Description:** Get all conversations for the current user with unread counts and online status.

**Response:**
```json
[
  {
    "conversation_id": 1,
    "other_user": {
      "id": 123,
      "username": "john_doe",
      "full_name": "John Doe",
      "avatar": "https://s3.amazonaws.com/avatars/john.jpg",
      "is_online": true
    },
    "last_message": "Hey, how are you?",
    "last_message_at": "2026-01-09T10:30:00Z",
    "last_message_by_me": false,
    "unread_count": 3,
    "updated_at": "2026-01-09T10:30:00Z"
  },
  // ... more conversations
]
```

---

### 2. Get Conversation Messages

**Endpoint:** `GET /api/v1/communication/chats/conversation/{user_id}/`

**Query Parameters:**
- `limit` (optional): Number of messages (default: 50)
- `offset` (optional): Pagination offset (default: 0)
- `before_id` (optional): Load messages before this message ID (for infinite scroll)

**Example:**
```
GET /api/v1/communication/chats/conversation/123/?limit=50&before_id=999
```

**Response:**
```json
{
  "conversation_id": 1,
  "other_user": {
    "id": 123,
    "username": "john_doe",
    "full_name": "John Doe",
    "avatar": "https://s3.amazonaws.com/avatars/john.jpg",
    "is_online": true
  },
  "messages": [
    {
      "id": 456,
      "sender": 789,
      "sender_name": "Jane Smith",
      "sender_username": "jane_smith",
      "sender_avatar": "https://s3.amazonaws.com/avatars/jane.jpg",
      "receiver": 123,
      "receiver_name": "John Doe",
      "receiver_username": "john_doe",
      "receiver_avatar": "https://s3.amazonaws.com/avatars/john.jpg",
      "conversation": 1,
      "message": "Hello! How are you?",
      "attachment": null,
      "attachment_url": null,
      "attachment_type": null,
      "is_read": true,
      "read_at": "2026-01-09T10:31:00Z",
      "delivered_at": "2026-01-09T10:30:30Z",
      "timestamp": "2026-01-09T10:30:00Z"
    }
  ],
  "has_more": false
}
```

---

### 3. Send Message

**Endpoint:** `POST /api/v1/communication/chats/`

**Request Body:**
```json
{
  "receiver_id": 123,
  "message": "Hello! How are you?",
  "attachment": null  // Optional file upload
}
```

**Response:**
```json
{
  "id": 456,
  "sender": 789,
  "sender_name": "Jane Smith",
  "receiver": 123,
  "receiver_name": "John Doe",
  "message": "Hello! How are you?",
  "attachment": null,
  "attachment_url": null,
  "is_read": false,
  "read_at": null,
  "delivered_at": null,
  "timestamp": "2026-01-09T10:30:00Z"
}
```

**Note:** Message is automatically delivered via SSE to the receiver.

---

### 4. Mark Messages as Read

**Endpoint:** `POST /api/v1/communication/chats/mark-read/`

**Request Body (Option 1 - Mark specific messages):**
```json
{
  "message_ids": [456, 457, 458]
}
```

**Request Body (Option 2 - Mark all in conversation):**
```json
{
  "conversation_id": 1
}
```

**Request Body (Option 3 - Mark all from sender):**
```json
{
  "sender_id": 123
}
```

**Response:**
```json
{
  "success": true,
  "marked_count": 3,
  "read_at": "2026-01-09T10:35:00Z"
}
```

---

### 5. Send Typing Indicator

**Endpoint:** `POST /api/v1/communication/chats/typing/`

**Request Body:**
```json
{
  "receiver_id": 123,
  "is_typing": true  // or false when stopped typing
}
```

**Response:**
```json
{
  "success": true
}
```

**Note:** Receiver gets real-time typing event via SSE.

---

### 6. Get Unread Count

**Endpoint:** `GET /api/v1/communication/chats/unread-count/`

**Response:**
```json
{
  "total_unread": 42,
  "conversations": [
    {
      "conversation_id": 1,
      "unread_count": 5,
      "other_user_id": 123,
      "other_user_name": "John Doe"
    },
    {
      "conversation_id": 2,
      "unread_count": 37,
      "other_user_id": 456,
      "other_user_name": "Jane Smith"
    }
  ]
}
```

---

### 7. Get Online Users

**Endpoint:** `GET /api/v1/communication/chats/online-users/`

**Response:**
```json
{
  "online_users": [123, 456, 789]
}
```

---

## Real-Time Events (SSE)

### SSE Connection

**Endpoint:** `GET /api/v1/communication/sse/events/`

**Authentication:** Pass token as query parameter
```
GET /api/v1/communication/sse/events/?token=YOUR_AUTH_TOKEN
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
    sender_name: "John Doe",
    receiver_id: 789,
    message: "Hello!",
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
    sender_name: "John Doe",
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
    reader_name: "John Doe",
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
    ... additional data
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

---

## React Integration

### Installation

```bash
npm install axios
```

### Setup API Client

```javascript
// src/api/client.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to all requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export default apiClient;
```

### Chat API Service

```javascript
// src/api/chatService.js
import apiClient from './client';

export const chatAPI = {
  // Get conversations list
  getConversations: () =>
    apiClient.get('/communication/chats/conversations/'),

  // Get messages in a conversation
  getMessages: (userId, params = {}) =>
    apiClient.get(`/communication/chats/conversation/${userId}/`, { params }),

  // Send a message
  sendMessage: (receiverId, message, attachment = null) => {
    const formData = new FormData();
    formData.append('receiver_id', receiverId);
    formData.append('message', message);
    if (attachment) {
      formData.append('attachment', attachment);
    }

    return apiClient.post('/communication/chats/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Mark messages as read
  markAsRead: (conversationId) =>
    apiClient.post('/communication/chats/mark-read/', { conversation_id: conversationId }),

  // Send typing indicator
  sendTyping: (receiverId, isTyping) =>
    apiClient.post('/communication/chats/typing/', {
      receiver_id: receiverId,
      is_typing: isTyping,
    }),

  // Get unread count
  getUnreadCount: () =>
    apiClient.get('/communication/chats/unread-count/'),

  // Get online users
  getOnlineUsers: () =>
    apiClient.get('/communication/chats/online-users/'),
};
```

### SSE Hook

```javascript
// src/hooks/useSSE.js
import { useEffect, useCallback, useRef, useState } from 'react';

const SSE_URL = 'http://localhost:8000/api/v1/communication/sse/events/';

export const useSSE = (onMessage, enabled = true) => {
  const eventSourceRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);

  const connect = useCallback(() => {
    if (!enabled) return;

    const token = localStorage.getItem('authToken');
    if (!token) {
      setError('No auth token');
      return;
    }

    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const url = `${SSE_URL}?token=${token}`;
    const eventSource = new EventSource(url);

    eventSource.onopen = () => {
      console.log('SSE Connected');
      setIsConnected(true);
      setError(null);
    };

    eventSource.onerror = (err) => {
      console.error('SSE Error:', err);
      setIsConnected(false);
      setError('Connection error');

      // Auto-reconnect after 5 seconds
      setTimeout(connect, 5000);
    };

    // Handle all event types
    ['connected', 'message', 'typing', 'read_receipt', 'notification', 'heartbeat'].forEach(eventType => {
      eventSource.addEventListener(eventType, (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage({ event: eventType, data });
        } catch (err) {
          console.error('Failed to parse SSE data:', err);
        }
      });
    });

    eventSourceRef.current = eventSource;
  }, [enabled, onMessage]);

  useEffect(() => {
    connect();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [connect]);

  return { isConnected, error, reconnect: connect };
};
```

---

## Complete React Chat Component

```javascript
// src/components/Chat/ChatWindow.jsx
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { chatAPI } from '../../api/chatService';
import { useSSE } from '../../hooks/useSSE';

const ChatWindow = ({ otherUser, currentUser }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isOtherUserTyping, setIsOtherUserTyping] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  // Load messages
  const loadMessages = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await chatAPI.getMessages(otherUser.id);
      setMessages(response.data.messages.reverse()); // Reverse for chronological order
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setIsLoading(false);
    }
  }, [otherUser.id]);

  // Handle SSE events
  const handleSSEMessage = useCallback((event) => {
    const { event: eventType, data } = event;

    switch (eventType) {
      case 'message':
        // Only add message if it's from the current conversation
        if (data.sender_id === otherUser.id || data.receiver_id === otherUser.id) {
          setMessages(prev => [...prev, data]);

          // Mark as read if we're the receiver
          if (data.receiver_id === currentUser.id) {
            chatAPI.markAsRead(data.conversation_id);
          }
        }
        break;

      case 'typing':
        if (data.sender_id === otherUser.id) {
          setIsOtherUserTyping(data.is_typing);

          // Auto-clear typing indicator after 5 seconds
          if (data.is_typing) {
            setTimeout(() => setIsOtherUserTyping(false), 5000);
          }
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

      default:
        break;
    }
  }, [otherUser.id, currentUser.id]);

  // Setup SSE
  const { isConnected } = useSSE(handleSSEMessage);

  // Load messages on mount
  useEffect(() => {
    loadMessages();
  }, [loadMessages]);

  // Scroll to bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle typing indicator
  const handleTyping = useCallback(() => {
    if (!isTyping) {
      setIsTyping(true);
      chatAPI.sendTyping(otherUser.id, true);
    }

    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Stop typing after 3 seconds of inactivity
    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
      chatAPI.sendTyping(otherUser.id, false);
    }, 3000);
  }, [isTyping, otherUser.id]);

  // Send message
  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!newMessage.trim()) return;

    const messageText = newMessage;
    setNewMessage('');

    // Stop typing indicator
    if (isTyping) {
      setIsTyping(false);
      chatAPI.sendTyping(otherUser.id, false);
    }

    try {
      const response = await chatAPI.sendMessage(otherUser.id, messageText);
      // Message will be added via SSE, but add optimistically for better UX
      setMessages(prev => [...prev, response.data]);
    } catch (error) {
      console.error('Failed to send message:', error);
      setNewMessage(messageText); // Restore message on error
    }
  };

  // Render message
  const renderMessage = (msg) => {
    const isMe = msg.sender === currentUser.id;
    const timestamp = new Date(msg.timestamp).toLocaleTimeString();

    return (
      <div key={msg.id} className={`message ${isMe ? 'message-sent' : 'message-received'}`}>
        <div className="message-content">
          <p>{msg.message}</p>
          {msg.attachment_url && (
            <img src={msg.attachment_url} alt="attachment" className="message-attachment" />
          )}
        </div>
        <div className="message-meta">
          <span className="timestamp">{timestamp}</span>
          {isMe && (
            <span className="read-status">
              {msg.is_read ? '✓✓' : '✓'}
            </span>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="chat-window">
      {/* Header */}
      <div className="chat-header">
        <div className="user-info">
          <img src={otherUser.avatar || '/default-avatar.png'} alt={otherUser.full_name} />
          <div>
            <h3>{otherUser.full_name}</h3>
            <span className={`status ${otherUser.is_online ? 'online' : 'offline'}`}>
              {otherUser.is_online ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>
        <div className="connection-status">
          {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
        </div>
      </div>

      {/* Messages */}
      <div className="messages-container">
        {isLoading ? (
          <div className="loading">Loading messages...</div>
        ) : (
          <>
            {messages.map(renderMessage)}
            {isOtherUserTyping && (
              <div className="typing-indicator">
                <span>{otherUser.full_name} is typing</span>
                <span className="dots">...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSendMessage} className="message-input-form">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => {
            setNewMessage(e.target.value);
            handleTyping();
          }}
          placeholder="Type a message..."
          className="message-input"
        />
        <button type="submit" className="send-button">
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatWindow;
```

### Conversations List Component

```javascript
// src/components/Chat/ConversationsList.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { chatAPI } from '../../api/chatService';
import { useSSE } from '../../hooks/useSSE';

const ConversationsList = ({ onSelectConversation }) => {
  const [conversations, setConversations] = useState([]);
  const [totalUnread, setTotalUnread] = useState(0);

  // Load conversations
  const loadConversations = useCallback(async () => {
    try {
      const response = await chatAPI.getConversations();
      setConversations(response.data);

      // Calculate total unread
      const unread = response.data.reduce((sum, conv) => sum + conv.unread_count, 0);
      setTotalUnread(unread);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  }, []);

  // Handle SSE events
  const handleSSEMessage = useCallback((event) => {
    const { event: eventType, data } = event;

    if (eventType === 'message') {
      // Refresh conversations to update last message and unread count
      loadConversations();
    }
  }, [loadConversations]);

  // Setup SSE
  useSSE(handleSSEMessage);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();

    // Refresh every minute
    const interval = setInterval(loadConversations, 60000);
    return () => clearInterval(interval);
  }, [loadConversations]);

  return (
    <div className="conversations-list">
      <div className="conversations-header">
        <h2>Messages</h2>
        {totalUnread > 0 && (
          <span className="unread-badge">{totalUnread}</span>
        )}
      </div>

      <div className="conversations-items">
        {conversations.map(conv => (
          <div
            key={conv.conversation_id}
            className="conversation-item"
            onClick={() => onSelectConversation(conv.other_user)}
          >
            <div className="avatar-container">
              <img src={conv.other_user.avatar || '/default-avatar.png'} alt={conv.other_user.full_name} />
              {conv.other_user.is_online && <span className="online-indicator" />}
            </div>

            <div className="conversation-content">
              <div className="conversation-header">
                <h4>{conv.other_user.full_name}</h4>
                <span className="timestamp">
                  {new Date(conv.last_message_at).toLocaleTimeString()}
                </span>
              </div>

              <div className="last-message">
                <p className={conv.unread_count > 0 ? 'unread' : ''}>
                  {conv.last_message_by_me ? 'You: ' : ''}
                  {conv.last_message}
                </p>
                {conv.unread_count > 0 && (
                  <span className="unread-count">{conv.unread_count}</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ConversationsList;
```

### Basic CSS

```css
/* src/components/Chat/Chat.css */

.chat-window {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
  background: #f5f5f5;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.status.online {
  color: #4caf50;
}

.status.offline {
  color: #9e9e9e;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: #ffffff;
}

.message {
  margin-bottom: 1rem;
  max-width: 70%;
}

.message-sent {
  margin-left: auto;
  text-align: right;
}

.message-received {
  margin-right: auto;
  text-align: left;
}

.message-content {
  display: inline-block;
  padding: 0.75rem 1rem;
  border-radius: 12px;
}

.message-sent .message-content {
  background: #1976d2;
  color: white;
}

.message-received .message-content {
  background: #e0e0e0;
  color: #000;
}

.message-meta {
  font-size: 0.75rem;
  color: #666;
  margin-top: 0.25rem;
}

.typing-indicator {
  color: #666;
  font-style: italic;
  padding: 0.5rem;
}

.message-input-form {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  border-top: 1px solid #e0e0e0;
  background: #f5f5f5;
}

.message-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 24px;
  font-size: 1rem;
}

.send-button {
  padding: 0.75rem 1.5rem;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 24px;
  cursor: pointer;
  font-weight: bold;
}

.send-button:hover {
  background: #1565c0;
}

/* Conversations List */

.conversations-list {
  width: 100%;
  max-width: 400px;
  height: 100vh;
  border-right: 1px solid #e0e0e0;
}

.conversations-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.unread-badge {
  background: #f44336;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
}

.conversation-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}

.conversation-item:hover {
  background: #f5f5f5;
}

.avatar-container {
  position: relative;
}

.avatar-container img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
}

.online-indicator {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  background: #4caf50;
  border: 2px solid white;
  border-radius: 50%;
}

.conversation-content {
  flex: 1;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}

.timestamp {
  font-size: 0.75rem;
  color: #666;
}

.last-message {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.last-message p {
  margin: 0;
  color: #666;
  font-size: 0.875rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.last-message p.unread {
  font-weight: bold;
  color: #000;
}

.unread-count {
  background: #f44336;
  color: white;
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  min-width: 20px;
  text-align: center;
}
```

---

## Database Models

### Conversation
Stores conversation metadata between two users.

```python
class Conversation:
    user1: User  # First participant
    user2: User  # Second participant
    last_message: str  # Preview of last message
    last_message_at: datetime
    last_message_by: User
    unread_count_user1: int
    unread_count_user2: int
```

### ChatMessage
Individual messages in conversations.

```python
class ChatMessage:
    sender: User
    receiver: User
    conversation: Conversation
    message: str
    attachment: File  # Optional
    attachment_type: str  # image/video/document
    is_read: bool
    read_at: datetime
    delivered_at: datetime
    timestamp: datetime
```

### TypingIndicator
Tracks who is currently typing.

```python
class TypingIndicator:
    user: User  # Who is typing
    conversation_partner: User  # To whom
    is_typing: bool
    timestamp: datetime  # Auto-updated
```

---

## Deployment

### Production Settings

1. **Use HTTPS** for SSE connections
2. **Configure Nginx** to support SSE:

```nginx
location /api/v1/communication/sse/ {
    proxy_pass http://django;
    proxy_http_version 1.1;
    proxy_set_header Connection '';
    proxy_buffering off;
    proxy_cache off;
    chunked_transfer_encoding off;
    proxy_read_timeout 24h;
}
```

3. **Redis Configuration:**
   - Use Redis Sentinel or Cluster for HA
   - Set appropriate `maxmemory-policy`
   - Enable persistence if needed

4. **Scale Horizontally:**
   - Run multiple Django instances
   - Redis Pub/Sub works across all instances
   - Use load balancer with sticky sessions for SSE

### Environment Variables

```env
# Production
REDIS_URL=redis://production-redis:6379
DJANGO_SETTINGS_MODULE=kumss_erp.settings.production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

---

## Troubleshooting

### Redis Not Connected

**Problem:** `✗ Redis is NOT connected!`

**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# If not running, start Redis
sudo systemctl start redis-server

# Check connection
python manage.py check_redis
```

### SSE Connection Fails

**Problem:** EventSource connection error

**Possible Causes:**
1. **Invalid token:** Check token in localStorage
2. **CORS issue:** Ensure backend allows your frontend origin
3. **Redis down:** Check Redis connection
4. **Firewall:** Ensure port 8000 is accessible

**Debug:**
```javascript
// Check token
console.log(localStorage.getItem('authToken'));

// Check SSE URL
console.log('Connecting to:', SSE_URL);

// Monitor connection
eventSource.onerror = (err) => {
  console.error('SSE Error:', err);
  console.log('ReadyState:', eventSource.readyState);
};
```

### Messages Not Arriving

**Problem:** Messages sent but not received in real-time

**Checklist:**
1. ✅ SSE connection active (`isConnected === true`)
2. ✅ Redis running (`python manage.py check_redis`)
3. ✅ Correct user ID in event handler
4. ✅ No JavaScript errors in console

### High Latency

**Problem:** Messages take >1 second to arrive

**Solutions:**
1. Check Redis latency: `redis-cli --latency`
2. Use Redis on same server as Django
3. Check network between frontend and backend
4. Monitor Django server CPU/memory

### Database Migrations

**Problem:** New models not in database

**Solution:**
```bash
python manage.py migrate communication
```

---

## Performance Tips

1. **Pagination:** Load messages in batches of 50
2. **Virtual scrolling:** For long message lists
3. **Debounce typing:** Send typing events max once per second
4. **Memoize components:** Use React.memo for message items
5. **Lazy load:** Load conversations/messages on demand
6. **Optimize queries:** Use select_related/prefetch_related

---

## Security Considerations

1. **Authentication:** All endpoints require valid token
2. **Authorization:** Users can only see their own messages
3. **Input validation:** Messages are sanitized
4. **File uploads:** Validate file types and sizes
5. **Rate limiting:** Consider adding rate limits for message sending
6. **XSS protection:** Escape user content in frontend

---

## Support

For issues or questions:
- Check Redis: `python manage.py check_redis`
- Check logs: `tail -f logs/debug.log`
- API docs: http://localhost:8000/api/docs/

---

**Version:** 2.0
**Last Updated:** January 2026
**License:** Proprietary

