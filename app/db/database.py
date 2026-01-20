import os
import urllib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Fetch environment variables
DB_SERVER = os.getenv("DB_SERVER", "insightexpertz.database.windows.net")
DB_NAME = os.getenv("DB_NAME", "APCDB")
DB_USERNAME = os.getenv("DB_USERNAME", "saadmin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Insight#123#@!")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

# Build connection string
# Azure SQL usually requires standard connection string format
connection_string = (
    f"DRIVER={{{DB_DRIVER}}};"
    f"SERVER={DB_SERVER},1433;"
    f"DATABASE={DB_NAME};"
    f"UID={DB_USERNAME};"
    f"PWD={DB_PASSWORD};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

# Encode for SQLAlchemy
params = urllib.parse.quote_plus(connection_string)
DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
