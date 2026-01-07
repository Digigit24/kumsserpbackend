# Auto-Start Redis on Windows

## Option 1: Windows Service (Best for Production)

### Install Redis as Windows Service:

1. **Download Redis for Windows:**

   - Get from: https://github.com/microsoftarchive/redis/releases
   - Or use: https://github.com/tporadowski/redis/releases (maintained version)

2. **Install as Service:**

   ```powershell
   # Run as Administrator
   redis-server --service-install redis.windows.conf --loglevel verbose
   ```

3. **Start the Service:**

   ```powershell
   redis-server --service-start
   ```

4. **Set to Auto-Start:**

   ```powershell
   # Open Services (Win+R, type: services.msc)
   # Find "Redis" service
   # Right-click → Properties → Startup type: Automatic
   ```

5. **Verify:**
   ```powershell
   redis-cli ping
   # Should return: PONG
   ```

### Service Commands:

```powershell
# Start
redis-server --service-start

# Stop
redis-server --service-stop

# Uninstall
redis-server --service-uninstall
```

---

## Option 2: WSL (Windows Subsystem for Linux)

### Install Redis in WSL:

```bash
sudo apt update
sudo apt install redis-server
```

### Enable Auto-Start:

```bash
# Edit redis config
sudo nano /etc/redis/redis.conf

# Make sure these are set:
# supervised systemd
# daemonize yes

# Enable service
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### Check Status:

```bash
sudo systemctl status redis-server
redis-cli ping
```

---

## Option 3: Docker (Easiest for Development)

### Create docker-compose.yml:

```yaml
version: "3.8"
services:
  redis:
    image: redis:alpine
    container_name: kumss_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: always
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

### Run:

```bash
# Start (runs in background)
docker-compose up -d redis

# Stop
docker-compose down

# View logs
docker-compose logs -f redis
```

### Auto-start with Docker Desktop:

- Docker Desktop → Settings → General → "Start Docker Desktop when you log in"

---

## Option 4: Startup Script (Quick & Simple)

### Create `start_redis.bat`:

```batch
@echo off
echo Starting Redis...
start /B redis-server
echo Redis started in background
```

### Add to Windows Startup:

1. Press `Win+R`, type: `shell:startup`
2. Copy `start_redis.bat` to the Startup folder
3. Redis will start when Windows boots

---

## Recommended Setup for Your Project

**For Development:**

```bash
# Use Docker (easiest)
docker-compose up -d redis
```

**For Production/Server:**

```powershell
# Install as Windows Service
redis-server --service-install
redis-server --service-start
```

---

## Verify Redis is Running

```bash
# Test connection
redis-cli ping

# Check if Django can connect
python manage.py shell
>>> from channels.layers import get_channel_layer
>>> channel_layer = get_channel_layer()
>>> print(channel_layer)
```

---

## Update Django Settings

Make sure your `settings.py` has:

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

Install required package:

```bash
pip install channels-redis
```
