import datetime
import mimetypes
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.modals.patient_details import TreatmentCreate, TreatmentDetails, TreatmentItem, PatientDetails
from app.utils.permissions import require_permission
from app.utils.error_handling import raise_db_error
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy import desc

load_dotenv()
router = APIRouter(
    prefix="/patient",
    tags=["Patient"],
)

@router.post("/treatement/details/register/")
def register_treatment(treatment_register: TreatmentCreate, db: Session = Depends(get_db),
                     user: dict = Depends(require_permission("patient_treatment", "add"))):
    try:
        patient = db.query(PatientDetails).filter(PatientDetails.id == treatment_register.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        treatment = TreatmentDetails(
            patient_id = treatment_register.patient_id,
            treatment_date = datetime.datetime.now(),
            diagnosis = treatment_register.diagnosis,
            treatment_plan = treatment_register.treatment_plan,
            doctor_name = treatment_register.doctor_name,
            notes = treatment_register.notes,
            assessment_file_name = treatment_register.assessment_file_name,
            assessment_file_base64 = treatment_register.assessment_file_base64
        )
        db.add(treatment)
        db.commit()
        db.refresh(treatment)

        # Save child items
        for item in treatment_register.items:
            db_item = TreatmentItem(
                session_id = treatment.id,
                treatment_name = item.treatment_name,
                cost = item.cost
            )
            db.add(db_item)

        db.commit()
        return {"message": "Treatment registered successfully", "id": treatment.id}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise_db_error(e)

@router.get("/treatement/diagnoses/distinct")
def get_distinct_diagnoses(db: Session = Depends(get_db),
                         user: dict = Depends(require_permission("patient_treatment", "view"))):
    try:
        results = db.query(TreatmentDetails.diagnosis).distinct().all()
        # Flatten list of tuples
        diagnoses = [r[0] for r in results if r[0]]
        return {"status": "success", "data": diagnoses}
    except Exception as e:
        raise_db_error(e)

@router.get("/treatement/physiotherapists/distinct")
def get_distinct_physiotherapists(db: Session = Depends(get_db),
                               user: dict = Depends(require_permission("patient_treatment", "view"))):
    try:
        results = db.query(TreatmentDetails.doctor_name).distinct().all()
        # Flatten list of tuples
        physiotherapists = [r[0] for r in results if r[0]]
        return {"status": "success", "data": physiotherapists}
    except Exception as e:
        raise_db_error(e)

@router.get("/treatement/history/")
def get_all_treatment_history(db: Session = Depends(get_db),
                               user: dict = Depends(require_permission("patient_treatment", "view"))):
    history = db.query(TreatmentDetails).order_by(desc(TreatmentDetails.treatment_date)).all()

    patient_ids = {h.patient_id for h in history}
    patients = {
        p.id: p
        for p in db.query(PatientDetails).filter(PatientDetails.id.in_(patient_ids)).all()
    } if patient_ids else {}

    data = []
    for h in history:
        items = db.query(TreatmentItem).filter(TreatmentItem.session_id == h.id).all()
        patient = patients.get(h.patient_id)
        data.append({
            "id": h.id,
            "patient_id": h.patient_id,
            "patient_name": patient.name if patient else None,
            "patient_phone": patient.phone_number if patient else None,
            "treatment_date": h.treatment_date,
            "diagnosis": h.diagnosis,
            "doctor_name": h.doctor_name,
            "notes": h.notes,
            "items": [{"treatment_name": i.treatment_name, "cost": i.cost} for i in items],
            "has_assessment_file": bool(h.assessment_file_base64),
            "assessment_file_name": h.assessment_file_name,
        })

    return {"status": "success", "count": len(data), "data": data}


@router.get("/treatement/history/{patient_id}")
def get_treatment_history(patient_id: str, db: Session = Depends(get_db),
                         user: dict = Depends(require_permission("patient_treatment", "view"))):
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
            "items": [{"treatment_name": i.treatment_name, "cost": i.cost} for i in items],
            "has_assessment_file": bool(h.assessment_file_base64),
            "assessment_file_name": h.assessment_file_name,
        }
        data.append(h_dict)

    return {"status": "success", "data": data}


@router.get("/treatement/details/{session_id}/assessment-file/")
def get_assessment_file(session_id: int, db: Session = Depends(get_db),
                         user: dict = Depends(require_permission("patient_treatment", "view"))):
    treatment = db.query(TreatmentDetails).filter(TreatmentDetails.id == session_id).first()
    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment record not found")
    if not treatment.assessment_file_base64:
        raise HTTPException(status_code=404, detail="No assessment file attached to this record")

    content_type, _ = mimetypes.guess_type(treatment.assessment_file_name or "")
    return {
        "status": "success",
        "data": {
            "filename": treatment.assessment_file_name or f"assessment_{session_id}",
            "content_type": content_type or "application/octet-stream",
            "content_base64": treatment.assessment_file_base64,
        },
    }


@router.put("/treatement/details/{session_id}/")
def update_treatment(session_id: int, treatment_update: TreatmentCreate, db: Session = Depends(get_db),
                      user: dict = Depends(require_permission("patient_treatment", "edit"))):
    try:
        treatment = db.query(TreatmentDetails).filter(TreatmentDetails.id == session_id).first()
        if not treatment:
            raise HTTPException(status_code=404, detail="Treatment record not found")

        treatment.diagnosis = treatment_update.diagnosis
        treatment.treatment_plan = treatment_update.treatment_plan
        treatment.doctor_name = treatment_update.doctor_name
        treatment.notes = treatment_update.notes
        if treatment_update.assessment_file_base64 is not None:
            treatment.assessment_file_name = treatment_update.assessment_file_name
            treatment.assessment_file_base64 = treatment_update.assessment_file_base64

        # Replace items wholesale
        db.query(TreatmentItem).filter(TreatmentItem.session_id == session_id).delete(synchronize_session=False)
        for item in treatment_update.items:
            db.add(TreatmentItem(session_id=session_id, treatment_name=item.treatment_name, cost=item.cost))

        db.commit()
        db.refresh(treatment)
        return {"message": "Treatment updated successfully", "id": treatment.id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise_db_error(e)


@router.delete("/treatement/details/{session_id}/")
def delete_treatment(session_id: int, db: Session = Depends(get_db),
                      user: dict = Depends(require_permission("patient_treatment", "delete"))):
    try:
        treatment = db.query(TreatmentDetails).filter(TreatmentDetails.id == session_id).first()
        if not treatment:
            raise HTTPException(status_code=404, detail="Treatment record not found")

        db.query(TreatmentItem).filter(TreatmentItem.session_id == session_id).delete(synchronize_session=False)
        db.delete(treatment)
        db.commit()
        return {"message": "Treatment deleted successfully", "id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise_db_error(e)
