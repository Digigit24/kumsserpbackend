# WebSocket Integration Guide for React Frontend

## Overview
This document provides implementation details for integrating Django Channels WebSocket communication with your React frontend. The backend supports real-time chat and notifications.

---

## Backend Endpoints

### 1. **Chat WebSocket**
- **URL**: `ws://YOUR_BACKEND_URL/ws/chat/`
- **Purpose**: Real-time one-to-one messaging
- **Authentication**: Token required in query string

### 2. **Notifications WebSocket**
- **URL**: `ws://YOUR_BACKEND_URL/ws/notifications/`
- **Purpose**: System notifications and alerts
- **Authentication**: Token required in query string

---

## Authentication

All WebSocket connections require authentication via token in the URL:

```javascript
const token = localStorage.getItem('authToken'); // Your auth token
const wsUrl = `ws://localhost:8000/ws/chat/?token=${token}`;
const socket = new WebSocket(wsUrl);
```

**Note**: Use `wss://` for production (secure WebSocket)

---

## React Implementation

### Installation
```bash
npm install --save reconnecting-websocket
```

### Chat WebSocket Hook (`useChatWebSocket.js`)

```javascript
import { useEffect, useRef, useState, useCallback } from 'react';
import ReconnectingWebSocket from 'reconnecting-websocket';

export const useChatWebSocket = (token) => {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    if (!token) return;

    const wsUrl = `${process.env.REACT_APP_WS_URL}/ws/chat/?token=${token}`;
    const socket = new ReconnectingWebSocket(wsUrl);

    socket.addEventListener('open', () => {
      console.log('Chat WebSocket connected');
      setIsConnected(true);
    });

    socket.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);

      switch(data.type) {
        case 'chat_message':
          setMessages(prev => [...prev, {
            id: data.id,
            senderId: data.sender_id,
            senderName: data.sender_name,
            message: data.message,
            attachment: data.attachment,
            timestamp: data.timestamp
          }]);
          break;

        case 'message_sent':
          console.log('Message delivered:', data.id);
          break;

        case 'error':
          console.error('WebSocket error:', data.error);
          break;
      }
    });

    socket.addEventListener('close', () => {
      console.log('Chat WebSocket disconnected');
      setIsConnected(false);
    });

    socket.addEventListener('error', (error) => {
      console.error('WebSocket error:', error);
    });

    socketRef.current = socket;

    return () => {
      socket.close();
    };
  }, [token]);

  const sendMessage = useCallback((receiverId, message, attachment = null) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        receiver_id: receiverId,
        message: message,
        attachment: attachment
      }));
    }
  }, []);

  return { messages, isConnected, sendMessage };
};
```

### Notification WebSocket Hook (`useNotificationWebSocket.js`)

```javascript
import { useEffect, useRef, useState } from 'react';
import ReconnectingWebSocket from 'reconnecting-websocket';

export const useNotificationWebSocket = (token) => {
  const [notifications, setNotifications] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    if (!token) return;

    const wsUrl = `${process.env.REACT_APP_WS_URL}/ws/notifications/?token=${token}`;
    const socket = new ReconnectingWebSocket(wsUrl);

    socket.addEventListener('open', () => {
      console.log('Notification WebSocket connected');
      setIsConnected(true);
    });

    socket.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);

      setNotifications(prev => [...prev, {
        id: data.id || Date.now(),
        title: data.title,
        message: data.message,
        type: data.notification_type || 'info',
        timestamp: data.timestamp || new Date().toISOString()
      }]);
    });

    socket.addEventListener('close', () => {
      console.log('Notification WebSocket disconnected');
      setIsConnected(false);
    });

    socketRef.current = socket;

    return () => {
      socket.close();
    };
  }, [token]);

  return { notifications, isConnected };
};
```

---

## Usage Examples

### Chat Component

