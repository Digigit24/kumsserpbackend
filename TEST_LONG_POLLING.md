# Testing Long Polling - Comprehensive Guide

## Quick Test: Verify Auto-Update Works

### Test 1: Check Backend is Working

**Step 1: Test Polling Endpoint**
```bash
curl "http://localhost:8000/api/v1/communication/poll/test/"
```

**Expected Response:**
```json
{
  "status": "ok",
  "message": "Long polling is working",
  "timestamp": 1704888600.123
}
```

**Step 2: Test Actual Polling**
```bash
# This will wait ~5.5 seconds if no events
curl "http://localhost:8000/api/v1/communication/poll/events/?token=YOUR_TOKEN"
```

**Expected Response (no events):**
```json
{
  "events": [],
  "timestamp": 1704888600.123
}
```

---

### Test 2: Verify Messages Trigger Events

**Terminal 1 (Start Polling):**
```bash
# This will WAIT for events
curl "http://localhost:8000/api/v1/communication/poll/events/?token=USER_B_TOKEN"
```

**Terminal 2 (Send Message):**
```bash
# Send a message to User B
curl -X POST "http://localhost:8000/api/v1/communication/chats/" \
  -H "Authorization: Token USER_A_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "receiver": USER_B_ID,
    "message": "Test message"
  }'
```

**Terminal 1 should immediately receive:**
```json
{
  "events": [
    {
      "event": "message",
      "data": {
        "id": 123,
        "sender_id": USER_A_ID,
        "message": "Test message",
        ...
      }
    }
  ],
  "timestamp": 1704888600.123
}
```

✅ If you see this, long polling is working!

---

## Frontend Testing

### Test 3: Verify Continuous Polling

Add this to your browser console when chat is open:

```javascript
// Monitor polling requests
const originalFetch = window.fetch;
let pollCount = 0;

window.fetch = function(...args) {
  if (args[0].includes('/poll/events/')) {
    pollCount++;
    console.log(`🔄 Poll request #${pollCount}`, new Date().toLocaleTimeString());
  }
  return originalFetch.apply(this, args);
};

// After 30 seconds, check count
setTimeout(() => {
  console.log(`✅ Total poll requests in 30s: ${pollCount}`);
  // Should be 4-6 requests (each takes ~5.5s if no events)
}, 30000);
```

**Expected Output:**
```
🔄 Poll request #1 10:30:00
🔄 Poll request #2 10:30:05
🔄 Poll request #3 10:30:11
🔄 Poll request #4 10:30:16
🔄 Poll request #5 10:30:22
✅ Total poll requests in 30s: 5
```

✅ If you see 4-6 requests, continuous polling is working!

---

### Test 4: Verify Auto-Update

**Setup:**
1. Open browser window A (User A)
2. Open browser window B (User B)
3. Open chat between A and B in both windows

**Test:**
1. Type message in Window A, click Send
2. **Watch Window B** - message should appear **automatically** without refresh!
3. Should take < 6 seconds maximum

**Expected Behavior:**
- Window A: Message appears immediately (optimistic update)
- Window B: Message appears within 0-6 seconds **automatically**

❌ If Window B requires refresh, polling isn't working!

---

## Debugging: Why Auto-Update Doesn't Work

### Problem 1: Polling Not Starting

**Check React Hook:**
```javascript
useEffect(() => {
  console.log('🚀 Starting poll - enabled:', enabled, 'token:', !!token);
  // ...
}, [enabled, token, poll]);
```

**Expected Output:**
```
🚀 Starting poll - enabled: true token: true
```

**Fix if not starting:**
- Ensure `enabled={true}` passed to `useLongPolling`
- Ensure `token` is not null/undefined
- Check component is mounted

---

### Problem 2: Polling Stops After First Request

**Add Debug Logs:**
```javascript
const poll = useCallback(async () => {
  isPollingRef.current = true;
  console.log('🎬 Poll loop started');

  while (isPollingRef.current) {
    console.log('🔄 Making poll request...');

    try {
      const response = await fetch(/* ... */);
      console.log('✅ Poll response received');

      const data = await response.json();
      console.log('📦 Events:', data.events.length);

      // Process events...

      console.log('🔁 Loop continues...');
    } catch (error) {
      console.error('❌ Poll error:', error);
      await new Promise(r => setTimeout(r, 2000));
    }
  }

  console.log('🛑 Poll loop ended');
}, [/* ... */]);
```

**Expected Output (continuous):**
```
🎬 Poll loop started
🔄 Making poll request...
✅ Poll response received
📦 Events: 0
🔁 Loop continues...
🔄 Making poll request...
✅ Poll response received
📦 Events: 1
🔁 Loop continues...
🔄 Making poll request...
...
```

**If loop stops:**
- Check for errors in console
- Verify `isPollingRef.current` stays `true`
- Check component didn't unmount

---

### Problem 3: Events Received But UI Doesn't Update

**Add Debug to Event Handler:**
```javascript
const handleEvent = useCallback((eventType, data) => {
  console.log('📨 Event handler called:', eventType);
  console.log('📝 Data:', data);

  switch (eventType) {
    case 'message':
      console.log('💬 Processing message event');
      handleNewMessage(data);
      break;
    // ...
  }
}, []);
```

**Then in handleNewMessage:**
```javascript
const handleNewMessage = useCallback((data) => {
  console.log('🔍 Checking if should update UI...');
  console.log('Active conversation:', activeConversation);
  console.log('Sender ID:', data.sender_id);
  console.log('Receiver ID:', data.receiver_id);

  if (activeConversation &&
      (data.sender_id === activeConversation.user_id ||
       data.receiver_id === activeConversation.user_id)) {
    console.log('✅ Should update UI!');

    setMessages(prev => {
      console.log('📝 Current messages:', prev.length);
      const updated = [...prev, data];
      console.log('📝 Updated messages:', updated.length);
      return updated;
    });
  } else {
    console.log('❌ Not for active conversation, skipping UI update');
  }
}, [activeConversation]);
```

**If events received but UI not updating:**
- Check `activeConversation` matches sender/receiver
- Verify `setMessages` is called
- Check React DevTools for state updates

---

### Problem 4: Backend Not Sending Events

**Check Backend Logs:**
```bash
# Enable debug logging
# In settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'apps.communication': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

