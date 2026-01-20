import requests
import json

BASE_URL = "http://127.0.0.1:3000"

def test_register():
    url = f"{BASE_URL}/user/register/"
    payload = {
        "username": "test_user_ag_1",
        "password_hash": "securepassword123"
    }
    print(f"Testing Register with: {payload}")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Register Failed: {e}")

def test_login():
    url = f"{BASE_URL}/user/login/"
    payload = {
        "username": "test_user_ag_1",
        "password_hash": "securepassword123"
    }
    print(f"\nTesting Login with: {payload}")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Login Failed: {e}")

if __name__ == "__main__":
    test_register()
    test_login()
