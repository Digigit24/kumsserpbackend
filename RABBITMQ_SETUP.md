# RabbitMQ Setup Guide - Quick Start

## 🚨 You're seeing 503 error because RabbitMQ is not running

The long polling system requires RabbitMQ to be installed and running. Here's how to set it up:

---

## ⚡ Quick Setup (Choose One)

### Option 1: Docker (Easiest - Recommended for Development)

```bash
# Pull and run RabbitMQ with management UI
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:management

# Wait 30 seconds for RabbitMQ to start, then test
python manage.py check_rabbitmq
```

**Advantages:**
- ✅ Works on Windows, Mac, Linux
- ✅ No installation needed (just Docker)
- ✅ Easy to start/stop
- ✅ Clean uninstall

**Management UI:** http://localhost:15672 (guest/guest)

---

### Option 2: Windows Installation (Native)

**Step 1: Install Erlang (Required Dependency)**

1. Download Erlang: https://www.erlang.org/downloads
2. Run installer (e.g., `otp_win64_26.2.1.exe`)
3. Use default settings
4. Verify: Open CMD and type `erl -version`

**Step 2: Install RabbitMQ**

1. Download RabbitMQ: https://www.rabbitmq.com/install-windows.html
2. Run installer (e.g., `rabbitmq-server-3.13.0.exe`)
3. RabbitMQ installs as Windows Service and starts automatically

**Step 3: Enable Management UI (Optional but Recommended)**

```cmd
cd "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.13.0\sbin"
rabbitmq-plugins enable rabbitmq_management
```

**Step 4: Verify Installation**

```bash
# Check Windows Service
sc query RabbitMQ

# Or use Django command
python manage.py check_rabbitmq
```

**Management UI:** http://localhost:15672 (guest/guest)

---

### Option 3: Linux Installation

#### Ubuntu/Debian

```bash
# Install RabbitMQ
sudo apt-get update
sudo apt-get install -y rabbitmq-server

# Start service
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

# Enable management plugin
sudo rabbitmq-plugins enable rabbitmq_management

# Test connection
python manage.py check_rabbitmq
```

#### CentOS/RHEL

```bash
# Install RabbitMQ
sudo yum install -y rabbitmq-server

# Start service
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

# Enable management
sudo rabbitmq-plugins enable rabbitmq_management

# Test
python manage.py check_rabbitmq
```

---

## 🧪 Testing Your Installation

### Test 1: Check RabbitMQ Service

**Windows:**
```cmd
# Check if service is running
sc query RabbitMQ

# Start service if stopped
net start RabbitMQ

# Restart service
net stop RabbitMQ
net start RabbitMQ
```

**Linux:**
```bash
# Check status
sudo systemctl status rabbitmq-server

# Start if stopped
sudo systemctl start rabbitmq-server

# Restart
sudo systemctl restart rabbitmq-server
```

**Docker:**
```bash
# Check if container is running
docker ps | grep rabbitmq

# Start if stopped
docker start rabbitmq

# View logs
docker logs rabbitmq
```

### Test 2: Django Management Command

```bash
python manage.py check_rabbitmq
```

**Expected Output (Success):**
```
✓ RabbitMQ connection successful
✓ RabbitMQ channel operational
✓ Queue operations working
✓ All RabbitMQ checks passed!
```

**If Failed:**
- Check RabbitMQ is running (see Test 1)
- Check port 5672 is not blocked by firewall
- Verify `RABBITMQ_URL` in your `.env` file

### Test 3: Management UI

1. Open browser: http://localhost:15672
2. Login: `guest` / `guest`
3. Should see RabbitMQ dashboard

### Test 4: Long Polling Endpoint

```bash
# Should return OK (not 503)
curl http://localhost:8000/api/v1/communication/poll/test/
```

---

## 🔧 Configuration

### .env File

Create or update your `.env` file:

```bash
# Add this line (or verify it exists)
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

### Django Settings

Already configured in `kumss_erp/settings/base.py`:

```python
RABBITMQ_URL = config('RABBITMQ_URL', default='amqp://guest:guest@localhost:5672/')
```

---

## 🐛 Troubleshooting

### Issue: 503 Service Unavailable

**Cause:** RabbitMQ not running or not accessible

**Solutions:**

1. **Start RabbitMQ:**
   ```bash
   # Windows
   net start RabbitMQ

   # Linux
   sudo systemctl start rabbitmq-server

   # Docker
   docker start rabbitmq
   ```

2. **Check Logs:**
   ```bash
   # Windows
   # Logs at: C:\Users\<username>\AppData\Roaming\RabbitMQ\log\

   # Linux
   sudo tail -f /var/log/rabbitmq/rabbit@hostname.log

   # Docker
   docker logs rabbitmq
   ```

3. **Check Port:**
   ```bash
   # Windows
   netstat -an | findstr :5672

   # Linux
   netstat -tuln | grep 5672
   ```

### Issue: Connection Refused

**Cause:** Firewall blocking port 5672

**Solution:**
```bash
# Windows Firewall
netsh advfirewall firewall add rule name="RabbitMQ" dir=in action=allow protocol=TCP localport=5672

# Linux (UFW)
sudo ufw allow 5672/tcp
sudo ufw allow 15672/tcp
```

### Issue: Erlang Not Found (Windows)

**Cause:** Erlang not installed (required for RabbitMQ)

**Solution:**
1. Download Erlang: https://www.erlang.org/downloads
2. Install with default settings
3. Reinstall RabbitMQ

### Issue: Module 'pika' not found

**Cause:** Python package not installed

**Solution:**
```bash
pip install pika==1.3.2

# Or install all requirements
pip install -r requirements.txt
```

---

## 🚀 Quick Start Commands

### After Installing RabbitMQ:

```bash
# 1. Start RabbitMQ (if not running)
# Windows: net start RabbitMQ
# Linux: sudo systemctl start rabbitmq-server
# Docker: docker start rabbitmq

# 2. Install Python package
pip install pika==1.3.2

# 3. Create/update .env file
echo "RABBITMQ_URL=amqp://guest:guest@localhost:5672/" >> .env

# 4. Test connection
python manage.py check_rabbitmq

# 5. Start Django
python manage.py runserver

# 6. Test endpoint
curl http://localhost:8000/api/v1/communication/poll/test/
```

---

## 📊 Verifying Everything Works

### Checklist:

- [ ] RabbitMQ installed
- [ ] RabbitMQ service running
- [ ] Management UI accessible at http://localhost:15672
- [ ] `pika` Python package installed
- [ ] `RABBITMQ_URL` in `.env` file
- [ ] `python manage.py check_rabbitmq` passes
- [ ] Poll test endpoint returns 200 OK
- [ ] No more 503 errors

### Expected Behavior:

**Before RabbitMQ:**
```
GET /api/v1/communication/poll/events/
→ 503 Service Unavailable
```

**After RabbitMQ Running:**
```
GET /api/v1/communication/poll/events/
→ 200 OK
→ {"events": [], "timestamp": 1234567890}
```

---

## 💡 Recommended Setup for Development

**Using Docker (Simplest):**

```bash
# Start RabbitMQ
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  --restart unless-stopped \
  rabbitmq:management

# Install Python package
pip install pika==1.3.2

# Test
python manage.py check_rabbitmq

# Done! Now start Django
python manage.py runserver
```

**Benefits:**
- No system installation needed
- Works on all platforms
- Easy to reset (just delete container)
- Auto-restarts on boot

---

## 🎯 Next Steps After Setup

Once RabbitMQ is running:

1. ✅ `python manage.py check_rabbitmq` shows success
2. ✅ Start Django: `python manage.py runserver`
3. ✅ Test endpoint: `curl http://localhost:8000/api/v1/communication/poll/test/`
4. ✅ Frontend can now connect to `/api/v1/communication/poll/events/`
5. ✅ Real-time features (chat, notifications) will work

---

## 📞 Still Having Issues?

1. **Check the checklist above** - make sure all items are ✅
2. **Run diagnostics:**
   ```bash
   python manage.py check_rabbitmq
   ```
3. **Check Django logs** for specific error messages
4. **View RabbitMQ logs** (locations listed in troubleshooting)
5. **Try Docker option** if native installation fails

---

## 🔗 Useful Links

- RabbitMQ Windows: https://www.rabbitmq.com/install-windows.html
- RabbitMQ Linux: https://www.rabbitmq.com/install-debian.html
- Docker Image: https://hub.docker.com/_/rabbitmq
- Management UI Guide: https://www.rabbitmq.com/management.html

---

## 📝 Alternative: Fallback Mode (Temporary)

If you need to continue development without RabbitMQ temporarily, you can use fallback mode (real-time features will be disabled):

**Not recommended for production - install RabbitMQ instead**

See `apps/communication/fallback_views.py` for temporary solution.
