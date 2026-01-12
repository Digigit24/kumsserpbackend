# WebSocket + Redis Real-Time Communication Implementation

## 📚 Overview

This directory contains comprehensive documentation for the WebSocket + Redis real-time communication system implemented in the KUMSS ERP backend.

The implementation provides:
- ✅ **Real-time Chat** with emoji support (UTF-8)
- ✅ **Online/Offline Status** tracking with Redis
- ✅ **Typing Indicators** with automatic timeout
- ✅ **Read/Unread Message** tracking
- ✅ **Delivery Receipts** for messages
- ✅ **In-App Notifications** with read/unread status
- ✅ **Low Latency** with Redis Pub/Sub
- ✅ **Scalable Architecture** for production
- ✅ **React Integration** examples and hooks

## 📁 Documentation Structure

```
sockets_implementation/
├── README.md                           # This file - overview
├── 01_WEBSOCKET_API.md                 # WebSocket API documentation
├── 02_REST_API.md                      # REST API documentation
├── 03_REQUEST_RESPONSE_EXAMPLES.md     # Request/response payloads
├── 04_REACT_INTEGRATION.md             # React integration guide
├── 05_BEST_PRACTICES.md                # Best practices and optimization
├── 06_DEPLOYMENT.md                    # Deployment guide
└── 07_TROUBLESHOOTING.md               # Common issues and solutions
```

## 🚀 Quick Start

### Backend Setup

1. **Ensure Redis is running:**
   ```bash
   redis-server
   # OR
   sudo systemctl start redis-server
   ```

2. **Run database migrations:**
   ```bash
   python manage.py migrate communication
   ```

3. **Start Django with Daphne (ASGI server):**
   ```bash
   daphne -b 0.0.0.0 -p 8000 kumss_erp.asgi:application
   ```

### Frontend Setup (React)

See [04_REACT_INTEGRATION.md](./04_REACT_INTEGRATION.md) for detailed React integration.

**Quick example:**
```javascript
// Connect to WebSocket
const ws = new WebSocket(`ws://localhost:8000/ws/chat/?token=${authToken}`);

// Send message
ws.send(JSON.stringify({
  type: 'message',
  receiver_id: 123,
  message: 'Hello! 👋'
}));
```

## 🔌 Endpoints

### WebSocket Endpoints

| Endpoint | Purpose | Auth |
|----------|---------|------|
| `ws://domain/ws/chat/` | Real-time chat | Token (query param) |
| `ws://domain/ws/notifications/` | Real-time notifications | Token (query param) |

### REST API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/communication/chats/` | POST | Send message |
| `/api/v1/communication/chats/conversations/` | GET | Get conversations |
| `/api/v1/communication/chats/conversation/{user_id}/` | GET | Get messages |
| `/api/v1/communication/chats/mark-read/` | POST | Mark messages read |
| `/api/v1/communication/chats/typing/` | POST | Send typing indicator |
| `/api/v1/communication/chats/unread-count/` | GET | Get unread count |
| `/api/v1/communication/chats/online-users/` | GET | Get online users |
| `/api/v1/communication/notifications/` | GET | Get notifications |
| `/api/v1/communication/notifications/unread/` | GET | Get unread notifications |
| `/api/v1/communication/notifications/{id}/mark-read/` | POST | Mark notification read |
| `/api/v1/communication/notifications/mark-all-read/` | POST | Mark all read |

## 🏗️ Architecture

```
┌─────────────┐                 ┌──────────────┐                ┌─────────────┐
│   React     │  WebSocket      │    Django    │    Redis       │   Redis     │
│  Frontend   │ ←──────────────→│   Channels   │←──────────────→│   Pub/Sub   │
│             │                 │   Consumer   │                │             │
└─────────────┘                 └──────────────┘                └─────────────┘
       │                               │                                │
       │                               ↓                                │
       │                        ┌──────────────┐                        │
       │     REST API           │  PostgreSQL  │                        │
       └───────────────────────→│   Database   │←───────────────────────┘
                                └──────────────┘
```

### Key Components

1. **Django Channels** - WebSocket support for Django
2. **Redis** - Message broker for Channels layer + presence tracking
3. **PostgreSQL** - Persistent storage for messages and notifications
4. **Daphne** - ASGI server for production

