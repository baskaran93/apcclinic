import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.modals.patient_details import PatientDetails, TreatmentDetails, TreatmentItem
from app.modals.appointment import Appointment
from app.utils.token_generator import require_auth
from app.utils.error_handling import raise_db_error

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/summary/")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    user: dict = Depends(require_auth),
):
    try:
        today = datetime.datetime.utcnow().date()

        patients_today = (
            db.query(func.count(PatientDetails.id))
            .filter(func.date(PatientDetails.registeration_date) == today)
            .scalar()
        ) or 0

        appointments_today = (
            db.query(func.count(Appointment.id))
            .filter(func.date(Appointment.appointment_date) == today)
            .filter(Appointment.status != "Cancelled")
            .scalar()
        ) or 0

        consultations_today = (
            db.query(func.count(TreatmentDetails.id))
            .filter(func.date(TreatmentDetails.treatment_date) == today)
            .scalar()
        ) or 0

        revenue_today = (
            db.query(func.coalesce(func.sum(TreatmentItem.cost), 0))
            .join(TreatmentDetails, TreatmentItem.session_id == TreatmentDetails.id)
            .filter(func.date(TreatmentDetails.treatment_date) == today)
            .scalar()
        ) or 0

        return {
            "status": "success",
            "data": {
                "patients_today": int(patients_today),
                "appointments_today": int(appointments_today),
                "consultations_today": int(consultations_today),
                "revenue_today": float(revenue_today),
            },
        }
    except Exception as e:
        raise_db_error(e)
