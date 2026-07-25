import psycopg2
import requests
import json

# Railway PostgreSQL Connection Details
DB_SERVER = "hayabusa.proxy.rlwy.net"
DB_PORT = 48072
DB_NAME = "railway"
DB_USERNAME = "postgres"
DB_PASSWORD = "SkwWujMixQzGRoUtQGInAxcPyvOgJAUF"

# Railway API
API_URL = "https://helpful-presence-production-4bdd.up.railway.app"

print("\n" + "=" * 70)
print("RAILWAY POSTGRESQL CONNECTION TEST")
print("=" * 70)

print(f"\nDatabase Server: {DB_SERVER}:{DB_PORT}")
print(f"Database Name: {DB_NAME}")
print(f"Username: {DB_USERNAME}")

# Test 1: Direct PostgreSQL connection
print("\n[Test 1] Direct Database Connection...")
try:
    conn = psycopg2.connect(
        host=DB_SERVER,
        port=DB_PORT,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()

    # Check table counts
    cursor.execute("""
    SELECT
        'patient_details' as table_name, COUNT(*) FROM public.patient_details
    UNION ALL
    SELECT 'login', COUNT(*) FROM public.login
    UNION ALL
    SELECT 'appointments', COUNT(*) FROM public.appointments
    """)

    results = cursor.fetchall()
    print("✅ Connected to PostgreSQL successfully!")
    print("   Table contents:")
    for table, count in results:
        print(f"     • {table}: {count} records")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Direct connection failed: {e}")

# Test 2: API Health Check
print("\n[Test 2] API Health Check...")
try:
    response = requests.get(f"{API_URL}/health")
    assert response.status_code == 200
    print("✅ API is healthy")
except Exception as e:
    print(f"❌ API health check failed: {e}")

# Test 3: API Database Health
print("\n[Test 3] API Database Health Check...")
try:
    response = requests.get(f"{API_URL}/health/db")
    assert response.status_code == 200
    data = response.json()
    assert "connected" in data.get("status", "").lower()
    print("✅ Database is connected via API")
except Exception as e:
    print(f"❌ Database health check failed: {e}")

print("\n" + "=" * 70 + "\n")