## ✨ Features

### Chat Features

- **Real-time messaging** with instant delivery
- **Emoji support** (full UTF-8 support)
- **File attachments** (images, videos, documents)
- **Typing indicators** with 5-second auto-timeout
- **Read receipts** (✓ sent, ✓✓ read)
- **Delivery status** tracking
- **Online/offline status** with Redis TTL
- **Message history** with pagination
- **Unread count** per conversation
- **Search and filter** messages

### Notification Features

- **In-app notifications** with categories
- **Priority levels** (low, normal, high, urgent)
- **Read/unread tracking**
- **Auto-mark as read** when viewing related content
- **Push to WebSocket** for instant updates
- **Notification icons** and custom styling
- **Dismiss notifications**
- **Bulk operations** (mark all read, dismiss all)

### Presence Features

- **Online/offline status** with Redis
- **Auto-offline** after connection timeout (5 minutes)
- **Multiple device support**
- **Connection tracking**
- **Heartbeat monitoring**

## 🔐 Authentication

All WebSocket and REST API endpoints require authentication via token.

**WebSocket:**
```javascript
ws://domain/ws/chat/?token=YOUR_AUTH_TOKEN
```

**REST API:**
```http
Authorization: Token YOUR_AUTH_TOKEN
```

## 📊 Performance

- **Low latency:** Sub-100ms message delivery
- **Scalability:** Horizontal scaling with Redis
- **Efficient:** Redis Pub/Sub for broadcasting
- **Optimized:** Database indexes for fast queries
- **Cached:** Online status cached in Redis

## 🔧 Configuration

### Django Settings

```python
# Channel Layers (WebSocket)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [REDIS_URL],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}

# Redis Cache
REDIS_URL = 'redis://127.0.0.1:6379'
```

### Environment Variables

```bash
REDIS_URL=redis://127.0.0.1:6379
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com
```

## 📈 Monitoring

### Redis Keys

Monitor these Redis keys for health:
- `ws:online_users` - Set of online user IDs
- `ws:online:{user_id}` - Individual user online status (TTL: 5 min)
- `ws:typing:{user_id}:{partner_id}` - Typing indicators (TTL: 5 sec)
- `ws:connections:{user_id}` - User's WebSocket connections
- `ws:pending:{user_id}` - Pending messages for offline users

### Database Tables

- `chat_message` - All chat messages
- `conversation` - Conversation metadata
- `typing_indicator` - Typing indicator records
- `in_app_notification` - In-app notifications

## 🧪 Testing

### Test WebSocket Connection

```bash
# Using websocat
websocat "ws://localhost:8000/ws/chat/?token=YOUR_TOKEN"

# Send test message
{"type":"message","receiver_id":2,"message":"Test"}
```

### Test REST API

```bash
# Get conversations
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/v1/communication/chats/conversations/

# Send message
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"receiver_id":2,"message":"Hello"}' \
  http://localhost:8000/api/v1/communication/chats/
```

## 📚 Further Reading

- [01_WEBSOCKET_API.md](./01_WEBSOCKET_API.md) - Complete WebSocket API reference
- [02_REST_API.md](./02_REST_API.md) - Complete REST API reference
- [03_REQUEST_RESPONSE_EXAMPLES.md](./03_REQUEST_RESPONSE_EXAMPLES.md) - All request/response examples
- [04_REACT_INTEGRATION.md](./04_REACT_INTEGRATION.md) - React integration with hooks
- [05_BEST_PRACTICES.md](./05_BEST_PRACTICES.md) - Best practices and optimization
- [06_DEPLOYMENT.md](./06_DEPLOYMENT.md) - Production deployment guide
- [07_TROUBLESHOOTING.md](./07_TROUBLESHOOTING.md) - Common issues and solutions

## 🤝 Support

For issues or questions:
1. Check [07_TROUBLESHOOTING.md](./07_TROUBLESHOOTING.md)
2. Review the documentation
3. Check Redis and database logs
4. Enable Django debug logging

## 📝 License

This implementation is part of the KUMSS ERP system.

---

**Last Updated:** January 12, 2026
**Version:** 1.0.0
