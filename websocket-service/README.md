# KUMSS ERP WebSocket Microservice

Real-time WebSocket microservice for KUMSS ERP using Socket.io. Handles chat and notifications with scalable architecture.

## Features

- **Real-time Chat**: Direct messaging between users with typing indicators and read receipts
- **Notifications**: User-specific and college-wide notification broadcasting
- **Online Status**: Track user online/offline status in real-time
- **Scalable Architecture**: Built with Socket.io and Redis for horizontal scaling
- **Authentication**: Integrates with Django REST Framework token authentication
- **PostgreSQL Integration**: Direct database access for message persistence

## Architecture

```
┌─────────────────┐
│  Django Backend │
│   (Port 8000)   │
└────────┬────────┘
         │
         │ HTTP API
         │
┌────────▼────────────────┐
│  WebSocket Microservice │
│      (Port 3001)        │
│                         │
│  ┌──────────────────┐  │
│  │   Socket.io      │  │
│  │   Server         │  │
│  └──────────────────┘  │
│                         │
│  ┌──────────────────┐  │
│  │   Chat Handler   │  │
│  └──────────────────┘  │
│                         │
│  ┌──────────────────┐  │
│  │ Notification     │  │
│  │ Handler          │  │
│  └──────────────────┘  │
└─────────┬───────────────┘
          │
    ┌─────┴─────┐
    │           │
┌───▼───┐   ┌───▼──────┐
│ Redis │   │PostgreSQL│
└───────┘   └──────────┘
```

## Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0
- PostgreSQL (shared with Django)
- Redis

## Installation

### 1. Install Dependencies

```bash
cd websocket-service
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Server Configuration
PORT=3001
NODE_ENV=development

# Django Backend URL
DJANGO_BACKEND_URL=http://localhost:8000

# PostgreSQL Database (same as Django)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=kumss_erp
DB_USER=postgres
DB_PASSWORD=your_password

# Redis Configuration
REDIS_URL=redis://localhost:6379

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Logging
LOG_LEVEL=info
```

### 3. Run the Service

**Development:**
```bash
npm run dev
```

**Production:**
```bash
npm start
```

## Docker Deployment

### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f websocket-service

# Stop services
docker-compose down
```

### Using Standalone Docker

```bash
# Build image
docker build -t kumss-websocket-service .

# Run container
docker run -d \
  --name websocket-service \
  -p 3001:3001 \
  --env-file .env \
  kumss-websocket-service
```

## API Endpoints

### Health Check
```
GET /health
```

### Send Notification
```
POST /api/notify
Content-Type: application/json

{
  "recipientId": "user-uuid",
  "type": "general",
  "title": "Notification Title",
  "message": "Notification message",
  "metadata": {}
}
```

### Broadcast Notification
```
POST /api/broadcast
Content-Type: application/json

{
  "collegeId": "college-uuid",
  "type": "general",
  "title": "Notification Title",
  "message": "Notification message",
  "metadata": {}
}
```

### Get Online Users
```
GET /api/online-users
```

## Socket.io Events

### Client → Server Events

#### Chat Events
- `chat:send` - Send a chat message
- `chat:typing` - Send typing indicator
- `chat:markRead` - Mark messages as read
- `chat:getMessages` - Fetch conversation messages
- `chat:getOnlineStatus` - Get online status of users

#### Notification Events
- `notification:send` - Send notification to user
- `notification:broadcast` - Broadcast to college
- `notification:getUnread` - Get unread notifications
- `notification:markRead` - Mark notifications as read
- `notification:getUnreadCount` - Get unread count

#### System Events
- `heartbeat` - Keep connection alive

### Server → Client Events

#### Chat Events
- `chat:message` - New message received
- `chat:typing` - Typing indicator
- `chat:readReceipt` - Message read receipt

#### Notification Events
- `notification:new` - New notification

#### System Events
- `user:online` - User came online
- `user:offline` - User went offline
- `heartbeat:ack` - Heartbeat acknowledgment

## Client Connection Example

### JavaScript/TypeScript

```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:3001', {
  auth: {
    token: 'your-django-token'
  }
});

// Connection events
socket.on('connect', () => {
  console.log('Connected to WebSocket server');
});

