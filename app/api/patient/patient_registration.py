import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.db.database import get_db
from app.modals.patient_details import PatientRegister, PatientDetails, TreatmentDetails, TreatmentItem
from app.modals.appointment import Appointment
from app.utils.permissions import require_permission
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel

load_dotenv()
router = APIRouter()


class PatientUpdate(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    phone_number: Optional[str] = None
    age: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    mode_of_referral: Optional[str] = None


@router.post("/patient/details/register/")
def register_patient(patient_register: PatientRegister, db: Session = Depends(get_db),
                     user: dict = Depends(require_permission("patients", "add"))):
    try:
        # Generate a unique patient ID based on the maximum existing ID
        max_id = db.query(func.max(PatientDetails.id)).scalar()
        if max_id:
            try:
                max_num = int(max_id.replace('APC', ''))
            except ValueError:
                max_num = 0
            new_num = max_num + 1
        else:
            new_num = 1
        patient_id = f"APC{new_num:04d}"

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
    except IntegrityError as e:
        db.rollback()
        error_str = str(e)
        print(f"REGISTRATION INTEGRITY ERROR: {error_str}")
        if "ix_patient_details_name" in error_str or "UniqueViolation" in error_str or "2601" in error_str:
            raise HTTPException(status_code=400, detail="A patient with this name already exists.")
        raise HTTPException(status_code=400, detail="Database integrity error.")
    except Exception as e:
        db.rollback()
        error_str = str(e)
        print(f"REGISTRATION ERROR: {error_str}")
        if "SQLDriverConnect" in error_str or "Cannot open server" in error_str:
             raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
        raise HTTPException(status_code=400, detail=error_str)


@router.put("/patient/details/update/{patient_id}/")
def update_patient_path(patient_id: str, patient_update: PatientUpdate, db: Session = Depends(get_db),
                        user: dict = Depends(require_permission("patients", "edit"))):
    """Update patient by path parameter ID. Only provided fields will be updated."""
    try:
        patient = db.query(PatientDetails).filter(PatientDetails.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Update only provided fields
        for field, value in patient_update.dict(exclude_unset=True).items():
            if field == "id":
                continue
            setattr(patient, field, value)

        db.commit()
        db.refresh(patient)
        return {"message": "Patient updated successfully", "id": patient.id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"UPDATE ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/patient/details/update/")
def update_patient_body(patient_update: PatientUpdate, db: Session = Depends(get_db),
                        user: dict = Depends(require_permission("patients", "edit"))):
    """Update patient by sending an object containing `id` and the fields to update."""
    try:
        if not patient_update.id:
            raise HTTPException(status_code=400, detail="Patient id is required in the payload")

        patient = db.query(PatientDetails).filter(PatientDetails.id == patient_update.id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        for field, value in patient_update.dict(exclude_unset=True).items():
            if field == "id":
                continue
            setattr(patient, field, value)

        db.commit()
        db.refresh(patient)
        return {"message": "Patient updated successfully", "id": patient.id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"UPDATE ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/patient/details/{patient_id}/")
def update_patient_patch(patient_id: str, patient_update: PatientUpdate, db: Session = Depends(get_db),
                         user: dict = Depends(require_permission("patients", "edit"))):
    """Handle PATCH requests to update partial patient fields at the path the frontend uses."""
    try:
        patient = db.query(PatientDetails).filter(PatientDetails.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        for field, value in patient_update.dict(exclude_unset=True).items():
            if field == "id":
                continue
            setattr(patient, field, value)

        db.commit()
        db.refresh(patient)
        return {"message": "Patient updated successfully", "id": patient.id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_str = str(e)
        print(f"DATABASE ERROR: {error_str}")
        if "SQLDriverConnect" in error_str or "Cannot open server" in error_str:
             raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
        raise HTTPException(status_code=500, detail=error_str)


@router.delete("/patient/details/{patient_id}/")
def delete_patient(patient_id: str, db: Session = Depends(get_db),
                    user: dict = Depends(require_permission("patients", "delete"))):
    try:
        patient = db.query(PatientDetails).filter(PatientDetails.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        session_ids = [
            row[0] for row in
            db.query(TreatmentDetails.id).filter(TreatmentDetails.patient_id == patient_id).all()
        ]
        if session_ids:
            db.query(TreatmentItem).filter(TreatmentItem.session_id.in_(session_ids)).delete(synchronize_session=False)
        db.query(TreatmentDetails).filter(TreatmentDetails.patient_id == patient_id).delete(synchronize_session=False)
        db.query(Appointment).filter(Appointment.patient_id == patient_id).delete(synchronize_session=False)
        db.delete(patient)

        db.commit()
        return {"message": "Patient deleted successfully", "id": patient_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_str = str(e)
        if "SQLDriverConnect" in error_str or "Cannot open server" in error_str:
             raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
        raise HTTPException(status_code=500, detail=error_str)
