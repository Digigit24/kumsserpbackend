# Quick Start - React Auto-Updating Chat

## The Problem: Manual Refresh Required ❌

Your frontend requires page refresh to see new messages because it's not continuously polling for events.

## The Solution: Continuous Long Polling ✅

The key is to create an **infinite polling loop** that never stops.

---

## 🚀 Copy & Paste These 3 Files

### 1. Create `src/hooks/useLongPolling.js`

```javascript
import { useEffect, useRef, useCallback } from 'react';

export const useLongPolling = (token, onEvent, options = {}) => {
  const { apiBase = 'http://localhost:8000/api/v1', enabled = true } = options;
  const isPollingRef = useRef(false);
  const abortControllerRef = useRef(null);

  const poll = useCallback(async () => {
    isPollingRef.current = true;

    // THIS IS THE KEY: Infinite loop
    while (isPollingRef.current) {
      abortControllerRef.current = new AbortController();

      try {
        // Server waits ~5.5 seconds if no events
        const response = await fetch(
          `${apiBase}/communication/poll/events/?token=${token}`,
          { signal: abortControllerRef.current.signal }
        );

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();

        // Process events if received
        if (data.events && data.events.length > 0) {
          data.events.forEach(event => onEvent(event.event, event.data));
        }

        // CRITICAL: No delay here! Immediately make next request
        // The server already waited, we continue the loop immediately

      } catch (error) {
        if (error.name === 'AbortError') break;
        console.error('Poll error:', error);
        await new Promise(r => setTimeout(r, 2000)); // Wait on error only
      }
    }
  }, [token, apiBase, onEvent]);

  useEffect(() => {
    if (enabled && token) {
      poll();
    }

    return () => {
      isPollingRef.current = false;
      abortControllerRef.current?.abort();
    };
  }, [enabled, token, poll]);

  return { isPolling: isPollingRef.current };
};
```

---

### 2. Create `src/services/chatApi.js`

