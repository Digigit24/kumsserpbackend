# REST API Documentation

Complete REST API reference for chat and notifications.

## Base URL

```
http://your-domain.com/api/v1/communication/
```

## Authentication

All endpoints require token authentication.

**Header:**
```
Authorization: Token YOUR_AUTH_TOKEN
```

---

## Chat Endpoints

### 1. Send Message

**POST** `/chats/`

Send a new chat message.

**Request:**
```json
{
  "receiver_id": 456,
  "message": "Hello! 👋",
  "attachment": null  // Optional file upload
}
```

**Response (201):**
```json
{
  "id": 789,
  "sender": 123,
  "sender_name": "John Doe",
  "receiver": 456,
  "receiver_name": "Jane Smith",
  "conversation": 12,
  "message": "Hello! 👋",
  "attachment": null,
  "is_read": false,
  "timestamp": "2026-01-12T10:30:00Z",
  "delivered_at": "2026-01-12T10:30:00Z"
}
```

---

### 2. Get Conversations

**GET** `/chats/conversations/`

Get list of all conversations.

**Response (200):**
```json
[
  {
    "conversation_id": 12,
    "other_user": {
      "id": 456,
      "username": "jane",
      "full_name": "Jane Smith",
      "avatar": "https://example.com/avatar.jpg",
      "is_online": true
    },
    "last_message": "Hello! 👋",
    "last_message_at": "2026-01-12T10:30:00Z",
    "last_message_by_me": true,
    "unread_count": 0,
    "updated_at": "2026-01-12T10:30:00Z"
  }
]
```

---

### 3. Get Conversation Messages

**GET** `/chats/conversation/{user_id}/`

Get messages with a specific user.

**Query Parameters:**
- `limit` (default: 50): Number of messages
- `offset` (default: 0): Pagination offset
- `before_id`: Get messages before this ID

**Response (200):**
```json
{
  "conversation_id": 12,
  "messages": [...],
  "other_user": {...},
  "has_more": true
}
```

---

### 4. Mark Messages as Read

**POST** `/chats/mark-read/`

Mark messages as read.

**Request (Option 1 - By conversation):**
```json
{
  "conversation_id": 12
}
```

**Request (Option 2 - By message IDs):**
```json
{
  "message_ids": [789, 790, 791]
}
```

**Request (Option 3 - By sender):**
```json
{
  "sender_id": 456
}
```

**Response (200):**
```json
{
  "success": true,
  "marked_count": 3,
  "read_at": "2026-01-12T10:31:00Z"
}
```

---

### 5. Send Typing Indicator

**POST** `/chats/typing/`

Send typing indicator.

**Request:**
```json
{
  "receiver_id": 456,
  "is_typing": true
}
```

**Response (200):**
```json
{
  "success": true
}
```

---

### 6. Get Unread Count

**GET** `/chats/unread-count/`

Get total unread message count.

**Response (200):**
```json
{
  "total_unread": 5,
  "conversations": [
    {
      "conversation_id": 12,
      "unread_count": 3,
      "other_user_id": 456,
      "other_user_name": "Jane Smith"
    }
  ]
}
```

---

### 7. Get Online Users

**GET** `/chats/online-users/`

Get list of currently online users.

**Response (200):**
```json
{
  "online_users": [123, 456, 789]
}
```

---

## Notification Endpoints

### 1. Get Notifications

**GET** `/notifications/`

Get all notifications for current user.

**Query Parameters:**
- `notification_type`: Filter by type
- `is_read`: Filter by read status (true/false)
- `priority`: Filter by priority (low, normal, high, urgent)
- `page`: Page number
- `page_size`: Items per page (default: 20)

**Response (200):**
```json
{
  "count": 42,
  "next": "http://...?page=2",
  "previous": null,
  "results": [
    {
      "id": 789,
      "notification_type": "message",
      "title": "New Message",
      "message": "John Doe sent you a message",
      "link": "/chat/123",
      "icon": "message",
      "priority": "normal",
      "is_read": false,
      "read_at": null,
      "created_at": "2026-01-12T10:30:00Z",
      "time_ago": "5 minutes"
    }
  ]
}
```

---

### 2. Get Unread Notifications

**GET** `/notifications/unread/`

Get only unread notifications.

**Response (200):**
```json
{
  "count": 5,
  "notifications": [...]
}
```

---

### 3. Get Unread Count

**GET** `/notifications/unread-count/`

Get count of unread notifications.

**Response (200):**
```json
{
  "count": 5
}
```

---

### 4. Mark Notification as Read

**POST** `/notifications/{id}/mark-read/`

Mark specific notification as read.

**Response (200):**
```json
{
  "success": true,
  "notification_id": 789,
  "read_at": "2026-01-12T10:31:00Z"
}
```

---

### 5. Mark All Notifications as Read

**POST** `/notifications/mark-all-read/`

Mark all notifications as read.

**Response (200):**
```json
{
  "success": true,
  "count": 5
}
```

---

### 6. Dismiss Notification

**DELETE** `/notifications/{id}/dismiss/`

Dismiss (soft delete) a notification.

**Response (200):**
```json
{
  "success": true,
  "notification_id": 789
}
```

---

### 7. Dismiss All Notifications

**DELETE** `/notifications/dismiss-all/`

Dismiss all notifications.

**Response (200):**
```json
{
  "success": true,
  "count": 42
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "error": "receiver_id is required"
}
```

### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found

```json
{
  "error": "User not found"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error"
}
```

---

## Rate Limiting

- **Chat messages:** 60 per minute
- **Typing indicators:** 30 per minute
- **API requests:** 100 per minute

Exceeded limits return HTTP 429 (Too Many Requests).

---

## Examples

### cURL Examples

```bash
# Get conversations
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/v1/communication/chats/conversations/

# Send message
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"receiver_id":456,"message":"Hello 👋"}' \
  http://localhost:8000/api/v1/communication/chats/

# Get unread notifications
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/v1/communication/notifications/unread/

# Mark all notifications as read
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/v1/communication/notifications/mark-all-read/
```

### JavaScript Examples

```javascript
// Send message
const sendMessage = async (receiverId, message) => {
  const response = await fetch('/api/v1/communication/chats/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${authToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      receiver_id: receiverId,
      message: message
    })
  });

  return await response.json();
};

// Get conversations
const getConversations = async () => {
  const response = await fetch('/api/v1/communication/chats/conversations/', {
    headers: {
      'Authorization': `Token ${authToken}`
    }
  });

  return await response.json();
};

// Mark notification as read
const markNotificationRead = async (notificationId) => {
  const response = await fetch(
    `/api/v1/communication/notifications/${notificationId}/mark-read/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Token ${authToken}`
      }
    }
  );

  return await response.json();
};
```

---

**Last Updated:** January 12, 2026
