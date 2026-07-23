import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import get_db
from app.modals.patient_details import PatientDetails
from sqlalchemy.orm import Session

def check_patient(patient_id: str):
    db: Session = next(get_db())
    patient = db.query(PatientDetails).filter(PatientDetails.id == patient_id).first()
    if patient:
        print(f"Patient {patient_id} exists: {patient.name}")
    else:
        print(f"Patient {patient_id} DOES NOT exist!")

if __name__ == "__main__":
    check_patient("APC0001")