```javascript
import React, { useState } from 'react';
import { useChatWebSocket } from './hooks/useChatWebSocket';

function ChatComponent() {
  const token = localStorage.getItem('authToken');
  const { messages, isConnected, sendMessage } = useChatWebSocket(token);
  const [messageText, setMessageText] = useState('');
  const [receiverId, setReceiverId] = useState('');

  const handleSend = () => {
    if (messageText && receiverId) {
      sendMessage(receiverId, messageText);
      setMessageText('');
    }
  };

  return (
    <div>
      <div>Status: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}</div>

      <div className="messages">
        {messages.map(msg => (
          <div key={msg.id}>
            <strong>{msg.senderName}:</strong> {msg.message}
            {msg.attachment && <a href={msg.attachment}>📎 Attachment</a>}
            <small>{new Date(msg.timestamp).toLocaleString()}</small>
          </div>
        ))}
      </div>

      <input
        type="number"
        placeholder="Receiver ID"
        value={receiverId}
        onChange={(e) => setReceiverId(e.target.value)}
      />

      <input
        type="text"
        value={messageText}
        onChange={(e) => setMessageText(e.target.value)}
        placeholder="Type a message..."
      />

      <button onClick={handleSend} disabled={!isConnected}>
        Send
      </button>
    </div>
  );
}
```

### Notification Component

```javascript
import React from 'react';
import { useNotificationWebSocket } from './hooks/useNotificationWebSocket';

function NotificationComponent() {
  const token = localStorage.getItem('authToken');
  const { notifications, isConnected } = useNotificationWebSocket(token);

  return (
    <div>
      <div>Notifications: {isConnected ? '🟢' : '🔴'}</div>

      <div className="notifications">
        {notifications.map(notif => (
          <div key={notif.id} className={`notification ${notif.type}`}>
            <h4>{notif.title}</h4>
            <p>{notif.message}</p>
            <small>{new Date(notif.timestamp).toLocaleString()}</small>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Environment Configuration

Add to your `.env` file:

```env
# Development
REACT_APP_WS_URL=ws://localhost:8000

# Production
REACT_APP_WS_URL=wss://your-domain.com
```

---

## Message Formats

### Sending Chat Message
```json
{
  "receiver_id": 123,
  "message": "Hello!",
  "attachment": "https://example.com/file.pdf"
}
```

### Receiving Chat Message
```json
{
  "type": "chat_message",
  "id": 456,
  "sender_id": 789,
  "sender_name": "John Doe",
  "message": "Hello!",
  "attachment": "https://example.com/file.pdf",
  "timestamp": "2026-01-06T10:30:00Z"
}
```

### Receiving Notification
```json
{
  "type": "notify",
  "title": "New Notice",
  "message": "Exam schedule released",
  "notification_type": "notice",
  "timestamp": "2026-01-06T10:30:00Z"
}
```

### Error Response
```json
{
  "type": "error",
  "error": "receiver_id is required"
}
```

---

## Error Handling

```javascript
socket.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'error') {
    // Show error to user
    alert(data.error);
  }
});
```

---

## Best Practices

1. **Auto-reconnection**: Use `reconnecting-websocket` library (already included)
2. **Token refresh**: Update WebSocket connection when auth token changes
3. **Connection status**: Show connection indicator to users
4. **Message persistence**: Store messages in state management (Redux/Context)
5. **Typing indicators**: Can be added via additional message types
6. **Read receipts**: Implement via REST API endpoint after displaying message
7. **Message ordering**: Backend sends timestamp; sort on frontend if needed

---

## Testing WebSocket Connection

### Browser Console Test
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/?token=YOUR_TOKEN');

ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Received:', JSON.parse(e.data));
ws.onerror = (e) => console.error('Error:', e);

// Send test message
ws.send(JSON.stringify({
  receiver_id: 2,
  message: "Test message"
}));
```

---

## Production Deployment Notes

1. **Use WSS**: Change protocol to `wss://` in production
2. **CORS**: Backend already configured with `AllowedHostsOriginValidator`
3. **Redis**: Ensure Redis is running and accessible (required for channels)
4. **Load Balancing**: Use sticky sessions or configure channel layers for multiple servers

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection fails | Check token validity, backend URL, Redis running |
| Messages not received | Verify user is authenticated, check browser console |
| Reconnection issues | Install `reconnecting-websocket` package |
| CORS errors | Add your frontend URL to backend `ALLOWED_HOSTS` |

---

## Support

For backend issues, check:
- Django Channels logs
- Redis connection status: `redis-cli ping`
- WebSocket route configuration in `apps/communication/routing.py`

## Additional Features (Future)

- Typing indicators
- Online/offline status
- Message reactions
- File upload support
- Group chat support
