"""
Management command to check Redis connection and provide setup instructions.
"""
import subprocess
import sys
import platform
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Check Redis connection and provide setup instructions'

    def handle(self, *args, **options):
        from apps.communication.redis_pubsub import RedisClient

        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Redis Connection Check'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        # Get Redis URL from settings
        redis_url = getattr(settings, 'REDIS_URL', 'redis://127.0.0.1:6379')
        self.stdout.write(f'\nRedis URL: {redis_url}\n')

        # Check connection
        redis_client = RedisClient()
        if redis_client.is_connected():
            self.stdout.write(self.style.SUCCESS('✓ Redis is connected and running!'))

            # Get Redis info
            try:
                client = redis_client.get_client()
                info = client.info()
                self.stdout.write(f"\nRedis Server Info:")
                self.stdout.write(f"  Version: {info.get('redis_version', 'Unknown')}")
                self.stdout.write(f"  Mode: {info.get('redis_mode', 'Unknown')}")
                self.stdout.write(f"  Connected clients: {info.get('connected_clients', 0)}")
                self.stdout.write(f"  Used memory: {info.get('used_memory_human', 'Unknown')}")
            except Exception as e:
                self.stdout.write(f"\nCould not get Redis info: {e}")

            self.stdout.write(self.style.SUCCESS('\n✓ Real-time messaging system is ready!'))
        else:
            self.stdout.write(self.style.ERROR('✗ Redis is NOT connected!'))
            self.stdout.write(self.style.WARNING('\nRedis is required for real-time messaging features.'))
            self._print_setup_instructions()

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))

    def _print_setup_instructions(self):
        """Print Redis setup instructions based on OS."""
        self.stdout.write(self.style.WARNING('\n' + '=' * 70))
        self.stdout.write(self.style.WARNING('Redis Setup Instructions'))
        self.stdout.write(self.style.WARNING('=' * 70))

        os_type = platform.system()

        if os_type == 'Windows':
            self.stdout.write(self.style.WARNING('''
Windows Setup Options:

Option 1: Using WSL (Windows Subsystem for Linux) - Recommended
1. Install WSL: wsl --install
2. Open WSL terminal
3. Install Redis:
   sudo apt-get update
   sudo apt-get install redis-server
4. Start Redis:
   sudo service redis-server start
5. Verify:
   redis-cli ping
   (Should return PONG)

Option 2: Using Docker
1. Install Docker Desktop for Windows
2. Run Redis container:
   docker run -d -p 6379:6379 --name redis redis:latest
3. Verify:
   docker ps
   (Should show redis container running)

Option 3: Using Memurai (Windows native Redis)
1. Download from: https://www.memurai.com/
2. Install and start the service
3. Redis will be available at localhost:6379
            '''))

        elif os_type == 'Linux':
            self.stdout.write(self.style.WARNING('''
Linux Setup:

Ubuntu/Debian:
1. Update package list:
   sudo apt-get update
2. Install Redis:
   sudo apt-get install redis-server
3. Start Redis:
   sudo systemctl start redis-server
4. Enable auto-start on boot:
   sudo systemctl enable redis-server
5. Verify:
   redis-cli ping
   (Should return PONG)

Using Docker (Alternative):
1. Install Docker
2. Run Redis container:
   docker run -d -p 6379:6379 --name redis redis:latest
            '''))

        elif os_type == 'Darwin':  # macOS
            self.stdout.write(self.style.WARNING('''
macOS Setup:

Option 1: Using Homebrew (Recommended)
1. Install Homebrew (if not installed):
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
2. Install Redis:
   brew install redis
3. Start Redis:
   brew services start redis
4. Verify:
   redis-cli ping
   (Should return PONG)

Option 2: Using Docker
1. Install Docker Desktop for Mac
2. Run Redis container:
   docker run -d -p 6379:6379 --name redis redis:latest
            '''))

        self.stdout.write(self.style.WARNING('''
After Installing Redis:

1. Make sure Redis is running:
   redis-cli ping
   (Should return PONG)

2. Set Redis URL in .env file:
   REDIS_URL=redis://127.0.0.1:6379

3. Run this check again:
   python manage.py check_redis

4. Start the Django server:
   python manage.py runserver
        '''))

        self.stdout.write(self.style.WARNING('=' * 70))
