# WebSocket API Specification

## Connection URLs

### Chat WebSocket
```
ws://YOUR_DOMAIN/ws/chat/?token=YOUR_AUTH_TOKEN
```

### Notifications WebSocket
```
ws://YOUR_DOMAIN/ws/notifications/?token=YOUR_AUTH_TOKEN
```

**Production:** Use `wss://` instead of `ws://`

---

## Authentication

**Method:** Token in query string
**Format:** `?token=YOUR_AUTH_TOKEN`

**Example:**
```javascript
const token = "abc123xyz789"; // From login response
const ws = new WebSocket(`ws://localhost:8000/ws/chat/?token=${token}`);
```

---

## 1. CHAT WEBSOCKET

### Connection Events

#### On Connect (Automatic)
User joins their personal room: `user_{user_id}`

#### On Disconnect (Automatic)
User leaves their room

---

### Request Payloads (Send)

#### Send Chat Message
```json
{
  "receiver_id": 123,
  "message": "Hello, how are you?",
  "attachment": "https://bucket.s3.amazonaws.com/file.pdf"
}
```

**Fields:**
- `receiver_id` (integer, required): ID of message recipient
- `message` (string, optional): Text message content
- `attachment` (string, optional): URL of file attachment
- **Note:** Either `message` or `attachment` must be provided

---

### Response Payloads (Receive)

#### 1. Message Sent Confirmation
```json
{
  "type": "message_sent",
  "id": 456,
  "status": "delivered"
}
```

**Trigger:** After successfully sending a message
**Use:** Update UI with message ID, show delivered status

---

#### 2. Incoming Chat Message
```json
{
  "type": "chat_message",
  "id": 789,
  "sender_id": 101,
  "sender_name": "John Doe",
  "message": "Hello, how are you?",
  "attachment": "https://bucket.s3.amazonaws.com/file.pdf",
  "timestamp": "2026-01-06T10:30:45.123456Z"
}
```

**Trigger:** When another user sends you a message
**Use:** Display in chat UI

**Fields:**
- `type`: Always `"chat_message"`
- `id`: Unique message ID
- `sender_id`: ID of sender
- `sender_name`: Full name of sender
- `message`: Text content (may be empty if attachment-only)
- `attachment`: File URL (null if no attachment)
- `timestamp`: ISO 8601 format

---

#### 3. Error Response
```json
{
  "type": "error",
  "error": "receiver_id is required"
}
```

**Triggers:**
- Missing `receiver_id`
- Both `message` and `attachment` are empty
- Invalid JSON format
- Receiver not found
- Server error

**Error Messages:**
- `"receiver_id is required"`
- `"message or attachment is required"`
- `"Invalid JSON format"`
- `"Failed to send message. Receiver not found."`
- `"An error occurred while processing your message"`

---

## 2. NOTIFICATIONS WEBSOCKET

### Connection Events

#### On Connect (Automatic)
User joins two rooms:
1. Personal: `notifications_{user_id}`
2. College-wide: `college_notifications_{college_id}` (if user has college)

#### On Disconnect (Automatic)
User leaves both rooms

---

### Request Payloads (Send)

**None** - Notifications are receive-only (server → client)

---

### Response Payloads (Receive)

#### Notification Event
```json
{
  "type": "notify",
  "title": "New Notice Published",
  "message": "Mid-term exam schedule has been released",
  "notification_type": "notice",
  "timestamp": "2026-01-06T14:20:00Z",
  "data": {
    "notice_id": 42,
    "url": "/notices/42"
  }
}
```

**Triggers:**
- New notice published (via Django signals)
- Bulk message sent
- Custom notification from backend

**Fields:**
- `type`: Always `"notify"`
- `title`: Notification heading
- `message`: Notification body
- `notification_type`: Type identifier (`"notice"`, `"alert"`, `"message"`, etc.)
- `timestamp`: ISO 8601 format
- `data`: Additional metadata (optional, varies by notification type)

---

## Backend Triggers

### Chat Messages
**Manual:** User sends message via WebSocket

### Notifications

#### 1. Notice Post-Save Signal
**File:** `apps/communication/signals.py`
**Trigger:** When `Notice.is_published = True`
**Action:** Broadcasts to `college_notifications_{college_id}`

```python
# Backend automatically sends
{
  "type": "notify",
  "title": "New Notice",
  "message": notice.title,
  "notification_type": "notice"
}
```

#### 2. Bulk Message Signal
**Trigger:** When `BulkMessage` is created
**Action:** Queues Celery task for async processing

#### 3. Manual Notifications (Backend Utility Functions)

**Send to specific user:**
```python
# Backend code
from apps.communication.utils import send_notification
send_notification(user_id=123, title="Alert", message="Your request approved")
```

**Broadcast to college:**
```python
from apps.communication.utils import broadcast_college_notification
broadcast_college_notification(college_id=5, title="Urgent", message="Classes suspended")
```

---

## Connection States

### JavaScript Example
```javascript
const ws = new WebSocket(url);

