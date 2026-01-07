import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

from django.db import connection
from apps.store.models import MaterialIssueNote

# Database connection info
db = connection.settings_dict
print('\n' + '='*70)
print('DATABASE CONNECTION VERIFICATION')
print('='*70)
print(f'Engine:   {db["ENGINE"]}')
print(f'Host:     {db.get("HOST", "localhost")}')
print(f'Database: {db["NAME"]}')
print(f'User:     {db.get("USER", "N/A")}')
print('='*70)

# Verify it's PostgreSQL and get version
with connection.cursor() as cursor:
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    
    # Check if it's PostgreSQL (not SQLite)
    if 'PostgreSQL' in version:
        print(f'\n[OK] CONFIRMED: Connected to PostgreSQL')
        print(f'     Version: {version.split(" on ")[0]}')
        
        # Check if it's Neon
        if 'ep-muddy-bird' in db.get('HOST', ''):
            print(f'[OK] CONFIRMED: Using Neon PostgreSQL Database')
            print(f'     Host: {db.get("HOST", "")}')
        else:
            print(f'[WARNING] PostgreSQL but might not be Neon')
    else:
        print(f'\n[ERROR] Not using PostgreSQL!')
        print(f'        Currently using: {version}')

# Count Material Issue Notes
min_count = MaterialIssueNote.objects.count()
print(f'\n[OK] Material Issue Notes in database: {min_count}')

if min_count > 0:
    print(f'\nRecent Material Issue Notes:')
    for min_note in MaterialIssueNote.objects.order_by('-created_at')[:5]:
        print(f'  - {min_note.min_number} - Status: {min_note.status} - Date: {min_note.issue_date}')

print('\n' + '='*70)
if 'PostgreSQL' in version and 'ep-muddy-bird' in db.get('HOST', ''):
    print('VERDICT: Data IS being stored in NEON POSTGRESQL [OK]')
else:
    print('VERDICT: Data is NOT in Neon PostgreSQL [ERROR]')
print('='*70 + '\n')
