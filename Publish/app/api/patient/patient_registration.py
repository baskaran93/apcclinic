import datetime
from typing import Dict
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.db.database import get_db
from app.modals.patient_details import PatientRegister, PatientDetails
from app.utils.token_generator import require_auth
from fastapi import APIRouter, Depends, Request

load_dotenv()
router = APIRouter()

@router.post("/patient/details/register/")
def register_patient(patient_register: PatientRegister, db: Session = Depends(get_db),
                     user: dict = Depends(require_auth)):
    patient_count = db.query(PatientDetails).count() + 1
    patient_id = f"APC{patient_count:04d}"

    new_patient = PatientDetails(
        id = patient_id,
        name = patient_register.name,
        phone_number = patient_register.phone_number,
        age = patient_register.age,
        address = patient_register.address,
        city = patient_register.city,
        pincode = patient_register.pincode,
        mode_of_referral = patient_register.mode_of_referral,
        registeration_date = func.now()
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return {"message": "Patient registered successfully", "id":new_patient.id}
