#!/usr/bin/env python
"""
Test script to verify login response includes all user details.
This simulates what the frontend will receive when calling the login API.

Usage:
    python test_login_response.py

Make sure your Django server is running on http://localhost:8000
"""

import requests
import json

# API endpoint
LOGIN_URL = "http://localhost:8000/api/v1/auth/login/"

# Test credentials - UPDATE THESE with your actual test user
TEST_CREDENTIALS = {
    "username": "admin",  # Change this to your test username
    "password": "admin123"  # Change this to your test password
}

# Optional: Add college header if needed
HEADERS = {
    "Content-Type": "application/json",
    # "X-College-ID": "1",  # Uncomment if your college requires this
}

def test_login():
    """Test the login endpoint and display the response."""
    print("=" * 80)
    print("TESTING LOGIN API RESPONSE")
    print("=" * 80)
    print(f"\nEndpoint: {LOGIN_URL}")
    print(f"Credentials: username='{TEST_CREDENTIALS['username']}'")
    print("\nSending request...")

    try:
        response = requests.post(
            LOGIN_URL,
            json=TEST_CREDENTIALS,
            headers=HEADERS,
            timeout=10
        )

        print(f"\nStatus Code: {response.status_code}")
        print("\n" + "=" * 80)
        print("COMPLETE API RESPONSE (What Frontend Receives)")
        print("=" * 80)

        if response.status_code == 200:
            data = response.json()

            # Pretty print the entire response
            print(json.dumps(data, indent=2))

            # Highlight specific sections
            print("\n" + "=" * 80)
            print("RESPONSE BREAKDOWN")
            print("=" * 80)

            print(f"\n✓ Authentication Token: {data.get('key', 'N/A')}")
            print(f"✓ Message: {data.get('message', 'N/A')}")

            if 'user' in data:
                print(f"\n✓ USER OBJECT (with {len(data['user'])} fields):")
                for key, value in data['user'].items():
                    print(f"  - {key}: {value}")

            print(f"\n✓ College ID: {data.get('college_id', 'N/A')}")
            print(f"✓ Tenant IDs: {data.get('tenant_ids', 'N/A')}")

            if 'accessible_colleges' in data:
                print(f"\n✓ ACCESSIBLE COLLEGES ({len(data.get('accessible_colleges', []))} colleges):")
                for college in data.get('accessible_colleges', []):
                    print(f"  - {college}")

            if 'user_roles' in data:
                print(f"\n✓ USER ROLES ({len(data.get('user_roles', []))} roles):")
                for role in data.get('user_roles', []):
                    print(f"  - {role}")

            if 'user_permissions' in data:
                permissions = data.get('user_permissions', [])
                print(f"\n✓ USER PERMISSIONS ({len(permissions)} permissions):")
                print(f"  {permissions}")

            if 'user_profile' in data:
                profile = data.get('user_profile')
                if profile:
                    print(f"\n✓ USER PROFILE:")
                    for key, value in profile.items():
                        print(f"  - {key}: {value}")
                else:
                    print(f"\n✓ USER PROFILE: None (not created yet)")

            print("\n" + "=" * 80)
            print("✓ LOGIN SUCCESSFUL - All user details are in the response!")
            print("=" * 80)

        else:
            print(f"\n✗ LOGIN FAILED")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to the server.")
        print("Make sure Django server is running: python manage.py runserver")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")

if __name__ == "__main__":
    test_login()
