# Windows Setup Guide

This guide helps you set up the WebSocket microservice on Windows.

## Prerequisites

### 1. Check PostgreSQL Installation

```powershell
# Check if PostgreSQL is running
Get-Service postgresql*

# If not installed, download from:
# https://www.postgresql.org/download/windows/
```

### 2. Check Redis Installation

```powershell
# Redis doesn't have an official Windows build
# Use WSL2 or Windows build from:
# https://github.com/microsoftarchive/redis/releases
```

**Alternative: Use Docker Desktop for Windows**
```powershell
# Install Docker Desktop from:
# https://www.docker.com/products/docker-desktop

# Start PostgreSQL
docker run -d --name postgres -e POSTGRES_PASSWORD=your_password -p 5432:5432 postgres:15

# Start Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

### 3. Check Node.js Installation

```powershell
node --version  # Should be >= 18
npm --version   # Should be >= 9
```

If not installed, download from: https://nodejs.org/

## Step-by-Step Setup

### Step 1: Configure Database Connection

1. **Find your PostgreSQL password:**
   - Open pgAdmin 4 (installed with PostgreSQL)
   - Or check your PostgreSQL installation notes

2. **Edit `.env` file in project root:**

Open `D:\kumsserpbackend\.env` in Notepad or VS Code and update:

```env
DATABASE_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD@localhost:5432/kumss_erp
```

Replace `YOUR_ACTUAL_PASSWORD` with your PostgreSQL password.

3. **Create the database:**

```powershell
# Open PowerShell as Administrator
psql -U postgres

# In psql:
CREATE DATABASE kumss_erp;
\q
```

If you don't have `psql` in PATH:
```powershell
# Find PostgreSQL bin directory (usually):
cd "C:\Program Files\PostgreSQL\15\bin"
.\psql.exe -U postgres

# Then create database
CREATE DATABASE kumss_erp;
\q
```

### Step 2: Run Database Migrations

```powershell
# In D:\kumsserpbackend
python manage.py migrate
```

### Step 3: Configure WebSocket Service

1. **Edit `websocket-service\.env`:**

Open `D:\kumsserpbackend\websocket-service\.env` and update:

```env
DB_PASSWORD=YOUR_ACTUAL_PASSWORD
```

2. **Install dependencies:**

```powershell
cd websocket-service
npm install
```

### Step 4: Start Redis

**Option A: Docker (Recommended)**
```powershell
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

**Option B: Windows Redis**
```powershell
# Download from: https://github.com/microsoftarchive/redis/releases
# Extract and run:
cd path\to\redis
.\redis-server.exe
```

**Option C: WSL2**
```powershell
# In WSL2
sudo service redis-server start
```

### Step 5: Start Services

**Terminal 1 - Django Backend:**
```powershell
# In D:\kumsserpbackend
python manage.py runserver
```

**Terminal 2 - WebSocket Service:**
```powershell
# In D:\kumsserpbackend\websocket-service
npm run dev
```

## Troubleshooting

### Issue 1: "password authentication failed for user postgres"

**Solution:**

1. **Find your PostgreSQL password:**
   ```powershell
   # It was set during PostgreSQL installation
   # Check these locations:
   # - Installation notes
   # - pgAdmin 4 saved connections
   # - Your password manager
   ```

2. **Reset PostgreSQL password (if forgotten):**
   ```powershell
   # Find pg_hba.conf (usually in):
   # C:\Program Files\PostgreSQL\15\data\pg_hba.conf

   # Open as Administrator and change:
   # FROM: host all all 127.0.0.1/32 scram-sha-256
   # TO:   host all all 127.0.0.1/32 trust

   # Restart PostgreSQL service:
   Restart-Service postgresql-x64-15

   # Connect without password:
   psql -U postgres

   # Reset password:
   ALTER USER postgres PASSWORD 'new_password';
   \q

   # Change pg_hba.conf back to scram-sha-256
   # Restart service again
   ```

3. **Update .env files with correct password**