**Send a test message and check logs:**
```
DEBUG Publishing message event to queue: event_queue:user:123
DEBUG Queued message to event_queue:user:123
```

**If no logs:**
- `publish_message_event` not being called
- Check `views.py` line 259

---

### Problem 5: RabbitMQ Queue Issues

**Check Queue Depth:**
```bash
# Open RabbitMQ management UI
http://localhost:15672

# Or use CLI
sudo rabbitmqctl list_queues name messages
```

**Expected:**
```
event_queue:user:123    0
event_queue:user:456    0
```

**If messages stuck in queue (> 10):**
- Long polling not consuming
- Check frontend is calling `/poll/events/`
- Restart RabbitMQ: `sudo systemctl restart rabbitmq-server`

---

## Complete Test Script

Save as `test_long_polling.sh`:

```bash
#!/bin/bash

API_BASE="http://localhost:8000/api/v1"
TOKEN_A="user_a_token_here"
TOKEN_B="user_b_token_here"
USER_A_ID="1"
USER_B_ID="2"

echo "🧪 Testing Long Polling..."
echo ""

# Test 1: Backend health
echo "1️⃣ Testing backend health..."
curl -s "$API_BASE/communication/poll/test/" | jq .
echo ""

# Test 2: Start polling in background
echo "2️⃣ Starting long poll (will wait for events)..."
curl -s "$API_BASE/communication/poll/events/?token=$TOKEN_B" > /tmp/poll_result.json &
POLL_PID=$!
sleep 1

# Test 3: Send message
echo "3️⃣ Sending test message..."
curl -s -X POST "$API_BASE/communication/chats/" \
  -H "Authorization: Token $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d "{\"receiver\": $USER_B_ID, \"message\": \"Auto-update test at $(date)\"}" | jq .
echo ""

# Test 4: Wait for poll result
echo "4️⃣ Waiting for poll response (max 10s)..."
sleep 3
if wait $POLL_PID 2>/dev/null; then
  echo "✅ Poll completed!"
  echo "📦 Events received:"
  cat /tmp/poll_result.json | jq .
else
  echo "⏰ Poll still waiting (this is normal if no events)"
  kill $POLL_PID 2>/dev/null
fi
echo ""

# Test 5: Check RabbitMQ
echo "5️⃣ Checking RabbitMQ queues..."
python manage.py shell -c "
from apps.communication.rabbitmq_queue import get_rabbitmq
client = get_rabbitmq()
print('Connected:', client.is_connected())
" 2>/dev/null
echo ""

echo "✅ Tests complete!"
```

