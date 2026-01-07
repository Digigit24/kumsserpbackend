#!/usr/bin/env python
import psycopg2
from decouple import config

# Get database URL from .env
db_url = config('DATABASE_URL')

print("=" * 70)
print("Checking material_issue_note table directly")
print("=" * 70)

try:
    # Parse DATABASE_URL
    # Format: postgresql://user:password@host:port/database
    import re
    pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
    match = re.match(pattern, db_url)
    
    if match:
        user, password, host, port, database = match.groups()
        
        # Connect to database
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        cursor = conn.cursor()
        
        # Count total records
        cursor.execute("SELECT COUNT(*) FROM material_issue_note")
        count = cursor.fetchone()[0]
        print(f"\n✅ Total records in material_issue_note: {count}")
        
        if count > 0:
            # Get sample records
            cursor.execute("""
                SELECT id, min_number, status, issue_date, receiving_college_id, 
                       central_store_id, indent_id
                FROM material_issue_note
                ORDER BY id DESC
                LIMIT 5
            """)
            
            print("\n📋 Sample Records:")
            print("-" * 70)
            for row in cursor.fetchall():
                print(f"ID: {row[0]}, MIN: {row[1]}, Status: {row[2]}, "
                      f"Date: {row[3]}, College: {row[4]}, Store: {row[5]}, Indent: {row[6]}")
            
            # Status distribution
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM material_issue_note 
                GROUP BY status
            """)
            print("\n📊 Status Distribution:")
            print("-" * 70)
            for row in cursor.fetchall():
                print(f"  {row[0]}: {row[1]} records")
            
            # College distribution
            cursor.execute("""
                SELECT receiving_college_id, COUNT(*) 
                FROM material_issue_note 
                GROUP BY receiving_college_id
            """)
            print("\n🏢 College Distribution:")
            print("-" * 70)
            for row in cursor.fetchall():
                print(f"  College ID {row[0]}: {row[1]} records")
        else:
            print("\n⚠️ No records found!")
            print("\nTo seed data, run: python manage.py seed_material_issues")
        
        cursor.close()
        conn.close()
        
    else:
        print("❌ Could not parse DATABASE_URL")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
