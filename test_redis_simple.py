import redis
import time

print("Testing Redis connection...")
print("Attempting to connect to redis://127.0.0.1:6379")

try:
    # Try with explicit timeout
    r = redis.Redis(
        host='127.0.0.1',
        port=6379,
        db=0,
        socket_connect_timeout=5,
        socket_timeout=5,
        decode_responses=True
    )
    
    print("\nConnection object created, testing ping...")
    result = r.ping()
    print(f"✅ SUCCESS! Redis responded with: {result}")
    
    # Test actual operations
    r.set('test', 'Hello Django WebSockets!')
    value = r.get('test')
    print(f"✅ Read/Write test successful: {value}")
    
    # Clean up
    r.delete('test')
    
    print("\n🎉 Redis is working perfectly!")
    print("✅ Your WebSockets will work correctly!")
    
except redis.ConnectionError as e:
    print(f"\n❌ Connection failed: {e}")
    print("\nPossible issues:")
    print("1. Redis might be protected/password required")
    print("2. Firewall blocking connection")
    print("3. Redis not accepting connections from 127.0.0.1")
    
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
