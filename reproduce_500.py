import sys
import os
import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import get_db
from app.api.patient.treatment_details import register_treatment
from app.modals.patient_details import TreatmentCreate, TreatmentItemCreate

def reproduce():
    db = next(get_db())
    
    # Mock payload matching user data
    payload = TreatmentCreate(
        patient_id="APC0001",
        diagnosis="test",
        treatment_plan="Master-Detail Visit",
        doctor_name="madhu",
        notes="text",
        items=[
            TreatmentItemCreate(treatment_name="Consultation", cost=500.0)
        ]
    )
    
    # Mock user
    user = {"id": 1, "username": "testuser"}
    
    print("Calling register_treatment...")
    try:
        register_treatment(payload, db, user)
        print("Success!")
    except Exception as e:
        print(f"Caught exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reproduce()
