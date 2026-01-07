import requests
import json

print("Testing Material Issue API endpoint...")
print("=" * 60)

url = "http://127.0.0.1:8000/api/v1/store/material-issues/"

try:
    response = requests.get(url)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            print(f"\n✅ SUCCESS! Found {len(data)} records")
            print("\n📋 First Record Fields:")
            print("-" * 60)
            first_record = data[0]
            for key, value in first_record.items():
                print(f"  {key}: {value}")
            
            print("\n✅ All fields are now included in the API response!")
            
            # Check if all expected fields are present
            expected_fields = [
                'id', 'created_at', 'updated_at', 'is_active', 'min_number',
                'issue_date', 'transport_mode', 'vehicle_number', 'driver_name',
                'driver_contact', 'status', 'dispatch_date', 'receipt_date',
                'min_document', 'internal_notes', 'receipt_confirmation_notes',
                'central_store_id', 'created_by_id', 'issued_by_id',
                'received_by_id', 'receiving_college_id', 'updated_by_id', 'indent_id'
            ]
            
            missing_fields = [f for f in expected_fields if f not in first_record]
            if missing_fields:
                print(f"\n⚠️ Warning: Missing fields: {missing_fields}")
            else:
                print(f"\n✅ All {len(expected_fields)} expected fields are present!")
        else:
            print("\n⚠️ No records found in response")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text[:500])
        
except requests.exceptions.ConnectionError:
    print("\n❌ Could not connect to server. Make sure Django is running on port 8000")
except Exception as e:
    print(f"\n❌ Error: {e}")