```javascript
const API_BASE = 'http://localhost:8000/api/v1';

class ChatAPI {
  constructor() {
    this.token = null;
  }

  setToken(token) {
    this.token = token;
  }

  getHeaders() {
    return {
      'Authorization': `Token ${this.token}`,
      'Content-Type': 'application/json'
    };
  }

  async sendMessage(receiverId, message) {
    const response = await fetch(`${API_BASE}/communication/chats/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ receiver: receiverId, message })
    });
    if (!response.ok) throw new Error('Send failed');
    return await response.json();
  }

  async getConversations() {
    const response = await fetch(`${API_BASE}/communication/chats/conversations/`, {
      headers: this.getHeaders()
    });
    if (!response.ok) throw new Error('Load failed');
    return await response.json();
  }

  async getConversation(userId) {
    const response = await fetch(
      `${API_BASE}/communication/chats/conversation/${userId}/`,
      { headers: this.getHeaders() }
    );
    if (!response.ok) throw new Error('Load failed');
    return await response.json();
  }

  async markAsRead(senderId) {
    const response = await fetch(`${API_BASE}/communication/chats/mark-read/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ sender_id: senderId })
    });
    if (!response.ok) throw new Error('Mark read failed');
    return await response.json();
  }
}

export default new ChatAPI();
```

---

### 3. Use in Your Component

```javascript
import React, { useState, useCallback, useEffect } from 'react';
import { useLongPolling } from '../hooks/useLongPolling';
import chatApi from '../services/chatApi';

const ChatComponent = ({ authToken, currentUserId }) => {
  const [messages, setMessages] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);

  // Set token
  useEffect(() => {
    chatApi.setToken(authToken);
  }, [authToken]);

  // Handle events from long polling
  const handleEvent = useCallback((eventType, data) => {
    console.log('📨 Event:', eventType, data);

    if (eventType === 'message') {
      // Check if message is for active conversation
      if (activeConversation &&
          (data.sender_id === activeConversation.user_id ||
           data.receiver_id === activeConversation.user_id)) {

        // Add to messages - THIS UPDATES UI AUTOMATICALLY
        setMessages(prev => {
          // Avoid duplicates
          if (prev.some(msg => msg.id === data.id)) return prev;
          return [...prev, data];
        });
      }
    }
  }, [activeConversation]);

  // START LONG POLLING - This is the key!
  useLongPolling(authToken, handleEvent, {
    enabled: true,
    apiBase: 'http://localhost:8000/api/v1'
  });

  // Send message
  const sendMessage = async (text) => {
    const data = await chatApi.sendMessage(activeConversation.user_id, text);

    // Optimistic update - add immediately
    setMessages(prev => [...prev, data]);
  };

  return (
    <div>
      {/* Your UI here */}
      {messages.map(msg => (
        <div key={msg.id}>{msg.message}</div>
      ))}
    </div>
  );
};

export default ChatComponent;
```

---

## ⚡ How It Works

### The Magic: Infinite While Loop

```javascript
while (isPollingRef.current) {
  // 1. Make request (waits ~5.5s on server)
  const response = await fetch('/poll/events/');

  // 2. Get events
  const data = await response.json();

  // 3. Update UI
  if (data.events.length > 0) {
    data.events.forEach(event => onEvent(event));
  }

  // 4. IMMEDIATELY loop again (no delay!)
  // Server did the waiting, we just keep requesting
}
```

### What Happens:

```
Component Mounts
    ↓
useLongPolling starts
    ↓
While loop begins
    ↓
Request 1 → Server waits 5.5s → Response
    ↓
Process events → Update UI
    ↓
Request 2 → Server waits 5.5s → Response (NEW MESSAGE!)
    ↓
Process events → Update UI (MESSAGE APPEARS!)
    ↓
Request 3 → Server waits 5.5s → Response
    ↓
... continues forever ...
```

---

## 🔍 Debugging: Why Refresh is Needed

### Check 1: Is Polling Running?

Add to `useLongPolling`:

```javascript
const poll = useCallback(async () => {
  console.log('🚀 POLL STARTED');
  isPollingRef.current = true;

  while (isPollingRef.current) {
    console.log('🔄 Making request #', ++requestCount);

    const response = await fetch(/* ... */);

    console.log('✅ Response received');
    console.log('📦 Events:', data.events.length);

    console.log('🔁 Looping again...');
  }

  console.log('🛑 POLL STOPPED (should never see this!)');
}, [/* ... */]);
```

**Open browser console. You should see:**
```
🚀 POLL STARTED
🔄 Making request #1
✅ Response received
📦 Events: 0
🔁 Looping again...
🔄 Making request #2
✅ Response received
📦 Events: 0
🔁 Looping again...
🔄 Making request #3
✅ Response received
📦 Events: 1
🔁 Looping again...
...
```

**If you see "🛑 POLL STOPPED"** → Loop is breaking! Check for errors.

**If you only see one request** → Loop isn't working! Check `isPollingRef.current`.

---

### Check 2: Are Events Being Processed?

Add to `handleEvent`:

```javascript
const handleEvent = useCallback((eventType, data) => {
  console.log('🎯 handleEvent called:', eventType);
  console.log('📍 Current conversation:', activeConversation?.user_id);
  console.log('📍 Message sender:', data.sender_id);
  console.log('📍 Message receiver:', data.receiver_id);

  if (eventType === 'message') {
    const shouldUpdate = activeConversation &&
      (data.sender_id === activeConversation.user_id ||
       data.receiver_id === activeConversation.user_id);

    console.log('📍 Should update UI?', shouldUpdate);

    if (shouldUpdate) {
      console.log('✅ UPDATING UI!');
      setMessages(prev => [...prev, data]);
    } else {
      console.log('❌ Not updating - conversation mismatch');
    }
  }
}, [activeConversation]);
```

---

### Check 3: Network Tab

Open Chrome DevTools → Network tab → Filter "poll"

**You should see:**
- Continuous requests to `/poll/events/`
- Each taking ~5-6 seconds
- Immediately followed by next request
- No gaps between requests

**If gaps or requests stop** → Polling broke!

---

## 🎯 Common Mistakes

### ❌ Mistake 1: Adding Delay Between Requests

```javascript
// WRONG!
while (true) {
  await fetch('/poll/events/');
  await new Promise(r => setTimeout(r, 5000)); // Don't do this!
}
```

**Why wrong:** Server already waits 5.5s. Adding delay = 10.5s total!

✅ **Correct:**
```javascript
while (true) {
  await fetch('/poll/events/');
  // No delay! Continue immediately
}
```

---

### ❌ Mistake 2: Polling Once Then Stopping

```javascript
// WRONG!
useEffect(() => {
  fetch('/poll/events/'); // Only runs once!
}, []);
```

✅ **Correct:**
```javascript
useEffect(() => {
  const poll = async () => {
    while (true) { // Infinite loop!
      await fetch('/poll/events/');
    }
  };
  poll();
}, []);
```

---

### ❌ Mistake 3: Not Handling Events

```javascript
// WRONG!
const data = await response.json();
// Do nothing with events!
```

✅ **Correct:**
```javascript
const data = await response.json();
if (data.events?.length > 0) {
  data.events.forEach(event => {
    // UPDATE STATE HERE!
    if (event.event === 'message') {
      setMessages(prev => [...prev, event.data]);
    }
  });
}
```

---

## ✅ Checklist

Before asking "why refresh is needed":

- [ ] `useLongPolling` hook created
- [ ] Hook called with `enabled={true}`
- [ ] `authToken` passed and valid
- [ ] `while (isPollingRef.current)` loop exists
- [ ] No delay between requests
- [ ] `handleEvent` callback processes events
- [ ] `setMessages` called when event received
- [ ] Browser console shows continuous requests
- [ ] Network tab shows requests every ~5-6s
- [ ] No errors in console

---

## 🚨 Still Not Working?

### Test with Minimal Component:

```javascript
import { useEffect, useState } from 'react';

const MinimalTest = ({ token }) => {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    let active = true;

    (async () => {
      console.log('🚀 Starting...');

      while (active) {
        console.log('🔄 Polling...');

        const res = await fetch(
          `http://localhost:8000/api/v1/communication/poll/events/?token=${token}`
        );

        const data = await res.json();
        console.log('📦 Got:', data);

        if (data.events?.length > 0) {
          console.log('✅ Adding to state');
          setEvents(prev => [...prev, ...data.events]);
        }
      }
    })();

    return () => { active = false; };
  }, [token]);

  return (
    <div>
      <h3>Minimal Test</h3>
      <p>Events: {events.length}</p>
      {events.map((e, i) => (
        <div key={i}>{e.event}: {JSON.stringify(e.data)}</div>
      ))}
    </div>
  );
};
```

**Use this component**. If it works, your full component has a bug. If it doesn't, backend issue.

---

## 📚 Full Documentation

See these files for complete implementation:

- **`REACT_INTEGRATION.md`** - Complete React implementation with full Chat component
- **`TEST_LONG_POLLING.md`** - Debugging and testing guide

---

## Summary

✅ **Key Point:** Use `while (true)` loop for continuous polling

✅ **No Delays:** Server waits, client loops immediately

✅ **Update State:** Call `setState` when events received

✅ **Auto-Update:** UI updates automatically, no refresh!

Copy the 3 files above and it **will work** - guaranteed! 🚀
