# Communication API Endpoints - Frontend Integration Guide

## Base URL
All endpoints are prefixed with: **`/api/v1/communication/`**

## Important Notes

⚠️ **Common Mistakes:**
1. ❌ Don't use `/communication/` - always include `/api/v1/` prefix
2. ❌ Don't use old SSE endpoints - they return 410 Gone
3. ✅ Use `/api/v1/communication/poll/events/` for long polling
4. ✅ Use `/api/v1/communication/chats/` for chat operations

## Real-Time Communication (Long Polling)

### 1. Poll for Events (Main Endpoint)
**Endpoint:** `GET /api/v1/communication/poll/events/`

**Authentication:** Token required (query param or header)

**Query Parameters:**
- `token` (string, required): User authentication token

**OR Header:**
```
Authorization: Token YOUR_AUTH_TOKEN
```

**Example Request:**
```javascript
const response = await fetch(
  'http://localhost:8000/api/v1/communication/poll/events/?token=YOUR_TOKEN'
);
const data = await response.json();
```

**Response (200 OK):**
```json
{
  "events": [
    {
      "event": "message",
      "data": {
        "id": 123,
        "sender_id": 456,
        "sender_name": "John Doe",
        "message": "Hello!",
        "timestamp": "2026-01-10T10:30:00Z"
      },
      "timestamp": null
    }
  ],
  "timestamp": 1704888600.123
}
```

**Response (No events - after 5.5s timeout):**
```json
{
  "events": [],
  "timestamp": 1704888600.123
}
```

**Errors:**
- `401 Unauthorized`: Invalid or missing token
- `503 Service Unavailable`: RabbitMQ not available

### 2. Test Endpoint
**Endpoint:** `GET /api/v1/communication/poll/test/`

**Purpose:** Verify long polling is working

**Example:**
```bash
curl http://localhost:8000/api/v1/communication/poll/test/
```

**Response:**
```json
{
  "status": "ok",
  "message": "Long polling is working",
  "timestamp": 1704888600.123
}
```

### 3. Disconnect
**Endpoint:** `POST /api/v1/communication/poll/disconnect/`

**Authentication:** Token required

**Purpose:** Manually mark user as offline

**Response:**
```json
{
  "status": "disconnected",
  "user_id": 123
}
```

## Chat Endpoints

### 1. Send Message
**Endpoint:** `POST /api/v1/communication/chats/`

**Full URL:** `http://localhost:8000/api/v1/communication/chats/`

**Authentication:** Token required (header)

**Headers:**
```
Authorization: Token YOUR_AUTH_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
  "receiver": 456,
  "message": "Hello, how are you?",
  "attachment": null
}
```

**Response (201 Created):**
```json
{
  "id": 123,
  "sender": 789,
  "receiver": 456,
  "message": "Hello, how are you?",
  "attachment": null,
  "is_read": false,
  "timestamp": "2026-01-10T10:30:00Z",
  "conversation_id": 101
}
```

### 2. Get Conversations
**Endpoint:** `GET /api/v1/communication/chats/conversations/`

**Full URL:** `http://localhost:8000/api/v1/communication/chats/conversations/`

**Response:**
```json
[
  {
    "user": {
      "id": 456,
      "username": "johndoe",
      "full_name": "John Doe"
    },
    "last_message": "Hello!",
    "last_message_at": "2026-01-10T10:30:00Z",
    "unread_count": 3,
    "is_online": true
  }
]
```

### 3. Get Conversation Messages
**Endpoint:** `GET /api/v1/communication/chats/conversation/{user_id}/`

**Full URL:** `http://localhost:8000/api/v1/communication/chats/conversation/456/`

**Response:**
```json
{
  "conversation_id": 101,
  "other_user": {
    "id": 456,
    "username": "johndoe",
    "full_name": "John Doe"
  },
  "messages": [
    {
      "id": 123,
      "sender": 789,
      "receiver": 456,
      "message": "Hello!",
      "timestamp": "2026-01-10T10:30:00Z",
      "is_read": true
    }
  ]
}
```

### 4. Mark Messages as Read
**Endpoint:** `POST /api/v1/communication/chats/mark-read/`

**Full URL:** `http://localhost:8000/api/v1/communication/chats/mark-read/`

**Request Body (Option 1 - by message IDs):**
```json
{
  "message_ids": [123, 124, 125]
}
```

**Request Body (Option 2 - by sender):**
```json
{
  "sender_id": 456
}
```

**Response:**
```json
{
  "status": "success",
  "marked_read": 3
}
```

### 5. Send Typing Indicator
**Endpoint:** `POST /api/v1/communication/chats/typing/`

**Full URL:** `http://localhost:8000/api/v1/communication/chats/typing/`

**Request Body:**
```json
{
  "receiver_id": 456,
  "is_typing": true
}
```

**Response:**
```json
{
  "status": "success"
}
```

### 6. Get Unread Count
**Endpoint:** `GET /api/v1/communication/chats/unread-count/`

**Full URL:** `http://localhost:8000/api/v1/communication/chats/unread-count/`

**Response:**
```json
{
  "total_unread": 15,
  "by_sender": {
    "456": 3,
    "789": 7,
    "101": 5
  }
}
```

### 7. Get Online Users
**Endpoint:** `GET /api/v1/communication/chats/online-users/`

**Full URL:** `http://localhost:8000/api/v1/communication/chats/online-users/`

**Response:**
```json
{
  "online_users": [123, 456, 789]
}
```

## Notification Endpoints

### Get Notices
**Endpoint:** `GET /api/v1/communication/notices/`

