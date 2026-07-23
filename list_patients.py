import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import get_db
from app.modals.patient_details import PatientDetails

def list_patients():
    db = next(get_db())
    patients = db.query(PatientDetails).all()
    print(f"Found {len(patients)} patients:")
    for p in patients:
        print(f"ID: {p.id}, Name: {p.name}, Phone: {p.phone_number}")

if __name__ == "__main__":
    list_patients()
