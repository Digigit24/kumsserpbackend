# WebSocket API Documentation

Complete reference for WebSocket endpoints, message types, and event handling.

## Table of Contents

- [Connection](#connection)
- [Chat WebSocket](#chat-websocket)
- [Notifications WebSocket](#notifications-websocket)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Connection Management](#connection-management)

---

## Connection

### Chat WebSocket

**Endpoint:** `ws://domain/ws/chat/?token=YOUR_TOKEN`

**Protocol:** WebSocket (ws:// for HTTP, wss:// for HTTPS)

**Authentication:** Token in query parameter

**Example:**
```javascript
const token = localStorage.getItem('authToken');
const wsUrl = `ws://localhost:8000/ws/chat/?token=${token}`;
const chatSocket = new WebSocket(wsUrl);
```

### Notifications WebSocket

**Endpoint:** `ws://domain/ws/notifications/?token=YOUR_TOKEN`

**Example:**
```javascript
const token = localStorage.getItem('authToken');
const wsUrl = `ws://localhost:8000/ws/notifications/?token=${token}`;
const notificationSocket = new WebSocket(wsUrl);
```

---

## Chat WebSocket

### Connection Events

#### Connected

Received immediately after successful connection.

**Server sends:**
```json
{
  "type": "connection",
  "status": "connected",
  "user_id": 123,
  "timestamp": "2026-01-12T10:30:00Z"
}
```

**Description:** Confirms WebSocket connection is established. User is marked as online.

---

### Message Types (Client → Server)

#### 1. Send Message

Send a chat message to another user.

**Client sends:**
```json
{
  "type": "message",
  "receiver_id": 456,
  "message": "Hello! How are you? 👋",
  "temp_id": "client-generated-uuid"  // Optional: for client-side tracking
}
```

**Fields:**
- `type` (required): Must be "message"
- `receiver_id` (required): ID of the message recipient
- `message` (required): Message content (supports emojis, UTF-8)
- `temp_id` (optional): Client-generated ID for tracking before server confirmation
- `attachment` (optional): Attachment URL or file reference

**Server responds:**
```json
{
  "type": "message_sent",
  "id": 789,
  "conversation_id": 12,
  "timestamp": "2026-01-12T10:30:00Z",
  "temp_id": "client-generated-uuid"
}
```

**Receiver gets:**
```json
{
  "type": "message",
  "id": 789,
  "conversation_id": 12,
  "sender_id": 123,
  "sender_name": "John Doe",
  "sender_avatar": "https://example.com/avatar.jpg",
  "receiver_id": 456,
  "message": "Hello! How are you? 👋",
  "attachment": null,
  "attachment_type": null,
  "timestamp": "2026-01-12T10:30:00Z",
  "is_read": false,
  "delivered_at": "2026-01-12T10:30:00Z"
}
```

---

#### 2. Typing Indicator

Notify another user that you're typing.

**Client sends:**
```json
{
  "type": "typing",
  "receiver_id": 456,
  "is_typing": true
}
```

**Fields:**
- `type` (required): Must be "typing"
- `receiver_id` (required): ID of the user to notify
- `is_typing` (required): `true` when starting to type, `false` when stopped

**Receiver gets:**
```json
{
  "type": "typing_indicator",
  "sender_id": 123,
  "sender_name": "John Doe",
  "is_typing": true,
  "timestamp": "2026-01-12T10:30:05Z"
}
```

**Auto-timeout:** Typing indicators automatically expire after 5 seconds.

**Best Practice:**
```javascript
let typingTimeout;

function sendTyping(isTyping) {
  clearTimeout(typingTimeout);

  chatSocket.send(JSON.stringify({
    type: 'typing',
    receiver_id: currentReceiverId,
    is_typing: isTyping
  }));

  if (isTyping) {
    // Auto-stop after 3 seconds
    typingTimeout = setTimeout(() => {
      sendTyping(false);
    }, 3000);
  }
}

// On input
messageInput.addEventListener('input', () => {
  sendTyping(true);
});
```

---

#### 3. Read Receipt

Mark messages as read.

**Client sends:**
```json
{
  "type": "read_receipt",
  "message_ids": [789, 790, 791]
}
```

**OR mark by conversation:**
```json
{
  "type": "read_receipt",
  "conversation_id": 12
}
```

**OR mark by sender:**
```json
{
  "type": "read_receipt",
  "sender_id": 123
}
```

**Fields:**
- `type` (required): Must be "read_receipt"
- `message_ids` (optional): Array of message IDs to mark as read
- `conversation_id` (optional): Mark all messages in conversation as read
- `sender_id` (optional): Mark all messages from sender as read

**Server responds:**
```json
{
  "type": "read_receipt_sent",
  "count": 3
}
```

**Original sender receives:**
```json
{
  "type": "read_receipt",
  "message_id": 789,
  "conversation_id": 12,
  "reader_id": 456,
  "reader_name": "Jane Smith",
  "read_at": "2026-01-12T10:31:00Z"
}
```

---

#### 4. Get Online Status

Check if a user is currently online.

**Client sends:**
```json
{
  "type": "get_online_status",
  "user_id": 456
}
```

**Server responds:**
```json
{
  "type": "online_status",
  "user_id": 456,
  "is_online": true,
  "timestamp": "2026-01-12T10:30:00Z"
}
```

---

### Message Types (Server → Client)

#### 1. Message Received

New message from another user.

**Server sends:**
```json
{
  "type": "message",
  "id": 789,
  "conversation_id": 12,
  "sender_id": 123,
  "sender_name": "John Doe",
  "sender_avatar": "https://example.com/avatar.jpg",
  "receiver_id": 456,
  "message": "Hello! 👋",
  "attachment": null,
  "attachment_type": null,
  "timestamp": "2026-01-12T10:30:00Z",
  "is_read": false,
  "delivered_at": "2026-01-12T10:30:00Z"
}
```

**Action:** Display message in chat UI, send delivery receipt automatically.

---

#### 2. Typing Indicator

User is typing.

**Server sends:**
```json
{
  "type": "typing_indicator",
  "sender_id": 123,
  "sender_name": "John Doe",
  "is_typing": true,
  "timestamp": "2026-01-12T10:30:05Z"
}
```

**Action:** Show "John Doe is typing..." indicator in UI.

---

#### 3. Read Receipt

Your message was read.

**Server sends:**
```json
{
  "type": "read_receipt",
  "message_id": 789,
  "conversation_id": 12,
  "reader_id": 456,
  "reader_name": "Jane Smith",
  "read_at": "2026-01-12T10:31:00Z"
}
```

**Action:** Update message status to "read" (✓✓).

---

#### 4. Delivery Receipt

Your message was delivered.

**Server sends:**
```json
{
  "type": "delivery_receipt",
  "message_id": 789,
  "delivered_at": "2026-01-12T10:30:01Z"
}
```

**Action:** Update message status to "delivered" (✓).

---

#### 5. Online Status Changed

User's online status changed.

**Server sends:**
```json
{
  "type": "online_status_changed",
  "user_id": 456,
  "is_online": true,
  "timestamp": "2026-01-12T10:30:00Z"
}
```

**Action:** Update user's online indicator in UI.

---

## Notifications WebSocket

### Connection Events

#### Connected

**Server sends:**
```json
{
  "type": "connection",
  "status": "connected",
  "user_id": 123,
  "unread_count": 5,
  "timestamp": "2026-01-12T10:30:00Z"
}
```

---

### Message Types (Client → Server)

#### 1. Mark Notification Read

Mark a specific notification as read.

**Client sends:**
```json
{
  "type": "mark_read",
  "notification_id": 789
}
```

**Server responds:**
```json
{
  "type": "notification_read",
  "notification_id": 789,
  "unread_count": 4
}
```

---

#### 2. Mark All Notifications Read

Mark all notifications as read.

**Client sends:**
```json
{
  "type": "mark_all_read"
}
```

**Server responds:**
```json
{
  "type": "all_notifications_read",
  "count": 5,
  "unread_count": 0
}
```

---

#### 3. Get Unread Count

Get current unread notification count.

**Client sends:**
```json
{
  "type": "get_unread_count"
}
```

**Server responds:**
```json
{
  "type": "unread_count",
  "count": 5
}
```

---

### Message Types (Server → Client)

#### 1. New Notification

New notification received.

**Server sends:**
```json
{
  "type": "notification",
  "notification": {
    "id": 789,
    "notification_type": "message",
    "title": "New Message",
    "message": "John Doe sent you a message",
    "link": "/chat/123",
    "icon": "message",
    "priority": "normal",
    "is_read": false,
    "created_at": "2026-01-12T10:30:00Z"
  }
}
```

**Action:** Display notification banner/toast, update unread count.

---

#### 2. Notification Update

Notification was updated (read, dismissed, etc.).

**Server sends:**
```json
{
  "type": "notification_update",
  "event": "notification_read",
  "notification_id": 789,
  "is_read": true,
  "read_at": "2026-01-12T10:31:00Z"
}
```

---

## Authentication

### Token Authentication

All WebSocket connections require authentication via token in query parameter.

**Format:**
```
ws://domain/ws/chat/?token=YOUR_AUTH_TOKEN
```

**Example:**
```javascript
const token = localStorage.getItem('authToken');
const ws = new WebSocket(`ws://localhost:8000/ws/chat/?token=${token}`);
```

### Token Generation

Tokens are generated via REST API login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"secret"}'
```

**Response:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {...}
}
```

---

## Error Handling

### Error Messages

**Format:**
```json
{
  "type": "error",
  "error": "Error description"
}
```

### Common Errors

#### 1. Authentication Failed

**Code:** 4001
**Reason:** Invalid or missing token

**Action:** Reconnect with valid token

---

#### 2. Rate Limit Exceeded

**Code:** 4029
**Reason:** Too many connections from same IP

**Action:** Wait and retry with exponential backoff

---

#### 3. Invalid Message Format

**Error:**
```json
{
  "type": "error",
  "error": "receiver_id is required"
}
```

**Action:** Fix message format and resend

---

#### 4. User Not Found

**Error:**
```json
{
  "type": "error",
  "error": "Failed to send message. Receiver not found."
}
```

**Action:** Verify receiver_id is valid

---

## Connection Management

### Reconnection Strategy

```javascript
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_INTERVAL = 2000; // Start with 2 seconds

function connectWebSocket() {
  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log('Connected');
    reconnectAttempts = 0;
  };

  ws.onclose = (event) => {
    console.log('Disconnected', event.code);

    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      const delay = RECONNECT_INTERVAL * Math.pow(2, reconnectAttempts);
      setTimeout(() => {
        reconnectAttempts++;
        connectWebSocket();
      }, delay);
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  return ws;
}
```

### Heartbeat/Ping

WebSocket connections automatically send heartbeat pings every 30 seconds to keep connection alive.

**No action required from client.**

### Online Status

User is automatically marked:
- **Online:** When WebSocket connects
- **Offline:** When WebSocket disconnects or after 5 minutes of inactivity

**TTL:** 5 minutes (refreshed on each message)

---

## Best Practices

### 1. Message Queue

Queue messages when offline and send when reconnected:

```javascript
const messageQueue = [];

function sendMessage(data) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(data));
  } else {
    messageQueue.push(data);
  }
}

