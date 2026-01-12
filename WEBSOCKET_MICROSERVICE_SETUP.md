# WebSocket Microservice Setup Guide

This guide explains how to set up and run the new Node.js WebSocket microservice for real-time chat and notifications.

## What Changed?

The Django SSE (Server-Sent Events) + Redis Pub/Sub implementation has been replaced with a dedicated Node.js microservice using Socket.io for better real-time performance and scalability.

### Old Architecture (Commented Out)
- `apps/communication/sse_views.py` - SSE endpoints (now commented out)
- `apps/communication/redis_pubsub.py` - Redis pub/sub (stub functions only)
- SSE endpoints: `/api/v1/communication/sse/events/`

### New Architecture (Active)
- `websocket-service/` - Node.js Socket.io microservice
- Django integration: `apps/communication/websocket_integration.py`
- New endpoints: `/api/v1/communication/ws/notify/`, `/ws/broadcast/`, `/ws/online-users/`

## Quick Start

### Option 1: Docker (Recommended)

1. Navigate to the websocket-service directory:
```bash
cd websocket-service
```

2. Copy and configure environment file:
```bash
cp .env.example .env
```

3. Edit `.env` with your database credentials:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=kumss_erp
DB_USER=postgres
DB_PASSWORD=your_password
REDIS_URL=redis://localhost:6379
```

4. Start the service:
```bash
docker-compose up -d
```

5. Check if it's running:
```bash
curl http://localhost:3001/health
```

### Option 2: Manual Setup

1. Install Node.js 18+ and npm:
```bash
# Check versions
node --version  # Should be >= 18
npm --version   # Should be >= 9
```

2. Navigate to websocket-service and install dependencies:
```bash
cd websocket-service
npm install
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Ensure PostgreSQL and Redis are running:
```bash
# Check PostgreSQL
psql -U postgres -d kumss_erp -c "SELECT 1"

# Check Redis
redis-cli ping  # Should return PONG
```

5. Start the service:
```bash
# Development mode (with auto-reload)
npm run dev

# Production mode
npm start
```

## Integration with Django

### 1. Update Django Environment

Add to your Django `.env` file:
```env
WEBSOCKET_SERVICE_URL=http://localhost:3001
```

### 2. Use in Django Code

#### Send Notification to User
```python
from apps.communication.websocket_integration import send_realtime_notification

# In your view or signal
send_realtime_notification(
    recipient_id=user.id,
    notification_type='approval_request',
    title='New Approval Request',
    message='You have a new approval request',
    metadata={'approval_id': str(approval.id)}
)
```

#### Broadcast to College
```python
from apps.communication.websocket_integration import broadcast_realtime_notification

# In your view or signal
broadcast_realtime_notification(
    college_id=college.id,
    notification_type='notice',
    title='New Notice Published',
    message='A new notice has been published',
    metadata={'notice_id': str(notice.id)}
)
```

#### Via HTTP API
```python
import requests

# Send notification
response = requests.post(
    'http://localhost:8000/api/v1/communication/ws/notify/',
    headers={'Authorization': f'Token {user_token}'},
    json={
        'recipient_id': str(user_id),
        'type': 'general',
        'title': 'Test Notification',
        'message': 'This is a test',
        'metadata': {}
    }
)
```

## Frontend Integration

### Install Socket.io Client

```bash
npm install socket.io-client
# or
yarn add socket.io-client
```

### Connect to WebSocket Service

```javascript
import { io } from 'socket.io-client';

// Get Django token from your auth system
const djangoToken = localStorage.getItem('auth_token');

// Connect to WebSocket service
const socket = io('http://localhost:3001', {
  auth: {
    token: djangoToken
  },
  transports: ['websocket', 'polling']
});

// Connection events
socket.on('connect', () => {
  console.log('Connected to WebSocket server');
});

socket.on('disconnect', () => {
  console.log('Disconnected from WebSocket server');
});

// Listen for chat messages
socket.on('chat:message', (data) => {
  console.log('New message:', data);
  // Update UI with new message
});

// Listen for notifications
socket.on('notification:new', (notification) => {
  console.log('New notification:', notification);
  // Show notification to user
});

// Listen for typing indicators
socket.on('chat:typing', (data) => {
  console.log(`${data.senderName} is typing...`);
});

// Listen for read receipts
socket.on('chat:readReceipt', (data) => {
  console.log('Message read:', data);
});

// Send a message
function sendMessage(receiverId, message) {
  socket.emit('chat:send', {
    receiverId: receiverId,
    message: message
  }, (response) => {
    if (response.success) {
      console.log('Message sent:', response.message);
    } else {
      console.error('Failed to send:', response.error);
    }
  });
}

// Send typing indicator
function sendTypingIndicator(receiverId, isTyping) {
  socket.emit('chat:typing', {
    receiverId: receiverId,
    isTyping: isTyping
  });
}

// Mark messages as read
function markMessagesAsRead(messageIds, conversationId) {
  socket.emit('chat:markRead', {
    messageIds: messageIds,
    conversationId: conversationId
  }, (response) => {
    if (response.success) {
      console.log(`Marked ${response.count} messages as read`);
    }
  });
}

// Heartbeat to keep connection alive
setInterval(() => {
  socket.emit('heartbeat');
}, 30000);

socket.on('heartbeat:ack', (data) => {
  console.log('Heartbeat acknowledged:', data.timestamp);
});
```

