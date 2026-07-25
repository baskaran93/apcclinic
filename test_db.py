import requests
import json

# Railway Production URL
BASE_URL = "https://helpful-presence-production-4bdd.up.railway.app"

def test_database_health():
    """Test database connection through API"""
    print("\n" + "=" * 70)
    print("DATABASE CONNECTION TEST")
    print("=" * 70)

    url = f"{BASE_URL}/health/db"
    print(f"\nTesting: {url}")

    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")

        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")

        if response.status_code == 200:
            status = data.get("status", "")
            if "connected" in status.lower():
                print("\n✅ DATABASE CONNECTION: SUCCESS")
                print("   Database is online and accessible")
                return True
            else:
                print("\n❌ DATABASE CONNECTION: FAILED")
                print(f"   Status: {status}")
                return False
        else:
            print("\n❌ DATABASE CONNECTION: FAILED")
            print(f"   HTTP Error {response.status_code}")
            return False

    except Exception as e:
        print(f"\n❌ DATABASE CONNECTION: FAILED")
        print(f"   Error: {e}")
        return False

def test_data_availability():
    """Test that data is available in database"""
    print("\n" + "=" * 70)
    print("DATA AVAILABILITY TEST")
    print("=" * 70)

    # Get auth token first
    login_url = f"{BASE_URL}/user/login/"
    login_payload = {
        "username": "testuser",
        "password_hash": "pass123",
        "role": "admin"
    }

    print("\nGetting authentication token...")
    try:
        response = requests.post(login_url, json=login_payload)
        if response.status_code != 200:
            print("❌ Could not authenticate")
            return False

        token = response.json().get("access_token")
        print("✅ Authentication successful")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

    # Test user list endpoint
    print("\nFetching user data...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/user/list/", headers=headers)
        if response.status_code != 200:
            print("❌ Could not fetch user data")
            return False

        data = response.json()
        users = data.get("data", [])
        print(f"✅ Retrieved {len(users)} user records")
        print(f"   Users: {', '.join([u['username'] for u in users[:3]])}")

        if len(users) > 0:
            print("\n✅ DATA AVAILABILITY: SUCCESS")
            return True
        else:
            print("\n❌ DATA AVAILABILITY: FAILED - No data found")
            return False

    except Exception as e:
        print(f"\n❌ DATA AVAILABILITY: FAILED")
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    print("\nAPC CLINIC API - DATABASE TEST")
    print(f"Base URL: {BASE_URL}")

    db_health = test_database_health()
    data_avail = test_data_availability()

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Database Health: {'✅ PASS' if db_health else '❌ FAIL'}")
    print(f"Data Available: {'✅ PASS' if data_avail else '❌ FAIL'}")
    print("=" * 70 + "\n")

    exit(0 if (db_health and data_avail) else 1)
