import os
import urllib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # SQLAlchemy requires postgresql:// instead of postgres://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print(f"[DEBUG] Database config loaded: Using DATABASE_URL (PostgreSQL)")
else:
    # Fetch environment variables for MSSQL fallback
    DB_SERVER = os.getenv("DB_SERVER", "BINARY4")
    DB_NAME = os.getenv("DB_NAME", "APCNew")
    DB_USERNAME = os.getenv("DB_USERNAME", "sa")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "binary124@")
    DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

    print(f"[DEBUG] Database config loaded: Server={DB_SERVER}, Name={DB_NAME}, User={DB_USERNAME} (MSSQL)")

    # Build connection string
    connection_string = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_NAME};"
        f"UID={DB_USERNAME};"
        f"PWD={DB_PASSWORD};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30;"
    )

    # Encode for SQLAlchemy
    params = urllib.parse.quote_plus(connection_string)
    DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

# Create engine with lazy connection
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    echo=False  # Set to True for SQL debugging
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

