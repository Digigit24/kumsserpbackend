#!/bin/bash
# Clear Python cache and restart Django

echo "Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

echo "Cache cleared!"
echo "Now restart Django server with: python manage.py runserver"
