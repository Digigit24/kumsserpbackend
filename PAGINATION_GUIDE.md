# API Pagination Guide

## Response Format

All paginated endpoints return:

```json
{
  "count": 100,
  "total_pages": 5,
  "current_page": 1,
  "page_size": 20,
  "next": "http://api.example.com/endpoint/?page=2",
  "previous": null,
  "has_next": true,
  "has_previous": false,
  "results": [...]
}
```

## Query Parameters

- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

## Examples

```javascript
// Fetch page 2 with 50 items
fetch('/api/v1/endpoint/?page=2&page_size=50')

// Default (page 1, 20 items)
fetch('/api/v1/endpoint/')
```

## React Example

```javascript
const [data, setData] = useState({ results: [], count: 0 });
const [page, setPage] = useState(1);

useEffect(() => {
  fetch(`/api/v1/endpoint/?page=${page}`)
    .then(res => res.json())
    .then(data => setData(data));
}, [page]);

// Use data.total_pages for pagination controls
// Use data.has_next, data.has_previous for navigation
```
