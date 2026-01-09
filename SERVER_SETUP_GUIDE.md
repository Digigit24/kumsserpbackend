# Server Setup Guide - Real-Time Chat System

## Quick Start (5 Minutes)

### Step 1: Install and Start Redis

Choose your platform:

#### Linux (Ubuntu/Debian)
```bash
# Install Redis
sudo apt-get update
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server

# Enable auto-start on boot
sudo systemctl enable redis-server

# Verify
redis-cli ping
# Expected output: PONG
```

#### macOS
```bash
# Install Redis via Homebrew
brew install redis

# Start Redis
brew services start redis

# Verify
redis-cli ping
# Expected output: PONG
```

#### Windows (Using WSL)
```bash
# Install WSL first (if not installed)
wsl --install

# Open WSL terminal, then:
sudo apt-get update
sudo apt-get install redis-server

# Start Redis
sudo service redis-server start

# Verify
redis-cli ping
# Expected output: PONG
```

#### Docker (All Platforms)
```bash
# Run Redis container
docker run -d -p 6379:6379 --name redis redis:latest

# Verify container is running
docker ps

# Check Redis
docker exec -it redis redis-cli ping
# Expected output: PONG
```

---

### Step 2: Install Python Dependencies

```bash
# Navigate to project directory
cd /home/user/kumsserpbackend

# Install dependencies (if not already installed)
pip install -r requirements.txt
```

---

### Step 3: Configure Environment

Create or update `.env` file:

```bash
# Copy example
cp .env.example .env

# Edit .env file
nano .env
```

Add/update these lines:
```env
# Redis URL
REDIS_URL=redis://127.0.0.1:6379

# Django settings
DJANGO_SETTINGS_MODULE=kumss_erp.settings.development
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database (if not already configured)
DATABASE_URL=postgresql://user:password@localhost:5432/kumss_erp_db
```

---

### Step 4: Run Database Migrations

```bash
# Run migrations for new chat models
python manage.py migrate communication

# Run all migrations (if needed)
python manage.py migrate
```

---

### Step 5: Check Redis Connection

```bash
python manage.py check_redis
```

**Expected Output:**
```
======================================================================
Redis Connection Check
======================================================================

Redis URL: redis://127.0.0.1:6379

✓ Redis is connected and running!

Redis Server Info:
  Version: 7.1.0
  Mode: standalone
  Connected clients: 1
  Used memory: 1.2M

✓ Real-time messaging system is ready!

======================================================================
```

---

### Step 6: Start Django Server

```bash
python manage.py runserver
```

**Expected Output:**
```
Performing system checks...

System check identified no issues (0 silenced).
January 09, 2026 - 10:00:00
Django version 5.2.9, using settings 'kumss_erp.settings.development'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

## Verify Installation

### 1. Test SSE Connection

Open browser and navigate to:
```
http://localhost:8000/api/v1/communication/sse/test/
```

You should see test events streaming.

### 2. Test API Endpoints

Using curl or Postman:

```bash
# Get auth token first (login)
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'

# Use token to get conversations
curl http://localhost:8000/api/v1/communication/chats/conversations/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

---

## Running in Production

### With Gunicorn

```bash
# Install Gunicorn (already in requirements.txt)
pip install gunicorn

# Run with Gunicorn
gunicorn kumss_erp.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120

# Or use the production settings
gunicorn kumss_erp.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --env DJANGO_SETTINGS_MODULE=kumss_erp.settings.production
```

### With Daphne (ASGI - Recommended for SSE)

```bash
# Daphne is already installed
daphne -b 0.0.0.0 -p 8000 kumss_erp.asgi:application
```

### With Systemd (Linux)

Create `/etc/systemd/system/kumss-backend.service`:

```ini
[Unit]
Description=KUMSS ERP Backend
After=network.target redis.service postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/kumsserpbackend
Environment="DJANGO_SETTINGS_MODULE=kumss_erp.settings.production"
ExecStart=/var/www/kumsserpbackend/venv/bin/daphne -b 0.0.0.0 -p 8000 kumss_erp.asgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl start kumss-backend
sudo systemctl enable kumss-backend
sudo systemctl status kumss-backend
```

---

## Nginx Configuration (Production)

```nginx
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Regular API endpoints
    location /api/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # SSE endpoints - special configuration
    location /api/v1/communication/sse/ {
        proxy_pass http://django;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE specific
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;
        proxy_read_timeout 24h;
        proxy_connect_timeout 24h;
        proxy_send_timeout 24h;
    }

    # Static files
    location /static/ {
        alias /var/www/kumsserpbackend/staticfiles/;
    }

    # Media files
    location /media/ {
        alias /var/www/kumsserpbackend/media/;
    }
}
```

