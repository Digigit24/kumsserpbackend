# Server-Sent Events (SSE) Integration Guide

> **Complete guide for real-time event streaming using Server-Sent Events**
> **Everything you need to receive real-time notifications, messages, and updates**

---

## Table of Contents

1. [What is SSE?](#what-is-sse)
2. [SSE vs WebSocket](#sse-vs-websocket)
3. [Quick Start](#quick-start)
4. [SSE Endpoints](#sse-endpoints)
5. [Authentication](#authentication)
6. [Connection Management](#connection-management)
7. [Event Types & Payloads](#event-types--payloads)
8. [JavaScript Implementation](#javascript-implementation)
9. [React Implementation](#react-implementation)
10. [Error Handling](#error-handling)
11. [Reconnection Strategy](#reconnection-strategy)
12. [Testing](#testing)
13. [Troubleshooting](#troubleshooting)
14. [Production Considerations](#production-considerations)

---

## What is SSE?

**Server-Sent Events (SSE)** is a server push technology that allows a server to send automatic updates to clients via HTTP connection.

### Key Features:
- ✅ **One-way communication** from server to client
- ✅ **Automatic reconnection** built into browser API
- ✅ **Standard HTTP/HTTPS** (no special protocols)
- ✅ **Works through proxies** and firewalls
- ✅ **Simple to implement** compared to WebSockets
- ✅ **Event streaming** with named event types
- ✅ **Lower overhead** than polling

### Use Cases in This Application:
- 🔔 **Real-time messages** - Instant message delivery
- ⌨️ **Typing indicators** - See when someone is typing
- ✓ **Read receipts** - Know when messages are read
- 🟢 **Presence updates** - Online/offline status
- 📢 **Notifications** - System announcements
- 💓 **Heartbeat** - Connection keep-alive

---

## SSE vs WebSocket

| Feature | SSE | WebSocket |
|---------|-----|-----------|
| **Communication** | Server → Client only | Bidirectional |
| **Protocol** | HTTP/HTTPS | ws:// / wss:// |
| **Browser Support** | All modern browsers | All modern browsers |
| **Auto Reconnection** | Built-in | Manual implementation |
| **Proxy Friendly** | ✅ Yes | ⚠️ Needs configuration |
| **Complexity** | Low | Medium |
| **Use Case** | Server push notifications | Real-time bidirectional chat |

**Why we chose SSE:**
- Simpler deployment (no WebSocket proxy config)
- Automatic reconnection
- Standard HTTP (easier debugging)
- Perfect for server-to-client updates
- Client-to-server via REST API (POST requests)

---

## Quick Start

### 1. Install Requirements

No additional libraries needed! SSE is built into browsers via the `EventSource` API.

### 2. Basic Connection

```javascript
const token = 'YOUR_AUTH_TOKEN';
const url = `http://localhost:8000/api/v1/communication/sse/events/?token=${token}`;

const eventSource = new EventSource(url);

eventSource.onopen = () => {
  console.log('✅ Connected to SSE');
};

eventSource.onerror = (error) => {
  console.error('❌ SSE Error:', error);
};

// Listen for events
eventSource.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);
  console.log('New message:', data);
});
```

### 3. Close Connection

```javascript
eventSource.close();
```

---

## SSE Endpoints

### 1. Main Events Endpoint

**URL:** `GET /api/v1/communication/sse/events/`

**Full URL Example:**
```
http://localhost:8000/api/v1/communication/sse/events/?token=9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Authentication:** Token via query parameter

**Query Parameters:**
- `token` (required): Your authentication token

**Request Headers:**
```http
GET /api/v1/communication/sse/events/?token=YOUR_TOKEN HTTP/1.1
Host: localhost:8000
Accept: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

**Response Headers:**
```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
X-Accel-Buffering: no
Connection: keep-alive
```

**Response Format:**
```
event: connected
data: {"status":"connected","user_id":789}

event: message
data: {"id":456,"sender_id":123,"message":"Hello!","timestamp":"2026-01-09T10:30:00Z"}

event: heartbeat
data: {"timestamp":1736419800.123}
```

---

### 2. Test Endpoint

**URL:** `GET /api/v1/communication/sse/test/`

**Full URL Example:**
```
http://localhost:8000/api/v1/communication/sse/test/
```

**Authentication:** Not required (public test endpoint)

**Request Headers:**
```http
GET /api/v1/communication/sse/test/ HTTP/1.1
Host: localhost:8000
Accept: text/event-stream
Cache-Control: no-cache
```

**Response:** Sends 5 test events then completes

**Test Events:**
```
event: test
data: {"count":0,"message":"Test event 0"}

event: test
data: {"count":1,"message":"Test event 1"}

event: test
data: {"count":2,"message":"Test event 2"}

event: test
data: {"count":3,"message":"Test event 3"}

event: test
data: {"count":4,"message":"Test event 4"}

event: complete
data: {"message":"Test complete"}
```

**Usage:**
```javascript
const eventSource = new EventSource('http://localhost:8000/api/v1/communication/sse/test/');

eventSource.addEventListener('test', (event) => {
  const data = JSON.parse(event.data);
  console.log('Test event:', data);
});

eventSource.addEventListener('complete', (event) => {
  console.log('Test complete');
  eventSource.close();
});
```

---

## Authentication

### Getting Auth Token

**Step 1: Login to get token**

```javascript
const response = await fetch('http://localhost:8000/api/v1/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'john_doe',
    password: 'securePassword123'
  })
});

const data = await response.json();
const token = data.key;  // Save this token
```

**Step 2: Use token for SSE connection**

```javascript
const url = `http://localhost:8000/api/v1/communication/sse/events/?token=${token}`;
const eventSource = new EventSource(url);
```

### Token Storage

```javascript
// Save token
localStorage.setItem('authToken', token);

// Retrieve token
const token = localStorage.getItem('authToken');

// Use in SSE URL
const sseUrl = `${baseUrl}/communication/sse/events/?token=${token}`;
```

### Security Notes

⚠️ **Important:**
- Token is passed in URL query parameter (not in headers, as EventSource doesn't support custom headers)
- Use HTTPS in production to encrypt the token
- Token should be valid and not expired
- Server validates token before establishing connection

---

## Connection Management

### Connection Lifecycle

```javascript
const eventSource = new EventSource(url);

// 1. Connection Opening
eventSource.addEventListener('open', () => {
  console.log('Connection opening...');
});

// 2. Connection Opened
eventSource.onopen = () => {
  console.log('✅ Connected');
};

// 3. Receiving Events
eventSource.addEventListener('message', (event) => {
  console.log('Event received:', event.data);
});

// 4. Connection Error
eventSource.onerror = (error) => {
  console.error('❌ Connection error:', error);
  // EventSource will auto-reconnect
};

// 5. Close Connection (manual)
eventSource.close();
```

### Connection States

```javascript
// Check connection state
console.log(eventSource.readyState);

// States:
// 0 = CONNECTING
// 1 = OPEN
// 2 = CLOSED

switch(eventSource.readyState) {
  case EventSource.CONNECTING:
    console.log('🟡 Connecting...');
    break;
  case EventSource.OPEN:
    console.log('🟢 Connected');
    break;
  case EventSource.CLOSED:
    console.log('🔴 Closed');
    break;
}
```

### Auto-Reconnection

**Built-in behavior:**
- EventSource automatically reconnects on connection loss
- Default retry interval: ~3 seconds
- Browser handles reconnection automatically

**Manual reconnection:**
```javascript
let eventSource = null;

function connect() {
  eventSource = new EventSource(url);

  eventSource.onerror = (error) => {
    console.error('Connection error');
    eventSource.close();

    // Reconnect after 5 seconds
    setTimeout(connect, 5000);
  };
}

connect();
```

---

## Event Types & Payloads

### 1. Connected Event

**Event Type:** `connected`

**When:** Immediately after successful connection

**Payload:**
```json
{
  "status": "connected",
  "user_id": 789
}
```

**Example:**
```javascript
eventSource.addEventListener('connected', (event) => {
  const data = JSON.parse(event.data);
  console.log(`Connected as user ${data.user_id}`);
});
```

---

### 2. Message Event

**Event Type:** `message`

**When:** New chat message received

**Payload:**
```json
{
  "id": 456,
  "sender_id": 123,
  "sender_name": "Jane Smith",
  "receiver_id": 789,
  "message": "Hello! How are you?",
  "attachment": "https://s3.amazonaws.com/files/image.jpg",
  "attachment_type": "image",
  "timestamp": "2026-01-09T10:30:00Z",
  "is_read": false,
  "conversation_id": 1
}
```

**Fields:**
- `id` (integer): Message ID
- `sender_id` (integer): User ID of sender
- `sender_name` (string): Full name of sender
- `receiver_id` (integer): User ID of receiver
- `message` (string): Message text content
- `attachment` (string|null): URL to attachment file
- `attachment_type` (string|null): Type of attachment (image/video/document)
- `timestamp` (string): ISO 8601 timestamp
- `is_read` (boolean): Read status
- `conversation_id` (integer): Conversation ID

**Example:**
```javascript
eventSource.addEventListener('message', (event) => {
  const message = JSON.parse(event.data);

  // Display message in UI
  addMessageToChat(message);

  // Show notification if not focused
  if (!document.hasFocus()) {
    showNotification(message.sender_name, message.message);
  }

  // Play sound
  playNotificationSound();
});
```

---

### 3. Typing Event

**Event Type:** `typing`

**When:** Someone starts or stops typing

**Payload:**
```json
{
  "sender_id": 123,
  "sender_name": "Jane Smith",
  "is_typing": true
}
```

**Fields:**
- `sender_id` (integer): User ID who is typing
- `sender_name` (string): Full name of user
- `is_typing` (boolean): true = started typing, false = stopped typing

**Example:**
```javascript
const typingUsers = new Set();

eventSource.addEventListener('typing', (event) => {
  const data = JSON.parse(event.data);

  if (data.is_typing) {
    typingUsers.add(data.sender_id);
    showTypingIndicator(data.sender_name);
  } else {
    typingUsers.delete(data.sender_id);
    hideTypingIndicator(data.sender_id);
  }

  // Auto-hide after 5 seconds
  if (data.is_typing) {
    setTimeout(() => {
      typingUsers.delete(data.sender_id);
      hideTypingIndicator(data.sender_id);
    }, 5000);
  }
});
```

---

### 4. Read Receipt Event

**Event Type:** `read_receipt`

**When:** Your sent message was read by recipient

**Payload:**
```json
{
  "message_id": 456,
  "reader_id": 123,
  "reader_name": "Jane Smith",
  "read_at": "2026-01-09T10:35:00Z"
}
```

**Fields:**
- `message_id` (integer): ID of message that was read
- `reader_id` (integer): User ID who read the message
- `reader_name` (string): Full name of reader
- `read_at` (string|null): ISO 8601 timestamp when read

**Example:**
```javascript
eventSource.addEventListener('read_receipt', (event) => {
  const data = JSON.parse(event.data);

  // Update message status in UI
  updateMessageReadStatus(data.message_id, true, data.read_at);

  // Change checkmark from ✓ to ✓✓
  const messageElement = document.querySelector(`[data-message-id="${data.message_id}"]`);
  if (messageElement) {
    messageElement.querySelector('.read-indicator').textContent = '✓✓';
  }
});
```

---

### 5. Notification Event

**Event Type:** `notification`

**When:** System notification (notice published, event created, etc.)

**Payload:**
```json
{
  "title": "New Notice",
  "message": "Class cancelled tomorrow",
  "notification_type": "notice",
  "data": {
    "notice_id": 42,
    "is_urgent": true,
    "publish_date": "2026-01-09"
  }
}
```

**Fields:**
- `title` (string): Notification title
- `message` (string): Notification message
- `notification_type` (string): Type of notification (notice/event/announcement)
- `data` (object): Additional notification data (varies by type)

**Example:**
```javascript
eventSource.addEventListener('notification', (event) => {
  const notification = JSON.parse(event.data);

  // Show toast notification
  showToast(notification.title, notification.message, notification.notification_type);

  // Add to notification center
  addToNotificationCenter(notification);

  // Update notification badge
  incrementNotificationBadge();
});
```

---

### 6. Heartbeat Event

**Event Type:** `heartbeat`

**When:** Every 30 seconds (keep-alive)

**Payload:**
```json
{
  "timestamp": 1736419800.123
}
```

**Fields:**
- `timestamp` (number): Unix timestamp in seconds

**Purpose:**
- Keeps connection alive
- Prevents timeout by proxies/load balancers
- Can be used to detect connection issues

**Example:**
```javascript
let lastHeartbeat = Date.now();

eventSource.addEventListener('heartbeat', (event) => {
  const data = JSON.parse(event.data);
  lastHeartbeat = Date.now();
  console.log('💓 Heartbeat received');
});

// Check for stale connection
setInterval(() => {
  const timeSinceLastHeartbeat = Date.now() - lastHeartbeat;

  if (timeSinceLastHeartbeat > 60000) {
    // No heartbeat for 60 seconds - connection might be dead
    console.warn('⚠️ No heartbeat for 60 seconds');
    eventSource.close();
    reconnect();
  }
}, 10000);
```

---

### 7. Disconnected Event

**Event Type:** `disconnected`

**When:** Server is closing the connection

**Payload:**
```json
{
  "status": "disconnected"
}
```

**Example:**
```javascript
eventSource.addEventListener('disconnected', (event) => {
  console.log('Server closed connection');
  eventSource.close();
});
```

---

## JavaScript Implementation

### Basic Implementation

```javascript
// sse-client.js

class SSEClient {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl;
    this.token = token;
    this.eventSource = null;
    this.listeners = {};
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    const url = `${this.baseUrl}/communication/sse/events/?token=${this.token}`;

    console.log('Connecting to SSE:', url);
    this.eventSource = new EventSource(url);

    // Connection opened
    this.eventSource.onopen = () => {
      console.log('✅ SSE Connected');
      this.reconnectAttempts = 0;
      this.trigger('open');
    };

    // Connection error
    this.eventSource.onerror = (error) => {
      console.error('❌ SSE Error:', error);

      if (this.eventSource.readyState === EventSource.CLOSED) {
        this.handleReconnect();
      }

      this.trigger('error', error);
    };

    // Listen for all event types
    this.setupEventListeners();
  }

  setupEventListeners() {
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
      this.eventSource.addEventListener(eventType, (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log(`📨 [${eventType}]:`, data);
          this.trigger(eventType, data);
        } catch (error) {
          console.error(`Failed to parse ${eventType}:`, error);
        }
      });
    });
  }

  on(eventType, callback) {
    if (!this.listeners[eventType]) {
      this.listeners[eventType] = [];
    }
    this.listeners[eventType].push(callback);
  }

  off(eventType, callback) {
    if (!this.listeners[eventType]) return;

    this.listeners[eventType] = this.listeners[eventType].filter(
      cb => cb !== callback
    );
  }

  trigger(eventType, data) {
    if (!this.listeners[eventType]) return;

    this.listeners[eventType].forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in ${eventType} listener:`, error);
      }
    });
  }

  handleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.trigger('max_reconnect_attempts');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

    setTimeout(() => {
      this.connect();
    }, delay);
  }

  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.listeners = {};
    console.log('Disconnected from SSE');
  }

  isConnected() {
    return this.eventSource?.readyState === EventSource.OPEN;
  }
}

// Usage
const token = localStorage.getItem('authToken');
const sseClient = new SSEClient('http://localhost:8000/api/v1', token);

// Connect
sseClient.connect();

// Listen for events
sseClient.on('connected', (data) => {
  console.log('Connected as user:', data.user_id);
});

sseClient.on('message', (message) => {
  console.log('New message:', message);
  displayMessage(message);
});

sseClient.on('typing', (data) => {
  if (data.is_typing) {
    showTypingIndicator(data.sender_name);
  } else {
    hideTypingIndicator(data.sender_id);
  }
});

sseClient.on('read_receipt', (data) => {
  updateMessageStatus(data.message_id, 'read');
});

sseClient.on('notification', (notification) => {
  showNotification(notification.title, notification.message);
});

// Disconnect when leaving
window.addEventListener('beforeunload', () => {
  sseClient.disconnect();
});
```

---

## React Implementation

### Custom Hook

```javascript
// hooks/useSSE.js
import { useEffect, useCallback, useRef, useState } from 'react';

export const useSSE = (onEvent, token, enabled = true) => {
  const eventSourceRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef(null);

  const baseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

  const connect = useCallback(() => {
    if (!enabled || !token) {
      console.log('SSE not enabled or no token');
      return;
    }

    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const url = `${baseUrl}/communication/sse/events/?token=${token}`;
    console.log('🔌 Connecting to SSE:', url);

    const eventSource = new EventSource(url);

    eventSource.onopen = () => {
      console.log('✅ SSE Connected');
      setIsConnected(true);
      setError(null);
      reconnectAttemptsRef.current = 0;
    };

    eventSource.onerror = (err) => {
      console.error('❌ SSE Error:', err);
      setIsConnected(false);
      setError('Connection error');

      // Auto-reconnect with exponential backoff
      if (eventSource.readyState === EventSource.CLOSED) {
        eventSource.close();

        const maxAttempts = 5;
        if (reconnectAttemptsRef.current < maxAttempts) {
          reconnectAttemptsRef.current++;
          const delay = Math.min(
            1000 * Math.pow(2, reconnectAttemptsRef.current),
            30000
          );

          console.log(`🔄 Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current})`);

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else {
          console.error('Max reconnection attempts reached');
        }
      }
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
          console.log(`📨 SSE [${eventType}]:`, data);

          // Call the callback with event type and data
          onEvent({
            type: eventType,
            data: data
          });
        } catch (error) {
          console.error(`Failed to parse SSE event [${eventType}]:`, error);
        }
      });
    });

    eventSourceRef.current = eventSource;
  }, [enabled, token, baseUrl, onEvent]);

  useEffect(() => {
    connect();

    return () => {
      // Cleanup
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [connect]);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      setIsConnected(false);
    }
  }, []);

  const reconnect = useCallback(() => {
    reconnectAttemptsRef.current = 0;
    connect();
  }, [connect]);

  return {
    isConnected,
    error,
    disconnect,
    reconnect
  };
};
```

### Usage in Component

```javascript
// components/Chat.jsx
import React, { useState, useCallback } from 'react';
import { useSSE } from '../hooks/useSSE';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [typingUsers, setTypingUsers] = useState(new Set());
  const token = localStorage.getItem('authToken');

  // Handle SSE events
  const handleSSEEvent = useCallback((event) => {
    const { type, data } = event;

    switch (type) {
      case 'connected':
        console.log('Connected to chat server');
        break;

      case 'message':
        // Add new message
        setMessages(prev => [...prev, data]);
        break;

      case 'typing':
        // Update typing indicators
        setTypingUsers(prev => {
          const newSet = new Set(prev);
          if (data.is_typing) {
            newSet.add(data.sender_id);

            // Auto-remove after 5 seconds
            setTimeout(() => {
              setTypingUsers(current => {
                const updated = new Set(current);
                updated.delete(data.sender_id);
                return updated;
              });
            }, 5000);
          } else {
            newSet.delete(data.sender_id);
          }
          return newSet;
        });
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
        showToast(data.title, data.message);
        break;

      case 'heartbeat':
        // Connection is alive
        break;

      default:
        console.log('Unknown event type:', type);
    }
  }, []);

  // Connect to SSE
  const { isConnected, error, reconnect } = useSSE(
    handleSSEEvent,
    token,
    true // enabled
  );

  return (
    <div className="chat">
      {/* Connection Status */}
      <div className="connection-status">
        {isConnected ? (
          <span className="status-connected">🟢 Connected</span>
        ) : error ? (
          <span className="status-error">
            🔴 Disconnected
            <button onClick={reconnect}>Reconnect</button>
          </span>
        ) : (
          <span className="status-connecting">🟡 Connecting...</span>
        )}
      </div>

      {/* Messages */}
      <div className="messages">
        {messages.map(msg => (
          <div key={msg.id} className="message">
            <strong>{msg.sender_name}:</strong> {msg.message}
            {msg.is_read && <span className="read-indicator">✓✓</span>}
          </div>
        ))}
      </div>

      {/* Typing Indicator */}
      {typingUsers.size > 0 && (
        <div className="typing-indicator">
          Someone is typing...
        </div>
      )}
    </div>
  );
};

export default Chat;
```

---

## Error Handling

### Common Errors

#### 1. Unauthorized (401)

**Cause:** Invalid or missing token

**SSE Response:**
```
event: error
data: {"error":"Unauthorized"}
```

**Solution:**
```javascript
eventSource.addEventListener('error', (event) => {
  if (event.target.readyState === EventSource.CLOSED) {
    // Check if unauthorized
    const token = localStorage.getItem('authToken');
    if (!token) {
      console.error('No auth token - redirecting to login');
      window.location.href = '/login';
    }
  }
});
```

#### 2. Connection Failed

**Cause:** Server unreachable, network issue

**Solution:**
```javascript
let connectionAttempts = 0;

eventSource.onerror = (error) => {
  console.error('Connection error');

  if (connectionAttempts < 5) {
    connectionAttempts++;
    // EventSource will auto-reconnect
  } else {
    console.error('Max connection attempts reached');
    eventSource.close();
    showErrorMessage('Unable to connect to server');
  }
};

eventSource.onopen = () => {
  connectionAttempts = 0; // Reset on successful connection
};
```

#### 3. Redis Not Available

**Cause:** Redis server is down

**SSE Response:**
```
event: error
data: {"error":"Redis not available"}
```

**Solution:**
```javascript
eventSource.addEventListener('error', (event) => {
  try {
    const data = JSON.parse(event.data);
    if (data.error === 'Redis not available') {
      showErrorMessage('Real-time features temporarily unavailable');
    }
  } catch (e) {
    // Not a JSON error event
  }
});
```

---

## Reconnection Strategy

### Exponential Backoff

```javascript
class SSEConnection {
  constructor(url) {
    this.url = url;
    this.eventSource = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectTimeout = null;
  }

  connect() {
    this.eventSource = new EventSource(this.url);

    this.eventSource.onopen = () => {
      console.log('Connected');
      this.reconnectAttempts = 0;
    };

    this.eventSource.onerror = () => {
      console.error('Connection error');
      this.reconnect();
    };
  }

  reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.onMaxReconnectAttempts();
      return;
    }

    this.reconnectAttempts++;

    // Exponential backoff: 1s, 2s, 4s, 8s, 16s, 32s (max)
    const delay = Math.min(
      1000 * Math.pow(2, this.reconnectAttempts - 1),
      32000
    );

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

    this.reconnectTimeout = setTimeout(() => {
      this.connect();
    }, delay);
  }

  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
    if (this.eventSource) {
      this.eventSource.close();
    }
  }

  onMaxReconnectAttempts() {
    // Override this method
    alert('Unable to connect. Please check your connection and refresh.');
  }
}
```

---

## Testing

### Test Connection

```javascript
function testSSEConnection() {
  const testUrl = 'http://localhost:8000/api/v1/communication/sse/test/';
  const eventSource = new EventSource(testUrl);

  console.log('Testing SSE connection...');

  eventSource.addEventListener('test', (event) => {
    const data = JSON.parse(event.data);
    console.log('✅ Test event received:', data);
  });

  eventSource.addEventListener('complete', (event) => {
    const data = JSON.parse(event.data);
    console.log('✅ Test complete:', data);
    eventSource.close();
  });

  eventSource.onerror = (error) => {
    console.error('❌ Test failed:', error);
    eventSource.close();
  };

  // Auto-close after 10 seconds
  setTimeout(() => {
    console.log('Test timeout - closing connection');
    eventSource.close();
  }, 10000);
}

// Run test
testSSEConnection();
```

### Test with Auth Token

```javascript
function testAuthenticatedSSE(token) {
  const url = `http://localhost:8000/api/v1/communication/sse/events/?token=${token}`;
  const eventSource = new EventSource(url);

  console.log('Testing authenticated SSE...');

  let receivedEvents = {
    connected: false,
    heartbeat: false
  };

  eventSource.addEventListener('connected', (event) => {
    console.log('✅ Connected event received');
    receivedEvents.connected = true;
  });

  eventSource.addEventListener('heartbeat', (event) => {
    console.log('✅ Heartbeat received');
    receivedEvents.heartbeat = true;
  });

  eventSource.onerror = (error) => {
    console.error('❌ Connection error:', error);
  };

  // Check after 35 seconds (should receive at least one heartbeat)
  setTimeout(() => {
    console.log('Test results:', receivedEvents);

    if (receivedEvents.connected && receivedEvents.heartbeat) {
      console.log('✅ All tests passed!');
    } else {
      console.error('❌ Some tests failed');
    }

    eventSource.close();
  }, 35000);
}

// Run with your token
const token = localStorage.getItem('authToken');
testAuthenticatedSSE(token);
```

---

## Troubleshooting

### Issue 1: Connection Immediately Closes

**Symptoms:**
- EventSource immediately fires `onerror`
- `readyState` goes to `CLOSED` (2)

**Possible Causes:**
1. Invalid or missing token
2. CORS issues
3. Server not running
4. Wrong URL

**Debug Steps:**

```javascript
const eventSource = new EventSource(url);

console.log('Initial state:', eventSource.readyState);

eventSource.onopen = () => {
  console.log('Opened! State:', eventSource.readyState);
};

eventSource.onerror = (error) => {
  console.error('Error! State:', eventSource.readyState);
  console.error('Error object:', error);

  // Check if it's a network error
  if (eventSource.readyState === EventSource.CONNECTING) {
    console.log('Network error or CORS issue');
  } else if (eventSource.readyState === EventSource.CLOSED) {
    console.log('Connection was rejected by server (auth issue?)');
  }
};
```

**Solutions:**
- Check token validity
- Check backend CORS settings
- Check server logs
- Try test endpoint first

---

### Issue 2: Events Not Received

**Symptoms:**
- Connection established but no events received
- Only heartbeat events received

**Debug:**

```javascript
// Log all raw events
eventSource.onmessage = (event) => {
  console.log('Raw event:', event);
  console.log('Event type:', event.type);
  console.log('Event data:', event.data);
};

// Log specific events
['connected', 'message', 'typing', 'heartbeat'].forEach(eventType => {
  eventSource.addEventListener(eventType, (event) => {
    console.log(`Event [${eventType}]:`, event.data);
  });
});
```

**Solutions:**
- Check event listener names match server event names
- Check if events are being sent (server logs)
- Verify JSON parsing doesn't fail

---

### Issue 3: Memory Leaks

**Symptoms:**
- Browser gets slower over time
- Multiple connections opened

**Solution:**

```javascript
// Properly cleanup when component unmounts
useEffect(() => {
  const eventSource = new EventSource(url);

  // Setup listeners...

  return () => {
    // Cleanup
    eventSource.close();
    console.log('EventSource closed');
  };
}, [url]);

// Or in vanilla JS
window.addEventListener('beforeunload', () => {
  eventSource.close();
});
```

---

### Issue 4: CORS Errors

**Error:**
```
Access to resource blocked by CORS policy
```

**Solution:**

Check backend allows your origin:

```python
# Django settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]
```

For EventSource specifically:
```python
CORS_ALLOW_CREDENTIALS = True
```

---

## Production Considerations

### 1. Use HTTPS

⚠️ **Important:** In production, always use HTTPS

```javascript
// Development
const baseUrl = 'http://localhost:8000/api/v1';

// Production
const baseUrl = 'https://api.yourdomain.com/api/v1';

// Or use environment variable
const baseUrl = process.env.REACT_APP_API_BASE_URL;
```

### 2. Token Security

✅ **Best Practices:**
- Don't log tokens to console in production
- Use secure cookies if possible
- Implement token refresh
- Clear tokens on logout

```javascript
// Don't do this in production:
console.log('Token:', token); // ❌

// Do this instead:
if (process.env.NODE_ENV === 'development') {
  console.log('Token:', token.substring(0, 10) + '...'); // ✅
}
```

### 3. Proxy Configuration

**Nginx:**

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

### 4. Connection Limits

Browser limits:
- Chrome: 6 connections per domain
- Firefox: 6 connections per domain
- Safari: 6 connections per domain

**Solution:** Use only one SSE connection per user

```javascript
// Singleton pattern
class SSEManager {
  static instance = null;

  static getInstance(url, token) {
    if (!SSEManager.instance) {
      SSEManager.instance = new SSEConnection(url, token);
    }
    return SSEManager.instance;
  }
}

// Usage
const sse = SSEManager.getInstance(url, token);
```

### 5. Monitoring

```javascript
// Track connection metrics
const metrics = {
  connectTime: null,
  disconnectTime: null,
  eventsReceived: 0,
  reconnectionAttempts: 0
};

eventSource.onopen = () => {
  metrics.connectTime = Date.now();
};

eventSource.addEventListener('message', () => {
  metrics.eventsReceived++;
});

// Send to analytics
setInterval(() => {
  sendToAnalytics(metrics);
}, 60000);
```

---

## Summary

### Connection Checklist

- [ ] Get auth token from login
- [ ] Store token in localStorage
- [ ] Create EventSource with token in URL
- [ ] Listen for `connected` event
- [ ] Listen for specific event types (`message`, `typing`, etc.)
- [ ] Handle errors and reconnection
- [ ] Close connection on cleanup

### Key URLs

**Production:**
```
https://yourdomain.com/api/v1/communication/sse/events/?token=YOUR_TOKEN
```

**Development:**
```
http://localhost:8000/api/v1/communication/sse/events/?token=YOUR_TOKEN
```

**Test:**
```
http://localhost:8000/api/v1/communication/sse/test/
```

### Event Types Reference

| Event | When | Key Fields |
|-------|------|------------|
| `connected` | Connection established | `user_id` |
| `message` | New message | `sender_id`, `message`, `timestamp` |
| `typing` | Typing indicator | `sender_id`, `is_typing` |
| `read_receipt` | Message read | `message_id`, `read_at` |
| `notification` | System notification | `title`, `message`, `type` |
| `heartbeat` | Every 30s | `timestamp` |

---

## Next Steps

1. ✅ Copy SSE connection code
2. ✅ Test with test endpoint
3. ✅ Implement event handlers
4. ✅ Add error handling
5. ✅ Test with real messages
6. ✅ Deploy to production

**You're ready to integrate SSE!** 🚀

For complete API integration guide, see **FRONTEND_INTEGRATION_GUIDE.md**