ws.onopen = () => {
  // Send queued messages
  while (messageQueue.length > 0) {
    const msg = messageQueue.shift();
    ws.send(JSON.stringify(msg));
  }
};
```

### 2. Typing Indicator Debounce

Debounce typing indicators to reduce server load:

```javascript
const TYPING_DEBOUNCE = 500; // 500ms
let typingTimer;

input.addEventListener('input', () => {
  clearTimeout(typingTimer);

  // Send typing=true immediately on first keystroke
  if (!isTyping) {
    sendTyping(true);
    isTyping = true;
  }

  // Auto-stop after 500ms of no input
  typingTimer = setTimeout(() => {
    sendTyping(false);
    isTyping = false;
  }, TYPING_DEBOUNCE);
});
```

### 3. Batch Read Receipts

Batch read receipts to reduce server load:

```javascript
let pendingReadReceipts = new Set();
let readReceiptTimer;

function markAsRead(messageId) {
  pendingReadReceipts.add(messageId);

  clearTimeout(readReceiptTimer);
  readReceiptTimer = setTimeout(() => {
    ws.send(JSON.stringify({
      type: 'read_receipt',
      message_ids: Array.from(pendingReadReceipts)
    }));
    pendingReadReceipts.clear();
  }, 1000); // Send batch after 1 second
}
```

### 4. Handle Page Visibility

Pause reconnection attempts when page is hidden:

```javascript
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    // Page hidden, don't reconnect
    shouldReconnect = false;
  } else {
    // Page visible, allow reconnection
    shouldReconnect = true;
    if (ws.readyState !== WebSocket.OPEN) {
      connectWebSocket();
    }
  }
});
```

---

## Complete Example

```javascript
class ChatWebSocket {
  constructor(token, onMessage) {
    this.token = token;
    this.onMessage = onMessage;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 2000;
    this.messageQueue = [];

    this.connect();
  }

