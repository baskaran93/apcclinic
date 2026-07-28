import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.database import engine


def add_designation_column():
    with engine.begin() as conn:
        check_sql = """
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'login' AND COLUMN_NAME = 'designation_id';
        """
        result = conn.execute(text(check_sql)).scalar()
        if result == 0:
            print("Adding 'designation_id' column to login table")
            conn.execute(text("ALTER TABLE login ADD COLUMN designation_id INTEGER;"))
        else:
            print("'designation_id' column already exists on login table")

if __name__ == "__main__":
    add_designation_column()
