import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.modals.patient_details import PatientDetails, TreatmentDetails, TreatmentItem
from app.modals.appointment import Appointment
from app.modals.office_expense import OfficeExpense
from app.modals.enquiry import Enquiry
from app.utils.token_generator import require_auth
from app.utils.error_handling import raise_db_error

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


def _period_range(today: datetime.date, period: str):
    if period == "day":
        return today, today, "Today"
    if period == "week":
        start = today - datetime.timedelta(days=today.weekday())  # Monday
        return start, today, "This Week"
    # month (default)
    start = today.replace(day=1)
    return start, today, "This Month"


@router.get("/summary/")
def get_dashboard_summary(
    period: str = Query("month", pattern="^(day|week|month)$"),
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

        income_today = (
            db.query(func.coalesce(func.sum(TreatmentItem.cost), 0))
            .join(TreatmentDetails, TreatmentItem.session_id == TreatmentDetails.id)
            .filter(func.date(TreatmentDetails.treatment_date) == today)
            .scalar()
        ) or 0

        expenses_today = (
            db.query(func.coalesce(func.sum(OfficeExpense.amount), 0))
            .filter(func.date(OfficeExpense.expense_date) == today)
            .scalar()
        ) or 0

        revenue_today = float(income_today) - float(expenses_today)

        # ===== Period-based figures (day / week / month, default month) =====
        start_date, end_date, period_label = _period_range(today, period)

        income_period = (
            db.query(func.coalesce(func.sum(TreatmentItem.cost), 0))
            .join(TreatmentDetails, TreatmentItem.session_id == TreatmentDetails.id)
            .filter(func.date(TreatmentDetails.treatment_date).between(start_date, end_date))
            .scalar()
        ) or 0

        expenses_period = (
            db.query(func.coalesce(func.sum(OfficeExpense.amount), 0))
            .filter(func.date(OfficeExpense.expense_date).between(start_date, end_date))
            .scalar()
        ) or 0

        income_period = float(income_period)
        expenses_period = float(expenses_period)
        profit_loss = income_period - expenses_period
        profit_margin = (profit_loss / income_period * 100) if income_period > 0 else 0.0
        profit_loss_status = "profit" if profit_loss > 0 else ("loss" if profit_loss < 0 else "breakeven")

        walkins_period = (
            db.query(func.count(Enquiry.id))
            .filter(func.date(Enquiry.enquiry_date).between(start_date, end_date))
            .scalar()
        ) or 0

        return {
            "status": "success",
            "data": {
                "patients_today": int(patients_today),
                "appointments_today": int(appointments_today),
                "consultations_today": int(consultations_today),
                "income_today": float(income_today),
                "expenses_today": float(expenses_today),
                "revenue_today": revenue_today,
                "period": period,
                "period_label": period_label,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "income_period": income_period,
                "expenses_period": expenses_period,
                "profit_loss": profit_loss,
                "profit_margin": round(profit_margin, 1),
                "profit_loss_status": profit_loss_status,
                "walkins_period": int(walkins_period),
            },
        }
    except Exception as e:
        raise_db_error(e)
