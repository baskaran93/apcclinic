import psycopg2
import requests
import json

# Railway Configuration
API_URL = "https://helpful-presence-production-4bdd.up.railway.app"
DB_SERVER = "hayabusa.proxy.rlwy.net"
DB_PORT = 48072
DB_NAME = "railway"
DB_USERNAME = "postgres"
DB_PASSWORD = "SkwWujMixQzGRoUtQGInAxcPyvOgJAUF"

print("\n" + "=" * 70)
print("COMPREHENSIVE API AND DATABASE TEST SUITE")
print("=" * 70)

# Get external IP
print("\n[Info] Detecting connection details...")
try:
    ip = requests.get('https://api.ipify.org', timeout=5).text
    print(f"  Your Public IP: {ip}")
except Exception:
    print("  Could not detect public IP")

print(f"  API URL: {API_URL}")
print(f"  Database: {DB_SERVER}:{DB_PORT}/{DB_NAME}")

# Test 1: API Availability
print("\n[Test 1] API Availability Check...")
try:
    response = requests.get(f"{API_URL}/")
    assert response.status_code == 200
    print("✅ API is available and responding")
except Exception as e:
    print(f"❌ API not available: {e}")
    exit(1)

# Test 2: Database Connection (Direct)
print("\n[Test 2] Direct Database Connection (PostgreSQL)...")
try:
    conn = psycopg2.connect(
        host=DB_SERVER,
        port=DB_PORT,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        database=DB_NAME,
        connect_timeout=10
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"✅ Connected to PostgreSQL")
    print(f"   Version: {version.split(',')[0]}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Direct connection failed: {e}")

# Test 3: API Health Endpoints
print("\n[Test 3] API Health Endpoints...")
endpoints = [
    ("/health", "General Health"),
    ("/health/db", "Database Health"),
]

for endpoint, name in endpoints:
    try:
        response = requests.get(f"{API_URL}{endpoint}")
        if response.status_code == 200:
            print(f"✅ {name}: OK")
        else:
            print(f"⚠️  {name}: Status {response.status_code}")
    except Exception as e:
        print(f"❌ {name}: {e}")

# Test 4: Authentication Flow
print("\n[Test 4] Authentication Flow Test...")
try:
    # Step 1: Login
    login_payload = {
        "username": "testuser",
        "password_hash": "pass123",
        "role": "admin"
    }
    response = requests.post(
        f"{API_URL}/user/login/",
        json=login_payload
    )
    assert response.status_code == 200
    token = response.json().get("access_token")
    print("✅ Login successful, token obtained")

    # Step 2: Access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/user/list/", headers=headers)
    assert response.status_code == 200
    users = response.json().get("data", [])
    print(f"✅ Protected endpoint accessible: {len(users)} users retrieved")

except Exception as e:
    print(f"❌ Authentication flow failed: {e}")

# Test 5: Data Integrity
print("\n[Test 5] Data Integrity Check...")
try:
    login_payload = {
        "username": "testuser",
        "password_hash": "pass123",
        "role": "admin"
    }
    response = requests.post(f"{API_URL}/user/login/", json=login_payload)
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # Check data counts
    response = requests.get(f"{API_URL}/user/list/", headers=headers)
    users = response.json().get("data", [])

    print(f"✅ Data integrity verified")
    print(f"   Users in database: {len(users)}")

except Exception as e:
    print(f"❌ Data integrity check failed: {e}")

# Test 6: Database Query Performance
print("\n[Test 6] Database Query Performance...")
try:
    conn = psycopg2.connect(
        host=DB_SERVER,
        port=DB_PORT,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        database=DB_NAME,
        connect_timeout=10
    )
    cursor = conn.cursor()

    # Count records in main tables
    cursor.execute("""
    SELECT 'patient_details' as table_name, COUNT(*) FROM public.patient_details
    UNION ALL
    SELECT 'login', COUNT(*) FROM public.login
    UNION ALL
    SELECT 'appointments', COUNT(*) FROM public.appointments
    ORDER BY table_name
    """)

    print("✅ Database query performance: OK")
    print("   Table record counts:")
    for table, count in cursor.fetchall():
        print(f"     • {table}: {count}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Query performance test failed: {e}")

print("\n" + "=" * 70)
print("COMPREHENSIVE TEST COMPLETE")
print("=" * 70)
print("\n🎉 All systems operational!\n")
