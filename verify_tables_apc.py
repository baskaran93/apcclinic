from sqlalchemy import inspect
from app.db.database import engine
import traceback

def verify_tables():
    print("Checking database schema for treatment tables...")
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        target_tables = ['treatment_details', 'treatment_items']
        
        for table in target_tables:
            if table in tables:
                print(f"✅ Table '{table}' EXISTS.")
                columns = inspector.get_columns(table)
                for col in columns:
                    print(f"   - {col['name']} ({col['type']})")
            else:
                print(f"❌ Table '{table}' MISSING!")
                
    except Exception as e:
        print("Error verifying schema:")
        traceback.print_exc()

if __name__ == "__main__":
    verify_tables()