ws.onopen = () => {
  console.log('Connected');
  // Show "Online" indicator
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle based on data.type
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
  // Show error to user
};

ws.onclose = () => {
  console.log('Disconnected');
  // Show "Offline" indicator, attempt reconnect
};
```

---

## HTTP Headers

**Not applicable** - WebSocket uses query string authentication, not HTTP headers for auth.

**Standard WebSocket Headers (Automatic):**
```
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: [auto-generated]
Sec-WebSocket-Version: 13
```

---

## CORS & Security

**Backend Configuration:**
- `AllowedHostsOriginValidator` enabled
- Only requests from `ALLOWED_HOSTS` accepted
- Token authentication required
- Anonymous connections rejected

**Frontend Requirements:**
- Include valid auth token in URL
- Use secure WebSocket (`wss://`) in production
- Handle token expiration (close & reconnect)

---

## Error Handling Checklist

- [ ] Invalid/expired token → Connection rejected
- [ ] Network error → Auto-reconnect with exponential backoff
- [ ] JSON parse error → Log and ignore message
- [ ] Receiver not found → Show error to user
- [ ] Empty message → Validate before sending

---

## Testing

### Chat Test
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/?token=YOUR_TOKEN');

ws.onopen = () => {
  ws.send(JSON.stringify({
    receiver_id: 2,
    message: "Test message"
  }));
};

ws.onmessage = (e) => console.log('Received:', JSON.parse(e.data));
```

### Notification Test
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/notifications/?token=YOUR_TOKEN');
ws.onmessage = (e) => console.log('Notification:', JSON.parse(e.data));
```

---

## Quick Reference Table

| Event | Direction | Payload Type | Required Fields |
|-------|-----------|--------------|-----------------|
| Send Message | Client → Server | `{receiver_id, message?, attachment?}` | `receiver_id` + (`message` OR `attachment`) |
| Message Sent | Server → Client | `{type: "message_sent", id, status}` | All |
| Receive Message | Server → Client | `{type: "chat_message", ...}` | All |
| Error | Server → Client | `{type: "error", error}` | All |
| Notification | Server → Client | `{type: "notify", title, message}` | `type`, `title`, `message` |

---

## Environment Variables

```env
# .env file
REACT_APP_WS_URL=ws://localhost:8000  # Development
# REACT_APP_WS_URL=wss://api.yourdomain.com  # Production
```

---

## Deployment Notes

**Development:**
- Django: `python manage.py runserver`
- Redis: `redis-server`
- WebSocket: `ws://localhost:8000`

**Production:**
- Use Daphne ASGI server (not Gunicorn)
- Redis must be running
- Use `wss://` protocol
- Configure nginx for WebSocket proxying:
  ```nginx
  location /ws/ {
      proxy_pass http://backend;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
  }
  ```
