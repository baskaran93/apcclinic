import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.modals.patient_details import Treatment, TreatmentDetails
from app.modals.patient_details import PatientDetails
from app.utils.token_generator import require_auth
from fastapi import APIRouter, Depends, Request

load_dotenv()
router = APIRouter()

@router.post("/treatement/details/register/")
def register_treatment(treatment_register: Treatment, db: Session = Depends(get_db),
                     user: dict = Depends(require_auth)):
    count = db.query(TreatmentDetails).count() + 1
    treatment = TreatmentDetails(
        id = count,
        patient_id = treatment_register.patient_id,
        treatment_date = datetime.datetime.now().date(),
        diagnosis = treatment_register.diagnosis,
        treatment_plan = treatment_register.treatment_plan,
        doctor_name = treatment_register.doctor_name,
        notes = treatment_register.notes
    )
    db.add(treatment)
    db.commit()
    db.refresh(treatment)
    return {"message": "Patient registered successfully", "id":treatment.id}