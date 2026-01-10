# How to Disable WebSocket and Fix Auto-Update

## Step 1: Find and Disable WebSocket Hook

Your console shows WebSocket is trying to connect and failing. This interferes with long polling.

### Find this file: `useNotificationWebSocket.ts`

Look for code like this:

```typescript
// useNotificationWebSocket.ts
export const useNotificationWebSocket = () => {
  // WebSocket connection code...
  const ws = new WebSocket('ws://127.0.0.1:8000/ws/notifications/...');
  // ...
};
```

### Find where it's being used

Search your codebase for:

```typescript
import { useNotificationWebSocket } from './hooks/useNotificationWebSocket';

// Or
import useNotificationWebSocket from './hooks/useNotificationWebSocket';
```

### Disable it completely

**Option A: Comment it out**

```typescript
// In your component or layout:
const YourComponent = () => {
  // ❌ COMMENT THIS OUT:
  // useNotificationWebSocket();

  // ✅ KEEP ONLY THIS:
  useLongPolling(token, handleEvent, { enabled: true });

  // ... rest of code
};
```

**Option B: Remove the import**

```typescript
// ❌ Remove this line:
// import { useNotificationWebSocket } from './hooks/useNotificationWebSocket';

// ✅ Keep only:
import { useLongPolling } from './hooks/useLongPolling';
```

---

## Step 2: Replace Your useLongPolling.ts

**Copy the complete file from `FRONTEND_FIX_useLongPolling.ts`**

This version fixes:
- Double polling prevention
- React Strict Mode issues
- Proper cleanup
- Detailed logging

---

## Step 3: Update Your Chat Component

### Example implementation:

```typescript
// ChatComponent.tsx or wherever you handle chat
import { useState, useCallback, useEffect } from 'react';
import { useLongPolling } from './hooks/useLongPolling';

export const ChatComponent = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  // Get token from your auth system
  const token = localStorage.getItem('authToken');

  // Handle events from long polling
  const handleEvent = useCallback((eventType: string, data: any) => {
    console.log('[ChatComponent] Event received:', eventType, data);

    switch (eventType) {
      case 'message':
        console.log('[ChatComponent] Adding message to state');
        setMessages(prev => {
          // Prevent duplicates
          if (prev.some(msg => msg.id === data.id)) {
            console.log('[ChatComponent] Duplicate message, skipping');
            return prev;
          }
          console.log('[ChatComponent] New message added!');
          return [...prev, data];
        });
        break;

      case 'typing':
        // Handle typing indicator
        console.log('[ChatComponent] Typing event:', data);
        break;

      case 'read_receipt':
        // Handle read receipt
        console.log('[ChatComponent] Read receipt:', data);
        break;

      case 'notification':
        // Handle notification
        console.log('[ChatComponent] Notification:', data);
        break;

      default:
        console.log('[ChatComponent] Unknown event type:', eventType);
    }
  }, []);

  // Start long polling
  useLongPolling(token, handleEvent, {
    enabled: true, // MUST be true
    apiBase: 'http://127.0.0.1:8000/api/v1',
    onConnect: () => {
      console.log('[ChatComponent] Connected!');
      setIsConnected(true);
    },
    onDisconnect: () => {
      console.log('[ChatComponent] Disconnected');
      setIsConnected(false);
    },
    onError: (error) => {
      console.error('[ChatComponent] Error:', error);
    }
  });

  return (
    <div>
      <div>Status: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}</div>
      <div>
        {messages.map(msg => (
          <div key={msg.id}>{msg.message}</div>
        ))}
      </div>
    </div>
  );
};
```

---

## Step 4: Verify It's Working

### Open browser console and you should see:

```
[LongPolling] Effect triggered - enabled: true hasToken: true
[LongPolling] 🚀 Starting polling loop...
[LongPolling] 📡 Request #1 at 10:30:00
[LongPolling] ✅ Response received in 5.52s
[LongPolling] No events (timeout)
[LongPolling] 🔄 Continuing loop...
[LongPolling] 📡 Request #2 at 10:30:05
[LongPolling] ✅ Response received in 5.51s
[LongPolling] No events (timeout)
[LongPolling] 🔄 Continuing loop...
[LongPolling] 📡 Request #3 at 10:30:11
... (continues forever)
```

### When you send a message:

```
[LongPolling] 📡 Request #5 at 10:30:20
[LongPolling] ✅ Response received in 0.15s
[LongPolling] 📨 1 event(s) received
[LongPolling] Processing event 1: message
[ChatComponent] Event received: message {...}
[ChatComponent] Adding message to state
[ChatComponent] New message added!
[LongPolling] 🔄 Continuing loop...
```

### What you should NOT see:

- ❌ `WebSocket connection failed`
- ❌ `[LongPolling] Polling aborted` (except on page navigation)
- ❌ `[LongPolling] Already polling, ignoring duplicate call` (after first mount)

---

## Step 5: Check Network Tab

Open Chrome DevTools → Network tab:

1. Filter by "poll"
2. You should see continuous requests every ~5-6 seconds
3. Each request should complete in 0.1s-5.5s
4. No gaps between requests

---

## Common Issues

### Issue: "Already polling, ignoring duplicate call"

**Cause:** React Strict Mode mounting twice

**Fix:** The new hook handles this automatically. You'll see the message once, then it works normally.

### Issue: WebSocket errors still appearing

**Cause:** WebSocket hook still active somewhere

**Fix:** Search entire codebase for:
```bash
# In VS Code, search for:
useNotificationWebSocket
WebSocket
ws://
```

Comment out or remove all WebSocket-related code.

### Issue: Events not updating UI

**Cause:** Event handler not calling setState

**Fix:** Make sure your `handleEvent` function calls `setMessages` or similar:

```typescript
const handleEvent = useCallback((eventType: string, data: any) => {
  if (eventType === 'message') {
    setMessages(prev => [...prev, data]); // MUST call setState!
  }
}, []);
```

---

## Quick Test

### Create test file: `TestPolling.tsx`

```typescript
import { useEffect, useState } from 'react';

export const TestPolling = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const [events, setEvents] = useState<any[]>([]);

  const addLog = (msg: string) => {
    const time = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `${time}: ${msg}`]);
    console.log(msg);
  };

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (!token) {
      addLog('❌ No token found');
      return;
    }

    let active = true;
    let count = 0;

    const poll = async () => {
      addLog('🚀 Starting poll loop');

      while (active) {
        count++;
        addLog(`📡 Request #${count}`);

        try {
          const res = await fetch(
            `http://127.0.0.1:8000/api/v1/communication/poll/events/?token=${token}`
          );

          addLog(`✅ Response: ${res.status}`);

          const data = await res.json();

          if (data.events?.length > 0) {
            addLog(`📨 ${data.events.length} events!`);
            setEvents(prev => [...prev, ...data.events]);
          } else {
            addLog('No events (timeout)');
          }

        } catch (error: any) {
          addLog(`❌ Error: ${error.message}`);
          await new Promise(r => setTimeout(r, 2000));
        }
      }

      addLog('🛑 Poll stopped');
    };

    poll();

    return () => {
      active = false;
      addLog('🧹 Cleanup');
    };
  }, []);

  return (
    <div style={{ padding: 20, fontFamily: 'monospace' }}>
      <h2>Polling Test</h2>

      <div style={{ marginTop: 20 }}>
        <h3>Logs ({logs.length}):</h3>
        <div style={{
          background: '#000',
          color: '#0f0',
          padding: 10,
          height: 300,
          overflow: 'auto'
        }}>
          {logs.map((log, i) => (
            <div key={i}>{log}</div>
          ))}
        </div>
      </div>

      <div style={{ marginTop: 20 }}>
        <h3>Events Received ({events.length}):</h3>
        {events.map((e, i) => (
          <div key={i} style={{ background: '#f0f0f0', padding: 10, margin: 5 }}>
            <strong>{e.event}:</strong> {JSON.stringify(e.data)}
          </div>
        ))}
      </div>
    </div>
  );
};
```

**Use it:**
```typescript
// Replace your current chat component temporarily
import { TestPolling } from './TestPolling';

function App() {
  return <TestPolling />;
}
```

**Expected result:**
- Logs show continuous polling every ~5 seconds
- When you send a message from another window, it appears in Events
- No WebSocket errors
- No "aborted" messages

---

## Success Criteria

✅ Console shows continuous polling
✅ No WebSocket errors
✅ Messages appear automatically (no refresh)
✅ Network tab shows requests every ~5-6s
✅ Status shows "🟢 Connected"

If all these are true, auto-update is working!
