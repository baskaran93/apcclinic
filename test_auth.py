import requests
import json

# Railway Production URL
BASE_URL = "https://helpful-presence-production-4bdd.up.railway.app"

def test_health():
    """Test health endpoint"""
    url = f"{BASE_URL}/health"
    print("=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert response.json().get("status") == "ok"
        print("✅ PASSED\n")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        return False

def test_db_health():
    """Test database health endpoint"""
    url = f"{BASE_URL}/health/db"
    print("=" * 60)
    print("Testing Database Health Endpoint")
    print("=" * 60)
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert "connected" in response.json().get("status", "").lower()
        print("✅ PASSED\n")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        return False

def test_login_valid():
    """Test login with valid credentials"""
    url = f"{BASE_URL}/user/login/"
    payload = {
        "username": "testuser",
        "password_hash": "pass123",
        "role": "admin"
    }
    print("=" * 60)
    print(f"Testing Login with Valid Credentials")
    print("=" * 60)
    print(f"Username: {payload['username']}")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        assert response.status_code == 200
        assert "access_token" in data
        assert data.get("role") == "admin"
        print("✅ PASSED\n")
        return data.get("access_token")
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        return None

def test_login_invalid():
    """Test login with invalid credentials"""
    url = f"{BASE_URL}/user/login/"
    payload = {
        "username": "invaliduser",
        "password_hash": "wrongpassword",
        "role": "admin"
    }
    print("=" * 60)
    print("Testing Login with Invalid Credentials")
    print("=" * 60)
    print(f"Username: {payload['username']}")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 400
        print("✅ PASSED (Correctly rejected invalid credentials)\n")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        return False

def test_user_list_without_auth():
    """Test accessing protected endpoint without token"""
    url = f"{BASE_URL}/user/list/"
    print("=" * 60)
    print("Testing User List WITHOUT Authentication")
    print("=" * 60)
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 401
        print("✅ PASSED (Correctly rejected unauthenticated request)\n")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        return False

def test_user_list_with_auth(token):
    """Test accessing protected endpoint with valid token"""
    url = f"{BASE_URL}/user/list/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    print("=" * 60)
    print("Testing User List WITH Authentication")
    print("=" * 60)
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)[:500]}...")
        assert response.status_code == 200
        assert data.get("status") == "success"
        assert len(data.get("data", [])) > 0
        print(f"✅ PASSED (Retrieved {len(data.get('data', []))} users)\n")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("APC CLINIC API - AUTHENTICATION TEST SUITE")
    print("Base URL: " + BASE_URL)
    print("=" * 60 + "\n")

    results = []

    results.append(("Health Check", test_health()))
    results.append(("DB Health Check", test_db_health()))
    results.append(("Invalid Login", test_login_invalid()))

    token = test_login_valid()
    results.append(("Valid Login", token is not None))

    results.append(("User List (No Auth)", test_user_list_without_auth()))

    if token:
        results.append(("User List (With Auth)", test_user_list_with_auth(token)))

    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    print("=" * 60)
