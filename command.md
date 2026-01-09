# Sequential Commands to Run Backend

Run this entire line in PowerShell to start everything at once:

```powershell
wsl -d Ubuntu -u root service redis-server start; python manage.py check_redis; python manage.py migrate; python manage.py runserver
```

# Individual Steps breakdown

1. **Start Redis (via WSL)**

   ```powershell
   wsl -d Ubuntu -u root service redis-server start
   ```

2. **Check Redis Connection**

   ```powershell
   python manage.py check_redis
   ```

3. **Run Migrations**

   ```powershell
   python manage.py migrate
   ```

4. **Start Django Server**
   ```powershell
   python manage.py runserver
   ```
