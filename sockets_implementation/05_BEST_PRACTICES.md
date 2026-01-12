# Best Practices & Optimization Guide

Best practices for implementing and optimizing WebSocket + Redis real-time communication.

## Performance Optimization

### 1. Message Batching

Batch read receipts to reduce server load:

```javascript
class MessageBatcher {
  constructor(sendFn, delay = 1000) {
    this.sendFn = sendFn;
    this.delay = delay;
    this.queue = new Set();
    this.timer = null;
  }

  add(messageId) {
    this.queue.add(messageId);
    this.scheduleFlush();
  }

  scheduleFlush() {
    clearTimeout(this.timer);
    this.timer = setTimeout(() => this.flush(), this.delay);
  }

  flush() {
    if (this.queue.size > 0) {
      this.sendFn(Array.from(this.queue));
      this.queue.clear();
    }
  }
}

// Usage
const readReceiptBatcher = new MessageBatcher((messageIds) => {
  ws.send(JSON.stringify({
    type: 'read_receipt',
    message_ids: messageIds
  }));
});
```

### 2. Typing Indicator Debounce

Prevent excessive typing indicator updates:

```javascript
let typingTimer;
let isTyping = false;
const TYPING_TIMEOUT = 500;

function handleInput() {
  clearTimeout(typingTimer);

  if (!isTyping) {
    sendTyping(true);
    isTyping = true;
  }

  typingTimer = setTimeout(() => {
    sendTyping(false);
    isTyping = false;
  }, TYPING_TIMEOUT);
}
```

### 3. Lazy Loading Messages

Load messages on demand for better performance:

```javascript
const [messages, setMessages] = useState([]);
const [hasMore, setHasMore] = useState(true);
const [isLoading, setIsLoading] = useState(false);

const loadMoreMessages = async () => {
  if (isLoading || !hasMore) return;

  setIsLoading(true);

  const oldestMessageId = messages[0]?.id;
  const response = await fetch(
    `/api/v1/communication/chats/conversation/${userId}/?before_id=${oldestMessageId}&limit=20`,
    { headers: { Authorization: `Token ${token}` } }
  );

  const data = await response.json();
  setMessages((prev) => [...data.messages.reverse(), ...prev]);
  setHasMore(data.has_more);
  setIsLoading(false);
};

// Use with IntersectionObserver for infinite scroll
```

### 4. Connection Pooling

Reuse WebSocket connections:

```javascript
class WebSocketPool {
  constructor() {
    this.connections = new Map();
  }

  getConnection(url, token) {
    const key = `${url}:${token}`;

    if (this.connections.has(key)) {
      const ws = this.connections.get(key);
      if (ws.readyState === WebSocket.OPEN) {
        return ws;
      }
    }

    const ws = new WebSocket(`${url}?token=${token}`);
    this.connections.set(key, ws);
    return ws;
  }

  closeAll() {
    this.connections.forEach(ws => ws.close());
    this.connections.clear();
  }
}
```

---

## Security Best Practices

### 1. Token Management

**DO:**
- Store tokens in httpOnly cookies (backend sets)
- Use secure WebSocket (wss://) in production
- Implement token refresh mechanism
- Validate token on server for every message

**DON'T:**
- Store tokens in localStorage (XSS vulnerability)
- Send tokens in WebSocket message payloads
- Use hardcoded tokens

```javascript
// GOOD: Token in query param (over HTTPS)
const ws = new WebSocket(`wss://domain.com/ws/chat/?token=${token}`);

// BAD: Token in localStorage
localStorage.setItem('token', token); // Vulnerable to XSS
```

### 2. Input Sanitization

Sanitize user input before sending:

```javascript
import DOMPurify from 'dompurify';

function sendMessage(message) {
  // Sanitize HTML
  const clean = DOMPurify.sanitize(message);

  // Limit length
  if (clean.length > 5000) {
    alert('Message too long');
    return;
  }

  ws.send(JSON.stringify({
    type: 'message',
    receiver_id: receiverId,
    message: clean
  }));
}
```

### 3. Rate Limiting

Implement client-side rate limiting:

```javascript
class RateLimiter {
  constructor(maxRequests, timeWindow) {
    this.maxRequests = maxRequests;
    this.timeWindow = timeWindow;
    this.requests = [];
  }

  canMakeRequest() {
    const now = Date.now();
    this.requests = this.requests.filter(
      time => now - time < this.timeWindow
    );

    if (this.requests.length < this.maxRequests) {
      this.requests.push(now);
      return true;
    }

    return false;
  }
}

// 60 requests per minute
const rateLimiter = new RateLimiter(60, 60000);

function sendMessage(msg) {
  if (!rateLimiter.canMakeRequest()) {
    alert('Too many messages. Please slow down.');
    return;
  }

  ws.send(JSON.stringify(msg));
}
```

---

## Scalability

### 1. Horizontal Scaling

Redis enables horizontal scaling:

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Server 1 │────▶│  Redis   │◀────│ Server 2 │
└──────────┘     │  Pub/Sub │     └──────────┘
                 └──────────┘
```

**Configuration:**
```python
# settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [("redis-cluster.example.com", 6379)],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}
```

### 2. Load Balancing

Use sticky sessions for WebSocket:

```nginx
# nginx.conf
upstream websocket_backend {
    ip_hash;  # Sticky sessions
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;
    server 10.0.0.3:8000;
}

server {
    location /ws/ {
        proxy_pass http://websocket_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

### 3. Database Optimization

**Indexes:**
```python
# Ensure these indexes exist
class ChatMessage(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['conversation', '-timestamp']),
            models.Index(fields=['receiver', 'is_read']),
        ]