### React Hook Example

```javascript
import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';

export function useWebSocket(token) {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    if (!token) return;

    const newSocket = io('http://localhost:3001', {
      auth: { token },
      transports: ['websocket', 'polling']
    });

    newSocket.on('connect', () => {
      console.log('Connected');
      setIsConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected');
      setIsConnected(false);
    });

    newSocket.on('chat:message', (message) => {
      setMessages(prev => [...prev, message]);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, [token]);

  const sendMessage = (receiverId, message) => {
    if (socket) {
      socket.emit('chat:send', { receiverId, message }, (response) => {
        if (!response.success) {
          console.error('Failed to send message:', response.error);
        }
      });
    }
  };

  return { socket, isConnected, messages, sendMessage };
}
```

## Testing

### Test WebSocket Service Health

```bash
curl http://localhost:3001/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "websocket-service",
  "timestamp": "2024-01-12T10:30:00.000Z"
}
```

### Test Notification Sending

```bash
curl -X POST http://localhost:3001/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "recipientId": "user-uuid-here",
    "type": "general",
    "title": "Test Notification",
    "message": "This is a test notification",
    "metadata": {}
  }'
```

### Test via Django

```bash
# Using Django shell
python manage.py shell

from apps.communication.websocket_integration import send_realtime_notification
from apps.accounts.models import User

user = User.objects.first()
send_realtime_notification(
    recipient_id=user.id,
    notification_type='test',
    title='Test from Django',
    message='This is a test notification from Django',
    metadata={}
)
```

## Monitoring

### View Logs

**Docker:**
```bash
docker-compose logs -f websocket-service
```

**Manual:**
```bash
cd websocket-service
tail -f logs/combined.log
```

### Check Online Users

```bash
curl http://localhost:3001/api/online-users
```

### Monitor Redis

```bash
redis-cli

# Check online users
SMEMBERS online_users

# Check user sockets
SMEMBERS user_sockets:user-id-here

# Check online status
EXISTS online:user:user-id-here
```

## Production Deployment

### 1. Environment Configuration

Set production environment variables:
```env
NODE_ENV=production
PORT=3001
WEBSOCKET_SERVICE_URL=https://ws.yourdomain.com
DB_HOST=your-production-db-host
DB_PASSWORD=your-secure-password
REDIS_URL=redis://your-redis-host:6379
ALLOWED_ORIGINS=https://yourdomain.com
LOG_LEVEL=warn
```

### 2. Using Docker Compose

```bash
# Build and start in production mode
docker-compose -f docker-compose.yml up -d

# Scale to multiple instances
docker-compose up -d --scale websocket-service=3
```

### 3. Behind Nginx

```nginx
# /etc/nginx/sites-available/websocket

upstream websocket_backend {
    ip_hash;  # Sticky sessions
    server localhost:3001;
    server localhost:3002;
    server localhost:3003;
}

server {
    listen 443 ssl http2;
    server_name ws.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://websocket_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

### 4. Process Manager (PM2)

```bash
# Install PM2
npm install -g pm2

# Start service with PM2
cd websocket-service
pm2 start src/server.js --name websocket-service -i 4

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
```

## Troubleshooting

### Issue: Cannot connect to WebSocket service

**Solution:**
1. Check if service is running: `curl http://localhost:3001/health`
2. Check logs: `docker-compose logs websocket-service`
3. Verify firewall allows port 3001
4. Verify ALLOWED_ORIGINS includes your frontend URL

### Issue: Authentication failed

**Solution:**
1. Verify Django token is valid
2. Check token is being sent in `auth.token` parameter
3. Verify user is active in database
4. Check database connection in WebSocket service

### Issue: Messages not being received

**Solution:**
1. Check Redis is running: `redis-cli ping`
2. Verify database connection
3. Check user is connected: `GET /api/online-users`
4. Review WebSocket service logs

### Issue: High memory usage

**Solution:**
1. Increase Redis maxmemory limit
2. Scale to multiple instances
3. Implement message cleanup job
4. Check for memory leaks in logs

## Migration from SSE

If you were using the old SSE implementation:

1. **Old SSE endpoints are disabled** - They're commented out in `urls.py`
2. **Frontend code needs update** - Replace EventSource with Socket.io client
3. **Redis pub/sub calls are no-ops** - They return immediately without errors
4. **Database schema unchanged** - Same tables for messages and notifications

### Frontend Migration

**Old SSE code:**
```javascript
const eventSource = new EventSource('/api/v1/communication/sse/events/?token=' + token);
eventSource.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);
  // Handle message
});
```

**New Socket.io code:**
```javascript
const socket = io('http://localhost:3001', { auth: { token } });
socket.on('chat:message', (data) => {
  // Handle message
});
```

## Support

For issues, questions, or contributions:
- Check the main README: `websocket-service/README.md`
- Review logs: `websocket-service/logs/`
- Contact: KUMSS ERP development team

## References

- [Socket.io Documentation](https://socket.io/docs/)
- [Node.js PostgreSQL](https://node-postgres.com/)
- [Redis Node Client](https://redis.io/docs/clients/nodejs/)
- [Django REST Framework Tokens](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)
