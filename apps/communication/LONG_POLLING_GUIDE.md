# Long Polling with RabbitMQ Implementation Guide

## Overview

This application now uses **Long Polling with RabbitMQ** for real-time communication instead of WebSockets or Server-Sent Events (SSE). Long polling provides near real-time updates with better compatibility and simpler deployment. RabbitMQ provides reliable message queuing that works seamlessly on both Windows and Linux.

## How Long Polling Works

1. **Client makes a request** to the server
2. **Server holds the request** for 5-6 seconds, checking for new events
3. **If events arrive**, server responds immediately with the events
4. **If timeout is reached** (no events), server responds with empty array
5. **Client immediately makes a new request** to continue polling

This creates a near real-time connection without keeping persistent connections like WebSockets.

## RabbitMQ Setup

### Windows

1. **Download RabbitMQ:**
   - Download from: https://www.rabbitmq.com/install-windows.html
   - Install Erlang first (required dependency)
   - Install RabbitMQ Server

2. **Start RabbitMQ:**
   ```bash
   # Start as Windows service
   rabbitmq-server.bat

   # Or use the RabbitMQ Service - Start Windows Service
   ```

3. **Enable Management Plugin (Optional):**
   ```bash
   rabbitmq-plugins enable rabbitmq_management
   # Access UI at http://localhost:15672
   # Default login: guest/guest
   ```

### Linux

1. **Install RabbitMQ:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install rabbitmq-server

   # CentOS/RHEL
   sudo yum install rabbitmq-server
   ```

2. **Start RabbitMQ:**
   ```bash
   sudo systemctl start rabbitmq-server
   sudo systemctl enable rabbitmq-server  # Auto-start on boot
   ```

3. **Enable Management Plugin (Optional):**
   ```bash
   sudo rabbitmq-plugins enable rabbitmq_management
   # Access UI at http://localhost:15672
   ```

### Docker (Cross-platform)

```bash
# Run RabbitMQ with management plugin
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:management

# Access UI at http://localhost:15672
# Default login: guest/guest
```

### Test Connection

```bash
# Django management command
python manage.py check_rabbitmq
```

## API Endpoints

### 1. Long Poll Events
**Endpoint:** `GET /api/v1/communication/poll/events/`

**Authentication:** Token-based (query parameter or header)

**Parameters:**
- `token` (query param): User authentication token

**Response:**
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

**Event Types:**
- `message` - New chat message received
- `typing` - Someone is typing
- `read_receipt` - Message was read
- `notification` - System or college notification

**Example:**
```javascript
const response = await fetch(
  '/api/v1/communication/poll/events/?token=YOUR_TOKEN'
);
const data = await response.json();
console.log('Events:', data.events);
```

### 2. Test Endpoint
**Endpoint:** `GET /api/v1/communication/poll/test/`

**Purpose:** Test that long polling is working

**Response:**
```json
{
  "status": "ok",
  "message": "Long polling is working",
  "timestamp": 1704888600.123
}
```

### 3. Disconnect Endpoint
**Endpoint:** `POST /api/v1/communication/poll/disconnect/`

**Purpose:** Manually mark user as offline

**Response:**
```json
{
  "status": "disconnected",
  "user_id": 123
}
```

## Frontend Implementation

### Basic Implementation (JavaScript)

```javascript
class LongPollingClient {
  constructor(token) {
    this.token = token;
    this.baseUrl = '/api/v1/communication/poll';
    this.isPolling = false;
    this.eventHandlers = {};
  }

  // Register event handler
  on(eventType, handler) {
    if (!this.eventHandlers[eventType]) {
      this.eventHandlers[eventType] = [];
    }
    this.eventHandlers[eventType].push(handler);
  }

  // Emit event to handlers
  emit(eventType, data) {
    const handlers = this.eventHandlers[eventType] || [];
    handlers.forEach(handler => handler(data));
  }

  // Start long polling
  start() {
    this.isPolling = true;
    this.poll();
  }

  // Stop long polling
  stop() {
    this.isPolling = false;
  }

