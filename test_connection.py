from sqlalchemy import create_engine
from urllib.parse import quote_plus

DB_SERVER = "insightexpertz.database.windows.net"
DB_NAME = "APCDB"
DB_USERNAME = "saadmin"
DB_PASSWORD = quote_plus("Insight#123#@!")

DATABASE_URL = (
    f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}:1433/{DB_NAME}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&Encrypt=yes"
    "&TrustServerCertificate=no"
    "&Connection+Timeout=30"
)

print("URL:", DATABASE_URL)
engine = create_engine(DATABASE_URL)
try:
    with engine.connect() as conn:
        print("Connected!")
except Exception as e:
    print("Error:", e)