### Issue 2: "Redis connection refused"

**Solution:**

```powershell
# Check if Redis is running:
docker ps | Select-String redis

# If not, start it:
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Test connection:
docker exec -it redis redis-cli ping
# Should return: PONG
```

### Issue 3: "Cannot find module 'express'"

**Solution:**
```powershell
cd websocket-service
npm install
```

### Issue 4: Port already in use

**Solution:**
```powershell
# Find process using port 3001:
netstat -ano | findstr :3001

# Kill the process (replace PID):
taskkill /PID <PID> /F

# Or use different port in .env:
PORT=3002
```

### Issue 5: "ECONNREFUSED" connecting to PostgreSQL

**Solution:**
```powershell
# Check PostgreSQL is running:
Get-Service postgresql*

# Start it if stopped:
Start-Service postgresql-x64-15

# Check it's listening on 5432:
netstat -an | findstr :5432
```

## Testing the Setup

### 1. Test Django Backend

```powershell
# Terminal 1
cd D:\kumsserpbackend
python manage.py runserver

# Should see:
# Starting development server at http://127.0.0.1:8000/
```

Open browser: http://localhost:8000/admin/

### 2. Test WebSocket Service

```powershell
# Terminal 2
cd D:\kumsserpbackend\websocket-service
npm run dev

# Should see:
# WebSocket server running on port 3001
```

Open browser: http://localhost:3001/health

Expected response:
```json
{
  "status": "ok",
  "service": "websocket-service",
  "timestamp": "2024-01-12T..."
}
```

### 3. Test Integration

```powershell
# In another terminal:
curl http://localhost:8000/api/v1/communication/ws/online-users/
```

## Using Docker Compose (Easiest)

If you have Docker Desktop installed:

```powershell
# In D:\kumsserpbackend\websocket-service
docker-compose up

# This starts:
# - PostgreSQL on port 5432
# - Redis on port 6379
# - WebSocket service on port 3001
```

Then in another terminal:
```powershell
# Update Django .env to use Docker PostgreSQL:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/kumss_erp

# Run migrations:
python manage.py migrate

# Start Django:
python manage.py runserver
```

## Quick Commands Reference

```powershell
# Check services
Get-Service postgresql*
docker ps

# Start services
Start-Service postgresql-x64-15
docker start redis

# Stop services
Stop-Service postgresql-x64-15
docker stop redis

# View logs
docker logs -f redis
docker logs -f postgres

# Test connections
psql -U postgres -d kumss_erp -c "SELECT 1"
docker exec -it redis redis-cli ping

# Kill process on port
netstat -ano | findstr :3001
taskkill /PID <PID> /F
```

## Environment File Templates

### Django `.env` (project root)
```env
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=kumss_erp.settings.development
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/kumss_erp
REDIS_URL=redis://127.0.0.1:6379
WEBSOCKET_SERVICE_URL=http://localhost:3001
ALLOWED_HOSTS=localhost,127.0.0.1
DEBUG=True
```

### WebSocket `.env` (websocket-service folder)
```env
NODE_ENV=development
PORT=3001
DB_HOST=localhost
DB_PORT=5432
DB_NAME=kumss_erp
DB_USER=postgres
DB_PASSWORD=YOUR_PASSWORD
REDIS_URL=redis://localhost:6379
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
LOG_LEVEL=debug
```

## Next Steps

After setup is complete:

1. **Create a superuser:**
   ```powershell
   python manage.py createsuperuser
   ```

2. **Access admin panel:**
   http://localhost:8000/admin/

3. **Test chat/notifications:**
   - See WEBSOCKET_MICROSERVICE_SETUP.md for frontend integration

## Need Help?

Common issues:
- PostgreSQL not starting → Restart service or reinstall
- Redis not working → Use Docker instead
- Port conflicts → Change ports in .env files
- Module not found → Run `npm install` again

For more help, check:
- websocket-service/README.md
- WEBSOCKET_MICROSERVICE_SETUP.md