socket.on('disconnect', () => {
  console.log('Disconnected from WebSocket server');
});

// Chat events
socket.on('chat:message', (data) => {
  console.log('New message:', data);
});

// Send message
socket.emit('chat:send', {
  receiverId: 'recipient-uuid',
  message: 'Hello!',
}, (response) => {
  if (response.success) {
    console.log('Message sent:', response.message);
  }
});

// Notification events
socket.on('notification:new', (data) => {
  console.log('New notification:', data);
});

// Heartbeat
setInterval(() => {
  socket.emit('heartbeat');
}, 30000);
```

### Python (Django Integration)

```python
from apps.communication.websocket_integration import (
    send_realtime_notification,
    broadcast_realtime_notification
)

# Send notification to specific user
send_realtime_notification(
    recipient_id=user.id,
    notification_type='approval_request',
    title='New Approval Request',
    message='You have a new approval request',
    metadata={'approval_id': str(approval.id)}
)

# Broadcast to college
broadcast_realtime_notification(
    college_id=college.id,
    notification_type='notice',
    title='New Notice Published',
    message='A new notice has been published',
    metadata={'notice_id': str(notice.id)}
)
```

## Database Schema

The microservice uses the existing Django database schema:

- `authtoken_token` - Django REST Framework tokens
- `accounts_user` - User authentication
- `chat_message` - Chat messages
- `conversation` - Conversation metadata
- `typing_indicator` - Typing status
- `notification` - User notifications

## Redis Keys

- `online_users` - SET of online user IDs
- `user_sockets:{userId}` - SET of socket IDs for user
- `online:user:{userId}` - User online status with TTL

## Logging

Logs are stored in the `logs/` directory:

- `combined.log` - All logs
- `error.log` - Error logs only

Console logging is enabled in development mode.

## Scaling

The microservice is designed for horizontal scaling:

1. **Multiple Instances**: Run multiple instances behind a load balancer
2. **Redis Adapter**: Socket.io uses Redis for pub/sub across instances
3. **Sticky Sessions**: Configure load balancer for sticky sessions (optional)
4. **Database Connection Pool**: PostgreSQL connection pooling for efficiency

### Nginx Load Balancer Example

```nginx
upstream websocket_backend {
    ip_hash;  # Sticky sessions
    server localhost:3001;
    server localhost:3002;
    server localhost:3003;
}

server {
    listen 80;
    server_name ws.example.com;

    location / {
        proxy_pass http://websocket_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }
}
```

## Monitoring

### Health Check

```bash
curl http://localhost:3001/health
```

Response:
```json
{
  "status": "ok",
  "service": "websocket-service",
  "timestamp": "2024-01-12T10:30:00.000Z"
}
```

### Docker Health Check

The Dockerfile includes a health check that runs every 30 seconds.

## Troubleshooting

### Connection Issues

1. **Check Redis**: Ensure Redis is running and accessible
2. **Check Database**: Verify PostgreSQL connection
3. **Check Firewall**: Ensure port 3001 is open
4. **Check CORS**: Verify `ALLOWED_ORIGINS` includes your frontend URL

### Authentication Issues

1. **Verify Token**: Ensure Django token is valid
2. **Check User**: Verify user is active in database
3. **Check Logs**: Review logs for authentication errors

### Performance Issues

1. **Check Redis**: Monitor Redis memory usage
2. **Database Pool**: Increase connection pool size if needed
3. **Scaling**: Deploy multiple instances
4. **Logging**: Reduce log level in production

## Development

### Running Tests

```bash
npm test
```

### Linting

```bash
npm run lint
```

### Code Structure

```
src/
├── config/          # Configuration files
│   ├── database.js  # PostgreSQL config
│   └── redis.js     # Redis config
├── handlers/        # Socket.io event handlers
│   ├── chatHandler.js
│   └── notificationHandler.js
├── middleware/      # Express & Socket.io middleware
│   └── auth.js      # Authentication
├── services/        # Business logic
│   ├── chatService.js
│   ├── notificationService.js
│   └── onlineStatusService.js
├── utils/           # Utilities
│   └── logger.js    # Winston logger
└── server.js        # Main entry point
```

## License

MIT

## Support

For issues and questions, contact the KUMSS ERP development team.
