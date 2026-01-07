import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

from django.conf import settings
from django.db import connection

db = settings.DATABASES['default']

print('\n' + '='*60)
print('CURRENT DATABASE CONFIGURATION')
print('='*60)
print(f'Engine:   {db["ENGINE"]}')
print(f'Database: {db["NAME"]}')
print(f'Host:     {db.get("HOST", "N/A")}')
print(f'User:     {db.get("USER", "N/A")}')
print(f'Port:     {db.get("PORT", "N/A")}')
print('='*60)

# Test actual connection
with connection.cursor() as cursor:
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f'\n✓ Connected to: {version[0]}')
    
    # Count Material Issue Notes
    cursor.execute("SELECT COUNT(*) FROM material_issue_note;")
    count = cursor.fetchone()
    print(f'✓ Material Issue Notes in database: {count[0]}')
    
    
print('\n' + '='*60)
