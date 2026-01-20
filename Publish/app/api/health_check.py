from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from sqlalchemy.sql import text

router = APIRouter()

@router.get("/health/db")
def db_health_check(db: Session = Depends(get_db)):
    try:
        query = "SELECT 1"
        db.execute(text(query))  # Simple test query
        return {"status": "✅ Database is connected"}
    except Exception as e:
        return {"status": "❌ Database connection failed", "error": str(e)}
