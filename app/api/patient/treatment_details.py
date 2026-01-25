import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.modals.patient_details import TreatmentCreate, TreatmentDetails, TreatmentItem, PatientDetails
from app.utils.token_generator import require_auth
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy import desc

load_dotenv()
router = APIRouter(
    prefix="/patient",
    tags=["Patient"],
)

@router.post("/treatement/details/register/")
def register_treatment(treatment_register: TreatmentCreate, db: Session = Depends(get_db),
                     user: dict = Depends(require_auth)):
    try:
        print(f"[DEBUG] Registering treatment for patient: {treatment_register.patient_id}")
        print(f"[DEBUG] Payload: {treatment_register.dict()}")

        treatment = TreatmentDetails(
            patient_id = treatment_register.patient_id,
            treatment_date = datetime.datetime.now(),
            diagnosis = treatment_register.diagnosis,
            treatment_plan = treatment_register.treatment_plan,
            doctor_name = treatment_register.doctor_name,
            notes = treatment_register.notes
        )
        db.add(treatment)
        db.commit()
        db.refresh(treatment)
        print(f"[DEBUG] Master record created with ID: {treatment.id}")

        # Save child items
        for item in treatment_register.items:
            db_item = TreatmentItem(
                session_id = treatment.id,
                treatment_name = item.treatment_name,
                cost = item.cost
            )
            db.add(db_item)
        
        db.commit()
        print(f"[DEBUG] {len(treatment_register.items)} child items saved.")
        return {"message": "Treatment registered successfully", "id": treatment.id}
    
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Treatment Registration Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

@router.get("/treatement/history/{patient_id}")
def get_treatment_history(patient_id: str, db: Session = Depends(get_db),
                         user: dict = Depends(require_auth)):
    history = db.query(TreatmentDetails).filter(
        TreatmentDetails.patient_id == patient_id
    ).order_by(desc(TreatmentDetails.treatment_date)).all()

    # Enrich with items
    data = []
    for h in history:
        items = db.query(TreatmentItem).filter(TreatmentItem.session_id == h.id).all()
        h_dict = {
            "id": h.id,
            "treatment_date": h.treatment_date,
            "diagnosis": h.diagnosis,
            "doctor_name": h.doctor_name,
            "notes": h.notes,
            "items": [{"treatment_name": i.treatment_name, "cost": i.cost} for i in items]
        }
        data.append(h_dict)
    
    return {"status": "success", "data": data}