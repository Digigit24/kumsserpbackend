# Redis Windows Service - Step by Step Guide

## Step 1: Download Redis for Windows

### Option A: Tporadowski Redis (Recommended - Actively Maintained)

1. Go to: https://github.com/tporadowski/redis/releases
2. Download: **Redis-x64-5.0.14.1.msi** (or latest version)
3. Run the installer
4. **Important:** Check "Add Redis to PATH" during installation
5. Default install location: `C:\Program Files\Redis\`

### Option B: Microsoft Archive (Older but Stable)

1. Go to: https://github.com/microsoftarchive/redis/releases
2. Download: **Redis-x64-3.0.504.msi**
3. Run the installer

---

## Step 2: Install Redis as Windows Service

### Open PowerShell as Administrator:

1. Press `Win + X`
2. Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

### Navigate to Redis directory:

```powershell
cd "C:\Program Files\Redis"
```

### Install the service:

```powershell
redis-server --service-install redis.windows.conf --loglevel verbose
```

**Expected output:**

```
[####] Installing service...
[####] Service installed
```

---

## Step 3: Start Redis Service

### Start the service:

```powershell
redis-server --service-start
```

**Expected output:**

```
[####] Starting service...
[####] Service started
```

---

## Step 4: Set Redis to Auto-Start on Boot

### Method 1: Using Services GUI

1. Press `Win + R`
2. Type: `services.msc`
3. Press Enter
4. Find **"Redis"** in the list
5. Right-click → **Properties**
6. Change **Startup type** to: **Automatic**
7. Click **Apply** → **OK**

### Method 2: Using PowerShell (Admin)

```powershell
Set-Service -Name Redis -StartupType Automatic
```

---

## Step 5: Verify Redis is Running

### Test 1: Check Service Status

```powershell
Get-Service Redis
```

**Expected output:**

```
Status   Name               DisplayName
------   ----               -----------
Running  Redis              Redis
```

### Test 2: Ping Redis

```powershell
redis-cli ping
```

**Expected output:**

```
PONG
```

### Test 3: Check Redis Info

```powershell
redis-cli info server
```

---

## Step 6: Configure Django to Use Redis

### Install Python package:

```bash
pip install channels-redis
```

### Verify settings.py has:

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

### Test from Django:

```bash
python manage.py shell
```

```python
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
print(channel_layer)
# Should show RedisChannelLayer object
```

---

## Common Commands

### Service Management:

```powershell
# Start
redis-server --service-start

# Stop
redis-server --service-stop

# Restart
redis-server --service-stop
redis-server --service-start

# Uninstall
redis-server --service-uninstall
```

### Check if Redis is listening:

```powershell
netstat -an | findstr :6379
```

**Expected output:**

```
TCP    127.0.0.1:6379         0.0.0.0:0              LISTENING
```

---

## Troubleshooting

### Issue: "redis-server is not recognized"

**Solution:**

```powershell
# Add to PATH manually
$env:Path += ";C:\Program Files\Redis"

# Or permanently:
[System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\Redis", [System.EnvironmentVariableTarget]::Machine)
```

### Issue: Service won't start

**Solution:**

```powershell
# Check logs
Get-EventLog -LogName Application -Source Redis -Newest 10

# Or check Redis log file
notepad "C:\Program Files\Redis\Logs\redis_log.txt"
```

### Issue: Port 6379 already in use

**Solution:**

```powershell
# Find what's using the port
netstat -ano | findstr :6379

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

---

## Quick Verification Checklist

- [ ] Redis service installed
- [ ] Redis service started
- [ ] Redis set to "Automatic" startup
- [ ] `redis-cli ping` returns `PONG`
- [ ] Port 6379 is listening
- [ ] `channels-redis` installed in Python
- [ ] Django can connect to Redis

---

## Next Steps

After Redis is running:

1. Restart your Django server
2. WebSocket connections should work
3. Test notifications and chat features

**Restart Django:**

```bash
# Stop current server (Ctrl+C)
python manage.py runserver
```

The WebSocket errors should disappear! ✅