Run it:
```bash
chmod +x test_long_polling.sh
./test_long_polling.sh
```

---

## Expected vs. Actual Behavior

### ✅ Correct Behavior:

1. **Polling starts** when component mounts
2. **Polling continues** in infinite loop
3. **Request waits** ~5.5 seconds on server
4. **Response received** with events or empty
5. **New request** made immediately
6. **Events processed** and UI updated
7. **Loop never stops** (until component unmounts)

### ❌ Incorrect Behavior:

1. Polling makes 1 request then stops
2. Polling waits on client side (wrong!)
3. Events received but ignored
4. UI updates on refresh only
5. Errors in console

---

## Quick Fix Checklist

If auto-update doesn't work:

- [ ] RabbitMQ is running: `python manage.py check_rabbitmq`
- [ ] Backend test passes: `curl /poll/test/`
- [ ] Polling hook is enabled: Check `enabled={true}`
- [ ] Token is valid: Check `token` prop
- [ ] Loop continues: Check console logs
- [ ] Events received: Check network tab
- [ ] Event handler called: Add `console.log`
- [ ] State updates: Check React DevTools
- [ ] No errors: Check browser console
- [ ] Component mounted: Check React tree

---

## Still Not Working?

### Minimal Test Component

Create `src/MinimalTest.jsx`:

```javascript
import React, { useEffect, useState } from 'react';

const MinimalTest = ({ token }) => {
  const [events, setEvents] = useState([]);
  const [isPolling, setIsPolling] = useState(false);

  useEffect(() => {
    let active = true;

    const poll = async () => {
      setIsPolling(true);
      console.log('🚀 Starting minimal poll test...');

      while (active) {
        console.log('🔄 Making request...');

        try {
          const response = await fetch(
            `http://localhost:8000/api/v1/communication/poll/events/?token=${token}`
          );

          console.log('✅ Response received:', response.status);

          const data = await response.json();
          console.log('📦 Data:', data);

          if (data.events && data.events.length > 0) {
            console.log('📨 Adding events to state');
            setEvents(prev => [...prev, ...data.events]);
          }

          console.log('🔁 Continuing loop...');
        } catch (error) {
          console.error('❌ Error:', error);
          await new Promise(r => setTimeout(r, 2000));
        }
      }

      console.log('🛑 Poll stopped');
      setIsPolling(false);
    };

    poll();

    return () => {
      console.log('🧹 Cleanup - stopping poll');
      active = false;
    };
  }, [token]);

  return (
    <div style={{ padding: 20 }}>
      <h2>Minimal Poll Test</h2>
      <p>Status: {isPolling ? '🟢 Polling' : '🔴 Stopped'}</p>
      <p>Events received: {events.length}</p>
      <div>
        {events.map((e, i) => (
          <div key={i} style={{ background: '#f0f0f0', padding: 10, margin: 5 }}>
            <strong>{e.event}:</strong> {JSON.stringify(e.data)}
          </div>
        ))}
      </div>
    </div>
  );
};

export default MinimalTest;
```

Use it:
```javascript
import MinimalTest from './MinimalTest';

function App() {
  return <MinimalTest token="your-token" />;
}
```

**Expected behavior:**
1. Component mounts
2. See "🚀 Starting minimal poll test..." in console
3. See "🔄 Making request..." every ~5.5 seconds
4. When you send a message, see "📨 Adding events to state"
5. Event appears on screen **automatically**

If this works but full Chat doesn't, the issue is in the Chat component.

---

## Summary

✅ **Backend:** Fast, optimized, working
✅ **Long Polling:** Continuous loop, no delays
✅ **Events:** Published to RabbitMQ correctly
✅ **React Hook:** Handles polling automatically
✅ **UI Update:** Automatic, no refresh needed

If still having issues after following this guide, the problem is likely:
1. Frontend not starting the poll
2. Poll stopping after first request
3. Events not matching active conversation

Use the debug logs above to identify exactly where it fails!
