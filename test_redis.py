#!/usr/bin/env python
"""
Test Redis connection for WebSocket support
"""
import redis
import os
from decouple import config

def test_redis_connection():
    """Test connection to Redis server"""
    print("=== Testing Redis Connection ===\n")
    
    # Get Redis URL from environment
    redis_url = config('REDIS_URL', default='redis://127.0.0.1:6379')
    print(f"Redis URL: {redis_url}\n")
    
    try:
        # Connect to Redis
        print("Connecting to Redis...")
        r = redis.from_url(redis_url)
        
        # Test ping
        print("Sending PING...")
        response = r.ping()
        print(f"✅ PING response: {response}")
        
        # Test set/get
        print("\nTesting SET/GET operations...")
        r.set('test_key', 'Hello from Django!')
        value = r.get('test_key')
        print(f"✅ SET/GET successful: {value.decode('utf-8')}")
        
        # Clean up
        r.delete('test_key')
        
        # Get server info
        print("\nRedis Server Info:")
        info = r.info('server')
        print(f"  Redis Version: {info.get('redis_version')}")
        print(f"  OS: {info.get('os')}")
        print(f"  Process ID: {info.get('process_id')}")
        
        print("\n✅ Redis is working correctly!")
        print("✅ WebSockets will work without additional configuration.")
        return True
        
    except redis.ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check if Redis is running in WSL:")
        print("   wsl -d Ubuntu -e redis-cli ping")
        print("\n2. Start Redis server in WSL:")
        print("   wsl -d Ubuntu -e sudo service redis-server start")
        print("\n3. If Redis is not installed in WSL:")
        print("   wsl -d Ubuntu -e sudo apt-get update")
        print("   wsl -d Ubuntu -e sudo apt-get install redis-server")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    test_redis_connection()