```

**Query Optimization:**
```python
# Use select_related for foreign keys
messages = ChatMessage.objects.select_related(
    'sender', 'receiver', 'conversation'
).filter(conversation_id=conv_id)[:50]

# Use prefetch_related for reverse foreign keys
conversations = Conversation.objects.prefetch_related(
    'messages__sender', 'messages__receiver'
).filter(user1=user)
```

---

## Error Handling

### 1. Graceful Degradation

Fall back to polling if WebSocket fails:

```javascript
class ChatService {
  constructor(token) {
    this.token = token;
    this.useWebSocket = true;
    this.pollingInterval = null;
  }

  async connect() {
    try {
      this.ws = new WebSocket(`wss://domain.com/ws/chat/?token=${this.token}`);

      this.ws.onerror = () => {
        console.warn('WebSocket failed, falling back to polling');
        this.useWebSocket = false;
        this.startPolling();
      };
    } catch (error) {
      this.useWebSocket = false;
      this.startPolling();
    }
  }

  startPolling() {
    this.pollingInterval = setInterval(() => {
      this.fetchNewMessages();
    }, 5000); // Poll every 5 seconds
  }

  async fetchNewMessages() {
    const response = await fetch('/api/v1/communication/chats/conversation/123/', {
      headers: { Authorization: `Token ${this.token}` }
    });
    const data = await response.json();
    // Update UI
  }
}
```

### 2. Error Notifications

Show user-friendly error messages:

```javascript
function handleWebSocketError(error) {
  const errorMessages = {
    4001: 'Authentication failed. Please log in again.',
    4029: 'Too many connections. Please try again later.',
    1006: 'Connection lost. Attempting to reconnect...',
  };

  const message = errorMessages[error.code] || 'Connection error occurred.';

  showToast(message, 'error');
}
```

---

## Monitoring & Logging

### 1. Client-Side Monitoring

Track WebSocket metrics:

```javascript
class WebSocketMonitor {
  constructor() {
    this.metrics = {
      messagesReceived: 0,
      messagesSent: 0,
      errors: 0,
      reconnects: 0,
      avgLatency: 0,
    };
  }

  recordMessageReceived() {
    this.metrics.messagesReceived++;
  }

  recordMessageSent() {
    this.metrics.messagesSent++;
  }

  recordError() {
    this.metrics.errors++;
  }

  recordReconnect() {
    this.metrics.reconnects++;
  }

  getMetrics() {
    return this.metrics;
  }
}
```

### 2. Server-Side Monitoring

Monitor Redis and WebSocket health:

```python
# management/commands/check_websocket_health.py
from django.core.management.base import BaseCommand
from apps.communication.redis_utils import get_redis_client, get_online_count_ws

class Command(BaseCommand):
    help = 'Check WebSocket health metrics'

    def handle(self, *args, **options):
        redis = get_redis_client()

        if not redis:
            self.stdout.write(self.style.ERROR('Redis not available'))
            return

        # Check online users
        online_count = get_online_count_ws()
        self.stdout.write(f'Online users: {online_count}')

        # Check memory usage
        info = redis.info('memory')
        used_memory = info['used_memory_human']
        self.stdout.write(f'Redis memory: {used_memory}')
```

---

## Testing

### 1. Unit Tests

Test WebSocket consumers:

```python
# tests/test_consumers.py
from channels.testing import WebsocketCommunicator
from django.test import TestCase
from apps.communication.consumers import ChatConsumer

class ChatConsumerTestCase(TestCase):
    async def test_chat_message(self):
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/ws/chat/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send message
        await communicator.send_json_to({
            'type': 'message',
            'receiver_id': 2,
            'message': 'Test message'
        })

        # Receive response
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'message_sent')

        await communicator.disconnect()
```

### 2. Load Testing

Use tools like `websocket-bench`:

```bash
# Install
npm install -g websocket-bench

# Test
websocket-bench ws://localhost:8000/ws/chat/?token=TOKEN \
  -c 100 \  # 100 concurrent connections
  -d 60     # 60 seconds
```

---

## Production Checklist

- [ ] Use wss:// (secure WebSocket)
- [ ] Enable Redis persistence
- [ ] Set up Redis replication
- [ ] Configure load balancer with sticky sessions
- [ ] Enable compression (gzip)
- [ ] Set proper CORS headers
- [ ] Implement rate limiting
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure log aggregation (ELK stack)
- [ ] Set up alerting (PagerDuty, Slack)
- [ ] Test failover scenarios
- [ ] Document disaster recovery plan
- [ ] Set up automated backups
- [ ] Enable SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up CDN for static assets
- [ ] Enable health checks
- [ ] Configure auto-scaling

---

## Common Pitfalls

### 1. Memory Leaks

**Problem:** Not cleaning up WebSocket listeners

**Solution:**
```javascript
useEffect(() => {
  const ws = new WebSocket(url);

  ws.onmessage = handleMessage;

  // IMPORTANT: Clean up on unmount
  return () => {
    ws.close();
  };
}, [url]);
```

### 2. Stale Closures

**Problem:** Using stale state in WebSocket callbacks

**Solution:**
```javascript
// Use refs for latest state
const latestState = useRef(state);

useEffect(() => {
  latestState.current = state;
}, [state]);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Use latestState.current instead of state
  console.log(latestState.current);
};
```

### 3. Connection Storms

**Problem:** All clients reconnecting simultaneously

**Solution:**
```javascript
// Add random jitter to reconnection
const delay = BASE_DELAY * Math.pow(2, attempts) + Math.random() * 1000;
```

---

**Last Updated:** January 12, 2026
