import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError

from app.db.database import get_db
from app.modals.enquiry import Enquiry, EnquiryCreate
from app.modals.patient_details import PatientDetails
from app.utils.permissions import require_permission
from app.utils.error_handling import raise_db_error

router = APIRouter(
    prefix="/enquiry",
    tags=["Enquiry"],
)


def _serialize(enquiry: Enquiry):
    return {
        "id": enquiry.id,
        "name": enquiry.name,
        "phone_number": enquiry.phone_number,
        "alternative_number": enquiry.alternative_number,
        "reason": enquiry.reason,
        "enquiry_date": enquiry.enquiry_date,
        "status": enquiry.status,
        "converted_patient_id": enquiry.converted_patient_id,
    }


@router.post("/register/")
def register_enquiry(
    payload: EnquiryCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("patients", "add")),
):
    # Same optimistic max(id)+1 + retry-on-collision approach used for
    # patient registration, so two concurrent walk-ins can't be assigned
    # the same enquiry number.
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            max_id = db.query(func.max(Enquiry.id)).scalar()
            if max_id:
                try:
                    max_num = int(max_id.replace("ENQ", ""))
                except ValueError:
                    max_num = 0
                new_num = max_num + 1
            else:
                new_num = 1
            enquiry_id = f"ENQ{new_num:04d}"

            enquiry = Enquiry(
                id=enquiry_id,
                name=payload.name,
                phone_number=payload.phone_number,
                alternative_number=payload.alternative_number,
                reason=payload.reason,
                enquiry_date=datetime.datetime.utcnow(),
                status="Open",
            )
            db.add(enquiry)
            db.commit()
            db.refresh(enquiry)
            return {"status": "success", "message": "Enquiry registered successfully", "data": _serialize(enquiry)}
        except IntegrityError:
            db.rollback()
            if attempt < max_attempts - 1:
                continue
            raise HTTPException(status_code=400, detail="Could not register enquiry, please try again.")
        except Exception as e:
            db.rollback()
            raise_db_error(e)


@router.get("/list/")
def list_enquiries(
    status: Optional[str] = Query(None, description="Filter by status, e.g. Open or Converted"),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("patients", "view")),
):
    try:
        query = db.query(Enquiry)
        if status:
            query = query.filter(Enquiry.status == status)
        enquiries = query.order_by(Enquiry.enquiry_date.desc()).all()
        return {"status": "success", "count": len(enquiries), "data": [_serialize(e) for e in enquiries]}
    except Exception as e:
        raise_db_error(e)


@router.post("/convert/{enquiry_id}/")
def convert_enquiry_to_patient(
    enquiry_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("patients", "add")),
):
    """Turns an enquiry into a full patient record, re-pointing any
    appointments booked against the enquiry to the new patient id."""
    try:
        enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
        if not enquiry:
            raise HTTPException(status_code=404, detail="Enquiry not found")
        if enquiry.status == "Converted" and enquiry.converted_patient_id:
            raise HTTPException(status_code=400, detail="This enquiry has already been converted to a patient")

        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                max_id = db.query(func.max(PatientDetails.id)).scalar()
                if max_id:
                    try:
                        max_num = int(max_id.replace("APC", ""))
                    except ValueError:
                        max_num = 0
                    new_num = max_num + 1
                else:
                    new_num = 1
                patient_id = f"APC{new_num:04d}"

                new_patient = PatientDetails(
                    id=patient_id,
                    name=enquiry.name,
                    phone_number=enquiry.phone_number,
                    alternative_number=enquiry.alternative_number,
                    age=0,
                    address="",
                    city="",
                    pincode="",
                    mode_of_referral=None,
                    registeration_date=func.now(),
                )
                db.add(new_patient)
                db.flush()
                break
            except IntegrityError:
                db.rollback()
                if attempt < max_attempts - 1:
                    continue
                raise HTTPException(status_code=400, detail="Could not convert enquiry, please try again.")

        enquiry.status = "Converted"
        enquiry.converted_patient_id = new_patient.id

        # Re-point this enquiry's appointments to the new patient record.
        from app.modals.appointment import Appointment
        db.query(Appointment).filter(Appointment.enquiry_id == enquiry_id).update(
            {Appointment.patient_id: new_patient.id, Appointment.enquiry_id: None},
            synchronize_session=False,
        )

        db.commit()
        return {
            "status": "success",
            "message": "Enquiry converted to patient successfully",
            "data": {"patient_id": new_patient.id, "enquiry_id": enquiry.id},
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise_db_error(e)
