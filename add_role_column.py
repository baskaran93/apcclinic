import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.database import engine


def add_role_column():
    with engine.begin() as conn:
        check_sql = """
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'login' AND COLUMN_NAME = 'role';
        """
        result = conn.execute(text(check_sql)).scalar()
        if result == 0:
            print("Adding 'role' column to login table")
            conn.execute(text("ALTER TABLE login ADD COLUMN role VARCHAR(20);"))
            print("Backfilling existing users as 'admin'")
            conn.execute(text("UPDATE login SET role = 'admin' WHERE role IS NULL;"))
            conn.execute(text("ALTER TABLE login ALTER COLUMN role SET NOT NULL;"))
            conn.execute(text("ALTER TABLE login ALTER COLUMN role SET DEFAULT 'receptionist';"))
        else:
            print("'role' column already exists on login table")

if __name__ == "__main__":
    add_role_column()
