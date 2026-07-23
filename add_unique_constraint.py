import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.database import engine


def add_unique_constraint():
    with engine.begin() as conn:
        # Check if constraint already exists on id column
        check_sql = """
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
        WHERE TABLE_NAME = 'patient_details' AND CONSTRAINT_TYPE = 'UNIQUE' AND CONSTRAINT_NAME = 'uq_patient_id';
        """
        result = conn.execute(text(check_sql)).scalar()
        if result == 0:
            print('Adding unique constraint on patient_details.id')
            conn.execute(text('ALTER TABLE patient_details ADD CONSTRAINT uq_patient_id UNIQUE (id);'))
        else:
            print('Unique constraint on id already exists')

if __name__ == '__main__':
    add_unique_constraint()
