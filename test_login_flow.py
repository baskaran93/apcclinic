import requests
import json

# Railway Production URL
BASE_URL = "https://helpful-presence-production-4bdd.up.railway.app"

def test_login_flow():
    """Complete login flow test"""
    print("\n" + "=" * 70)
    print("APC CLINIC - LOGIN FLOW TEST")
    print("=" * 70)

    # Step 1: Check health
    print("\n[Step 1] Checking API Health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        print("✅ API is healthy")
    except Exception as e:
        print(f"❌ API health check failed: {e}")
        return False

    # Step 2: Check DB health
    print("[Step 2] Checking Database Connection...")
    try:
        response = requests.get(f"{BASE_URL}/health/db")
        assert response.status_code == 200
        assert "connected" in response.json().get("status", "").lower()
        print("✅ Database is connected")
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

    # Step 3: Attempt login
    print("[Step 3] Attempting Login...")
    login_url = f"{BASE_URL}/user/login/"
    payload = {
        "username": "testuser",
        "password_hash": "pass123",
        "role": "admin"
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        print(f"  Sending request to: {login_url}")
        print(f"  Credentials: {payload['username']}")
        response = requests.post(login_url, json=payload, headers=headers)
        print(f"  Status Code: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Login failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False

        data = response.json()
        print(f"✅ Login successful")
        print(f"  Message: {data.get('message')}")
        print(f"  Role: {data.get('role')}")

        token = data.get('access_token')
        if not token:
            print("❌ No access token received")
            return False

        print(f"  Token: {token[:50]}...")

        # Step 4: Use token to access protected endpoint
        print("[Step 4] Accessing Protected Endpoint with Token...")
        user_list_url = f"{BASE_URL}/user/list/"
        auth_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.get(user_list_url, headers=auth_headers)
        print(f"  Status Code: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Failed to access protected endpoint")
            print(f"  Response: {response.text}")
            return False

        data = response.json()
        users = data.get('data', [])
        print(f"✅ Successfully accessed protected endpoint")
        print(f"  Retrieved {len(users)} users")
        print(f"  Users: {', '.join([u['username'] for u in users[:5]])}")

        # Step 5: Summary
        print("\n" + "=" * 70)
        print("LOGIN FLOW TEST RESULTS")
        print("=" * 70)
        print("✅ Health Check: PASSED")
        print("✅ Database Check: PASSED")
        print("✅ Login: PASSED")
        print("✅ Protected Endpoint Access: PASSED")
        print("=" * 70)
        print("🎉 All tests passed! API is fully functional.\n")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_login_flow()
    exit(0 if success else 1)
