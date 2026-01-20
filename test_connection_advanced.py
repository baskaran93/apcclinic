from sqlalchemy import create_engine
from urllib.parse import quote_plus
import socket
import requests

DB_SERVER = "insightexpertz.database.windows.net"
DB_NAME = "APCDB"
DB_USERNAME = "saadmin"
DB_PASSWORD = quote_plus("Insight#123#@!")

# Print external IP to help user whitelist
try:
    ip = requests.get('https://api.ipify.org').text
    print(f"Your Public IP Address is: {ip}")
    print("Please ensure this IP is whitelisted in Azure SQL Server Firewall.")
except Exception as e:
    print("Could not determine public IP:", e)


DATABASE_URL_TRUST = (
    f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}:1433/{DB_NAME}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&Encrypt=yes"
    "&TrustServerCertificate=yes"
    "&Connection+Timeout=30"
)

print("\n--- Attempting connection with TrustServerCertificate=yes ---")
print("URL:", DATABASE_URL_TRUST)
engine = create_engine(DATABASE_URL_TRUST)
try:
    with engine.connect() as conn:
        print("Connected successfully with TrustServerCertificate=yes!")
except Exception as e:
    print("Connection failed even with TrustServerCertificate=yes")
    print("Error:", e)
