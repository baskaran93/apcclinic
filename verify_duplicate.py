import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import get_db
from app.api.patient.patient_registration import register_patient
from app.modals.patient_details import PatientRegister
from fastapi import HTTPException

# Mock User
user = {"id": 1, "username": "testuser"}

def verify_duplicate():
    db = next(get_db())
    
    # "Baskaran" already exists (APC0001)
    payload = PatientRegister(
        name="Baskaran",
        phone_number="1234567890",
        age=30,
        address="Test Address",
        city="Test City",
        pincode="123456"
    )
    
    print("Attempting to register duplicate patient 'Baskaran'...")
    try:
        register_patient(payload, db, user)
        print("FAILED: Registration succeeded unexpectedly!")
    except HTTPException as e:
        print(f"Caught expected exception: {e.detail}")
        if "already exists" in e.detail:
            print("SUCCESS: Correct error message received.")
        else:
            print("FAILED: Incorrect error message.")
    except Exception as e:
        print(f"Caught unexpected exception: {e}")

if __name__ == "__main__":
    verify_duplicate()