  // Long polling loop
  async poll() {
    while (this.isPolling) {
      try {
        const response = await fetch(
          `${this.baseUrl}/events/?token=${this.token}`,
          {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );

        if (!response.ok) {
          console.error('Polling error:', response.status);
          // Wait before retrying on error
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

        // Immediately continue polling
        // No delay needed as server already waited 5-6 seconds
      } catch (error) {
        console.error('Polling error:', error);
        // Wait before retrying on network error
        await this.sleep(2000);
      }
    }
  }

  // Helper to sleep
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Disconnect
  async disconnect() {
    this.stop();
    try {
      await fetch(`${this.baseUrl}/disconnect/?token=${this.token}`, {
        method: 'POST',
      });
    } catch (error) {
      console.error('Disconnect error:', error);
    }
  }
}

// Usage
const client = new LongPollingClient('YOUR_AUTH_TOKEN');

// Register event handlers
client.on('message', (data) => {
  console.log('New message:', data);
  // Update UI with new message
});

client.on('typing', (data) => {
  console.log('User is typing:', data.sender_name);
  // Show typing indicator
});

client.on('read_receipt', (data) => {
  console.log('Message read:', data.message_id);
  // Update message status
});

client.on('notification', (data) => {
  console.log('Notification:', data);
  // Show notification
});

// Start polling
client.start();

// Stop polling when user leaves or logs out
window.addEventListener('beforeunload', () => {
  client.disconnect();
});
```

### React Implementation

```javascript
import { useEffect, useRef, useCallback } from 'react';

function useLongPolling(token, onEvent) {
  const isPollingRef = useRef(false);
  const abortControllerRef = useRef(null);

  const poll = useCallback(async () => {
    while (isPollingRef.current) {
      // Create abort controller for this request
      abortControllerRef.current = new AbortController();

      try {
        const response = await fetch(
          `/api/v1/communication/poll/events/?token=${token}`,
          {
            signal: abortControllerRef.current.signal,
          }
        );

        if (!response.ok) {
          console.error('Polling error:', response.status);
          await new Promise(resolve => setTimeout(resolve, 2000));
          continue;
        }

        const data = await response.json();

        // Process events
        if (data.events && data.events.length > 0) {
          data.events.forEach(event => {
            onEvent(event.event, event.data);
          });
        }
      } catch (error) {
        if (error.name === 'AbortError') {
          // Request was aborted, stop polling
          break;
        }
        console.error('Polling error:', error);
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
  }, [token, onEvent]);

  useEffect(() => {
    // Start polling
    isPollingRef.current = true;
    poll();

    // Cleanup on unmount
    return () => {
      isPollingRef.current = false;
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [poll]);
}

// Usage in component
function ChatComponent() {
  const [messages, setMessages] = useState([]);
  const token = useAuthToken(); // Get your auth token

  const handleEvent = useCallback((eventType, data) => {
    switch (eventType) {
      case 'message':
        setMessages(prev => [...prev, data]);
        break;
      case 'typing':
        // Handle typing indicator
        break;
      case 'read_receipt':
        // Update message read status
        break;
      case 'notification':
        // Show notification
        break;
    }
  }, []);

  useLongPolling(token, handleEvent);

  return <div>{/* Your chat UI */}</div>;
}
```

## Event Types Reference

### Message Event
```json
{
  "event": "message",
  "data": {
    "id": 123,
    "sender_id": 456,
    "sender_name": "John Doe",
    "receiver_id": 789,
    "message": "Hello!",
    "attachment": "http://example.com/file.pdf",
    "attachment_type": "pdf",
    "timestamp": "2026-01-10T10:30:00Z",
    "is_read": false,
    "conversation_id": 101
  }
}
```

### Typing Event
```json
{
  "event": "typing",
  "data": {
    "sender_id": 456,
    "sender_name": "John Doe",
    "is_typing": true
  }
}
```

### Read Receipt Event
```json
{
  "event": "read_receipt",
  "data": {
    "message_id": 123,
    "reader_id": 789,
    "reader_name": "Jane Smith",
    "read_at": "2026-01-10T10:35:00Z"
  }
}
```

### Notification Event
```json
{
  "event": "notification",
  "data": {
    "title": "New Notice Published",
    "message": "Mid-term exam schedule released",
    "notification_type": "notice",
    "timestamp": "2026-01-10T10:30:00Z"
  }
}
```

## Technical Details

### Server Configuration

- **Timeout:** 5.5 seconds
- **Check Interval:** 0.3 seconds (server checks for events every 300ms)
- **Max Queue Size:** 100 events per user
- **Queue Expiration:** 30 minutes (1800 seconds)
- **Online Status TTL:** 5 minutes (300 seconds)

### RabbitMQ Queue Structure

- User events: `event_queue:user:{user_id}`
- College events: `event_queue:college:{college_id}`
- Online status: `online_status:user:{user_id}` (queue with TTL)

**Queue Properties:**
- Durable: Yes (survives broker restart)
- Auto-delete: No for event queues, Yes for online status
- Max length: 100 messages per queue
- Message TTL: 30 minutes (1,800,000 ms)
- Overflow behavior: Drop oldest messages

### Performance Considerations

1. **Immediate Response:** If events are in queue, server responds immediately (< 100ms)
2. **Timeout Response:** If no events, server responds after 5.5 seconds
3. **Network Efficiency:** Client only makes new request after receiving response
4. **Resource Usage:** Lower than WebSockets, no persistent connections
5. **Scalability:** Works well with load balancers and reverse proxies

### Comparison with SSE

| Feature | SSE (Old) | Long Polling (New) |
|---------|-----------|-------------------|
| Connection Type | Persistent | Request-Response |
| Server-to-Client | Yes | Yes |
| Client-to-Server | Separate requests | Separate requests |
| Proxy Compatibility | Good | Excellent |
| Load Balancer Support | Needs sticky sessions | No special config |
| Browser Support | Modern browsers | All browsers |
| Debugging | Harder | Standard HTTP tools |
| Resource Usage | Medium | Low-Medium |
| Latency | Very low (< 1s) | Low (< 6s worst case) |

## Best Practices

1. **Always disconnect on page unload**
   ```javascript
   window.addEventListener('beforeunload', () => {
     client.disconnect();
   });
   ```

2. **Handle errors gracefully**
   - Implement exponential backoff on errors
   - Show connection status to users
   - Retry failed requests

3. **Batch UI updates**
   - If multiple events arrive, batch update the UI
   - Use debouncing for typing indicators

4. **Monitor connection health**
   - Track last event timestamp
   - Show "reconnecting" status if no response for > 10s

5. **Use Authorization header in production**
   ```javascript
   fetch('/api/v1/communication/poll/events/', {
     headers: {
       'Authorization': `Token ${token}`
     }
   });
   ```

## Migration from SSE

If you're migrating from SSE, here are the key changes:

### Old SSE Code
```javascript
const eventSource = new EventSource(
  '/api/v1/communication/sse/events/?token=' + token
);

eventSource.addEventListener('message', (e) => {
  const data = JSON.parse(e.data);
  // Handle message
});
```

### New Long Polling Code
```javascript
const client = new LongPollingClient(token);
client.on('message', (data) => {
  // Handle message (data is already parsed)
});
client.start();
```

## Troubleshooting

### No events received
- Check RabbitMQ is running:
  - Windows: Check RabbitMQ service in Services
  - Linux: `sudo systemctl status rabbitmq-server`
  - Command: `python manage.py check_rabbitmq`
- Verify token is valid
- Check server logs for errors
- Test with `/api/v1/communication/poll/test/`
- Check RabbitMQ management UI at http://localhost:15672

### High latency
- Normal worst-case latency is 5-6 seconds (timeout)
- Check network connection
- Verify server isn't overloaded

### Events missed
- Check MAX_QUEUE_SIZE (default 100)
- Events older than 30 minutes expire
- User must be polling to receive events

### Memory issues
- Queues are limited to 100 events per user
- Queues expire after 30 minutes of inactivity
- Users marked offline after 5 minutes of no polling
- Monitor RabbitMQ memory usage in management UI

## Support

For issues or questions, please check:
- Server logs: `/var/log/django/`
- RabbitMQ logs:
  - Windows: `C:\Users\<user>\AppData\Roaming\RabbitMQ\log\`
  - Linux: `/var/log/rabbitmq/`
- RabbitMQ Management UI: http://localhost:15672
- Browser console for client-side errors