**Full URL:** `http://localhost:8000/api/v1/communication/notices/`

### Get Events
**Endpoint:** `GET /api/v1/communication/events/`

**Full URL:** `http://localhost:8000/api/v1/communication/events/`

## Migration from SSE

### Old Endpoints (DEPRECATED - Return 410 Gone)
- ❌ `/api/v1/communication/sse/events/`
- ❌ `/api/v1/communication/sse/test/`

These endpoints now return:
```json
{
  "error": "SSE endpoint has been replaced",
  "migration": {
    "old_endpoint": "/api/v1/communication/sse/events/",
    "new_endpoint": "/api/v1/communication/poll/events/",
    "method": "GET"
  }
}
```

**Status Code:** 410 Gone (Permanently removed)

### Migration Checklist

1. ✅ Replace all `/communication/` URLs with `/api/v1/communication/`
2. ✅ Replace EventSource with fetch() polling loop
3. ✅ Update endpoint from `/sse/events/` to `/poll/events/`
4. ✅ Parse response as JSON (not SSE format)
5. ✅ Implement immediate re-polling after receiving response

## Complete Frontend Example

### Chat Component with Long Polling

```javascript
// Configuration
const API_BASE = 'http://localhost:8000/api/v1/communication';
const AUTH_TOKEN = 'your-auth-token-here';

// Long Polling Client
class ChatClient {
  constructor(token) {
    this.token = token;
    this.isPolling = false;
    this.eventHandlers = {};
  }

  // Start polling
  start() {
    this.isPolling = true;
    this.poll();
  }

  // Stop polling
  stop() {
    this.isPolling = false;
  }

  // Polling loop
  async poll() {
    while (this.isPolling) {
      try {
        const response = await fetch(
          `${API_BASE}/poll/events/?token=${this.token}`
        );

        if (!response.ok) {
          console.error('Polling error:', response.status);
          await this.sleep(2000);
          continue;
        }

        const data = await response.json();

        // Process events
        if (data.events && data.events.length > 0) {
          data.events.forEach(event => {
            this.emit(event.event, event.data);
          });
        }
      } catch (error) {
        console.error('Polling error:', error);
        await this.sleep(2000);
      }
    }
  }

  // Send message
  async sendMessage(receiverId, message) {
    const response = await fetch(`${API_BASE}/chats/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        receiver: receiverId,
        message: message
      })
    });

    return await response.json();
  }

  // Mark messages as read
  async markAsRead(senderId) {
    const response = await fetch(`${API_BASE}/chats/mark-read/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        sender_id: senderId
      })
    });

    return await response.json();
  }

  // Send typing indicator
  async sendTyping(receiverId, isTyping) {
    await fetch(`${API_BASE}/chats/typing/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        receiver_id: receiverId,
        is_typing: isTyping
      })
    });
  }

  // Event handling
  on(eventType, handler) {
    if (!this.eventHandlers[eventType]) {
      this.eventHandlers[eventType] = [];
    }
    this.eventHandlers[eventType].push(handler);
  }

  emit(eventType, data) {
    const handlers = this.eventHandlers[eventType] || [];
    handlers.forEach(handler => handler(data));
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Usage
const client = new ChatClient(AUTH_TOKEN);

// Register event handlers
client.on('message', (data) => {
  console.log('New message:', data);
  // Update UI
});

client.on('typing', (data) => {
  console.log(`${data.sender_name} is typing...`);
  // Show typing indicator
});

client.on('read_receipt', (data) => {
  console.log('Message read:', data.message_id);
  // Update message status
});

// Start polling
client.start();

// Send a message
await client.sendMessage(456, 'Hello!');

// Send typing indicator
await client.sendTyping(456, true);

// Stop polling when done
window.addEventListener('beforeunload', () => {
  client.stop();
});
```

## Common Issues and Solutions

### Issue 1: 404 Not Found - `/communication/chats/`
**Problem:** Missing `/api/v1/` prefix

**Solution:**
```javascript
// ❌ Wrong
fetch('http://localhost:8000/communication/chats/')

// ✅ Correct
fetch('http://localhost:8000/api/v1/communication/chats/')
```

### Issue 2: 404 Not Found - `/api/v1/communication/sse/events/`
**Problem:** Using old SSE endpoint

**Solution:**
```javascript
// ❌ Wrong (old SSE)
const eventSource = new EventSource('/api/v1/communication/sse/events/')

// ✅ Correct (new long polling)
const response = await fetch('/api/v1/communication/poll/events/?token=XXX')
```

### Issue 3: 401 Unauthorized
**Problem:** Missing or invalid token

**Solution:**
```javascript
// Option 1: Query parameter
fetch('/api/v1/communication/poll/events/?token=YOUR_TOKEN')

// Option 2: Header (preferred)
fetch('/api/v1/communication/chats/', {
  headers: {
    'Authorization': `Token ${YOUR_TOKEN}`
  }
})
```

### Issue 4: CORS Errors
**Problem:** Frontend running on different port/domain

**Solution:** Backend already configured for CORS. Make sure you're using correct origin.

## Testing

### Test Long Polling
```bash
# Should return OK
curl http://localhost:8000/api/v1/communication/poll/test/
```

### Test Chat Endpoint
```bash
# Get conversations
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/v1/communication/chats/conversations/
```

### Test RabbitMQ Connection
```bash
# Django management command
python manage.py check_rabbitmq
```

## Support

For issues or questions:
- Check this guide for correct endpoint URLs
- Verify `/api/v1/` prefix is included
- Check authentication token is valid
- Review browser console for detailed errors
- See `LONG_POLLING_GUIDE.md` for implementation details
