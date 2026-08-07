import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.modals.appointment import Appointment, AppointmentCreate, AppointmentUpdate
from app.modals.patient_details import PatientDetails
from app.utils.permissions import require_permission
from app.utils.error_handling import raise_db_error

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)


def _serialize(appt: Appointment, patient: Optional[PatientDetails] = None):
    return {
        "id": appt.id,
        "patient_id": appt.patient_id,
        "patient_name": patient.name if patient else None,
        "patient_phone": patient.phone_number if patient else None,
        "appointment_date": appt.appointment_date,
        "doctor_name": appt.doctor_name,
        "notes": appt.notes,
        "status": appt.status,
        "created_at": appt.created_at,
    }


@router.post("/book/")
def book_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("appointments", "add")),
):
    try:
        patient = db.query(PatientDetails).filter(PatientDetails.id == payload.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        appt = Appointment(
            patient_id=payload.patient_id,
            appointment_date=payload.appointment_date,
            doctor_name=payload.doctor_name,
            notes=payload.notes,
            status="Scheduled",
            created_at=datetime.datetime.utcnow(),
        )
        db.add(appt)
        db.commit()
        db.refresh(appt)
        return {"status": "success", "message": "Appointment booked successfully", "data": _serialize(appt, patient)}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise_db_error(e)


@router.get("/list/")
def list_appointments(
    date: Optional[str] = Query(None, description="Filter by date YYYY-MM-DD"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("appointments", "view")),
):
    try:
        query = db.query(Appointment)

        if date:
            try:
                day = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format, expected YYYY-MM-DD")
            query = query.filter(func.date(Appointment.appointment_date) == day)

        if status:
            query = query.filter(Appointment.status == status)

        appointments = query.order_by(Appointment.appointment_date.asc()).all()

        patient_ids = {a.patient_id for a in appointments}
        patients = {
            p.id: p
            for p in db.query(PatientDetails).filter(PatientDetails.id.in_(patient_ids)).all()
        } if patient_ids else {}

        data = [_serialize(a, patients.get(a.patient_id)) for a in appointments]

        return {"status": "success", "count": len(data), "data": data}
    except HTTPException:
        raise
    except Exception as e:
        raise_db_error(e)


@router.patch("/{appointment_id}/")
def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("appointments", "edit")),
):
    try:
        appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appt:
            raise HTTPException(status_code=404, detail="Appointment not found")

        if payload.appointment_date is not None:
            appt.appointment_date = payload.appointment_date
        if payload.doctor_name is not None:
            appt.doctor_name = payload.doctor_name
        if payload.notes is not None:
            appt.notes = payload.notes
        if payload.status is not None:
            appt.status = payload.status

        db.commit()
        db.refresh(appt)

        patient = db.query(PatientDetails).filter(PatientDetails.id == appt.patient_id).first()
        return {"status": "success", "message": "Appointment updated successfully", "data": _serialize(appt, patient)}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise_db_error(e)


@router.delete("/{appointment_id}/")
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("appointments", "delete")),
):
    try:
        appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appt:
            raise HTTPException(status_code=404, detail="Appointment not found")

        appt.status = "Cancelled"
        db.commit()
        return {"status": "success", "message": "Appointment cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise_db_error(e)
