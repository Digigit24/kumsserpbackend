# API Compression Guide

## Backend Configuration

All API responses are **automatically compressed using GZip** compression.

- **Middleware**: `django.middleware.gzip.GZipMiddleware`
- **Min Size**: 0 bytes (compresses all responses)

---

## Frontend Integration

### 1. Fetch API (JavaScript)

```javascript
fetch('http://127.0.0.1:8000/api/v1/endpoint', {
  headers: {
    'Accept-Encoding': 'gzip, deflate, br'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

### 2. Axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
  headers: {
    'Accept-Encoding': 'gzip, deflate, br'
  }
});

// Use normally
api.get('/endpoint').then(response => console.log(response.data));
```

### 3. React Query

```javascript
import { useQuery } from '@tanstack/react-query';

const fetchData = async () => {
  const response = await fetch('http://127.0.0.1:8000/api/v1/endpoint', {
    headers: { 'Accept-Encoding': 'gzip, deflate, br' }
  });
  return response.json();
};

const { data } = useQuery(['key'], fetchData);
```

---

## Browser Behavior

Modern browsers **automatically**:
- Send `Accept-Encoding: gzip, deflate, br` header
- Decompress gzip responses

**No manual decompression needed** - browsers handle it natively.

---

## Benefits

- ⚡ Faster response times
- 📉 Reduced bandwidth usage (60-80% smaller payloads)
- 💰 Lower data costs for mobile users

---

## Verification

Check response headers in DevTools:

```
Content-Encoding: gzip
```

If present, compression is active.