---

## Docker Setup (Optional)

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: kumss_erp_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: .
    command: daphne -b 0.0.0.0 -p 8000 kumss_erp.asgi:application
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - db
    environment:
      - DJANGO_SETTINGS_MODULE=kumss_erp.settings.production
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/kumss_erp_db

volumes:
  redis_data:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

---

## Troubleshooting

### Redis Connection Failed

**Error:** `Redis is NOT connected!`

**Solutions:**
1. Check if Redis is running:
   ```bash
   redis-cli ping
   ```

2. Check Redis logs:
   ```bash
   # Linux
   sudo journalctl -u redis

   # macOS
   brew services info redis

   # Docker
   docker logs redis
   ```

3. Check firewall:
   ```bash
   # Allow Redis port
   sudo ufw allow 6379
   ```

### Port Already in Use

**Error:** `Error: That port is already in use.`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
python manage.py runserver 0.0.0.0:8001
```

### Migration Errors

**Error:** `Migration errors`

**Solution:**
```bash
# Show migrations
python manage.py showmigrations communication

# Run migrations
python manage.py migrate communication

# If still fails, fake the migration (use with caution)
python manage.py migrate communication --fake
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'django'`

**Solution:**
```bash
# Check if in virtual environment
which python

# Activate virtual environment (if you have one)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Monitoring

### Check System Status

```bash
# Check Redis
redis-cli ping
python manage.py check_redis

# Check Django
python manage.py check

# Check database
python manage.py dbshell
```

### Monitor Logs

```bash
# Django logs (if LOG_TO_FILE=True)
tail -f logs/debug.log

# Redis logs
redis-cli monitor

# System logs
journalctl -f -u kumss-backend
```

### Performance Metrics

```bash
# Redis stats
redis-cli info stats

# Redis memory
redis-cli info memory

# Active connections
redis-cli client list
```

---

## One-Command Setup Script

Create `setup.sh`:

```bash
#!/bin/bash

echo "========================================="
echo "KUMSS ERP Real-Time Chat Setup"
echo "========================================="

# Check if Redis is running
echo "\n1. Checking Redis..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis is running"
else
    echo "✗ Redis is not running!"
    echo "Starting Redis..."

    # Try to start Redis based on OS
    if command -v systemctl > /dev/null; then
        sudo systemctl start redis-server
    elif command -v brew > /dev/null; then
        brew services start redis
    else
        echo "Please start Redis manually"
        exit 1
    fi
fi

# Run migrations
echo "\n2. Running migrations..."
python manage.py migrate communication

# Check Redis connection
echo "\n3. Checking Redis connection..."
python manage.py check_redis

# Collect static files (production)
if [ "$DJANGO_SETTINGS_MODULE" = "kumss_erp.settings.production" ]; then
    echo "\n4. Collecting static files..."
    python manage.py collectstatic --noinput
fi

echo "\n========================================="
echo "Setup complete!"
echo "========================================="
echo "\nTo start the server, run:"
echo "  python manage.py runserver"
echo "\nOr with Daphne (recommended):"
echo "  daphne kumss_erp.asgi:application"
```

Make executable and run:
```bash
chmod +x setup.sh
./setup.sh
```

---

## Summary of Commands

### Development
```bash
# 1. Start Redis
redis-server  # or: sudo systemctl start redis-server

# 2. Check Redis
python manage.py check_redis

# 3. Run migrations
python manage.py migrate

# 4. Start Django
python manage.py runserver
```

### Production
```bash
# 1. Start Redis
sudo systemctl start redis-server

# 2. Collect static files
python manage.py collectstatic --noinput

# 3. Run migrations
python manage.py migrate

# 4. Start with Daphne
daphne -b 0.0.0.0 -p 8000 kumss_erp.asgi:application

# Or use systemd
sudo systemctl start kumss-backend
```

---

## Next Steps

1. ✅ Server running
2. ✅ Redis connected
3. 📖 Read [REALTIME_CHAT_API_DOCUMENTATION.md](./REALTIME_CHAT_API_DOCUMENTATION.md) for API details
4. 🚀 Integrate with React frontend (examples in documentation)
5. 🧪 Test SSE connection: http://localhost:8000/api/v1/communication/sse/test/
6. 📊 Monitor: http://localhost:8000/api/docs/

---

**Need Help?**
- Check Redis: `python manage.py check_redis`
- View logs: `tail -f logs/debug.log`
- API docs: http://localhost:8000/api/docs/