  connect() {
    const wsUrl = `ws://localhost:8000/ws/chat/?token=${this.token}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.flushMessageQueue();
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.onMessage(data);
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket disconnected', event.code);
      this.reconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts);
      setTimeout(() => {
        this.reconnectAttempts++;
        this.connect();
      }, delay);
    }
  }

  send(data) {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      this.messageQueue.push(data);
    }
  }

  flushMessageQueue() {
    while (this.messageQueue.length > 0) {
      const msg = this.messageQueue.shift();
      this.ws.send(JSON.stringify(msg));
    }
  }

  sendMessage(receiverId, message) {
    this.send({
      type: 'message',
      receiver_id: receiverId,
      message: message,
      temp_id: Date.now().toString()
    });
  }

  sendTyping(receiverId, isTyping) {
    this.send({
      type: 'typing',
      receiver_id: receiverId,
      is_typing: isTyping
    });
  }

  markAsRead(messageIds) {
    this.send({
      type: 'read_receipt',
      message_ids: messageIds
    });
  }

  close() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Usage
const chatWS = new ChatWebSocket(authToken, (data) => {
  console.log('Received:', data);

  switch(data.type) {
    case 'message':
      displayMessage(data);
      break;
    case 'typing_indicator':
      showTypingIndicator(data);
      break;
    case 'read_receipt':
      updateMessageStatus(data);
      break;
  }
});

// Send message
chatWS.sendMessage(456, 'Hello! 👋');
```

---

**Last Updated:** January 12, 2026
