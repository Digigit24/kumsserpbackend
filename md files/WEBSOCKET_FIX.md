# WebSocket Connection Fix

## Issue

WebSocket connections to `/ws/notifications/` and `/ws/chat/` are failing.

## Root Cause

The backend has WebSocket consumers configured, but **Django Channels requires Redis** to be running as a channel layer.

## Solution Options

### Option 1: Install & Run Redis (Recommended for Production)

1. **Install Redis:**

   - Windows: Download from https://github.com/microsoftarchive/redis/releases
   - Or use WSL: `sudo apt-get install redis-server`

2. **Start Redis:**

   ```bash
   redis-server
   ```

3. **Verify settings.py has:**
   ```python
   CHANNEL_LAYERS = {
       'default': {
           'BACKEND': 'channels_redis.core.RedisChannelLayer',
           'CONFIG': {
               "hosts": [('127.0.0.1', 6379)],
           },
       },
   }
   ```

### Option 2: Use In-Memory Channel Layer (Development Only)

If you don't need WebSocket functionality right now:

1. **Install:**

   ```bash
   pip install channels[daphne]
   ```

2. **Update settings.py:**
   ```python
   CHANNEL_LAYERS = {
       "default": {
           "BACKEND": "channels.layers.InMemoryChannelLayer"
       }
   }
   ```

### Option 3: Disable WebSocket Reconnection (Quick Fix)

If WebSockets aren't needed, disable them in the frontend:

- Comment out `useNotificationWebSocket` and `useChatWebSocket` hooks
- Or set a flag to disable WebSocket connections

## Current Status

- ✅ Permissions API fixed (`user_context` field now returned)
- ⚠️ WebSocket requires Redis or in-memory channel layer
