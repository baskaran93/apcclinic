import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, exists

from app.db.database import get_db
from app.modals.patient_details import PatientDetails, TreatmentDetails, TreatmentItem
from app.modals.appointment import Appointment
from app.modals.office_expense import OfficeExpense
from app.utils.token_generator import require_auth
from app.utils.error_handling import raise_db_error

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


def _parse_date(value: str, field_name: str) -> datetime.date:
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}, expected YYYY-MM-DD")


def _period_range(today: datetime.date, period: str, start_date: str = None, end_date: str = None):
    if period == "day":
        return today, today, "Today"
    if period == "week":
        start = today - datetime.timedelta(days=today.weekday())  # Monday
        return start, today, "This Week"
    if period == "custom":
        if not start_date or not end_date:
            raise HTTPException(status_code=400, detail="start_date and end_date are required for a custom period")
        start = _parse_date(start_date, "start_date")
        end = _parse_date(end_date, "end_date")
        if start > end:
            raise HTTPException(status_code=400, detail="start_date must be on or before end_date")
        label = f"{start.strftime('%d %b %Y')} – {end.strftime('%d %b %Y')}" if start != end else start.strftime("%d %b %Y")
        return start, end, label
    # month (default)
    start = today.replace(day=1)
    return start, today, "This Month"


@router.get("/summary/")
def get_dashboard_summary(
    period: str = Query("month", pattern="^(day|week|month|custom)$"),
    start_date: str = Query(None, description="Required when period=custom, format YYYY-MM-DD"),
    end_date: str = Query(None, description="Required when period=custom, format YYYY-MM-DD"),
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

        # ===== Period-based figures (day / week / month / custom, default month) =====
        start_date, end_date, period_label = _period_range(today, period, start_date, end_date)

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

        # Walk-in = a treatment given with no matching appointment booked for
        # that patient on that same day (i.e. they were seen without booking
        # ahead), rather than a scheduled/confirmed visit.
        had_appointment_that_day = (
            exists()
            .where(Appointment.patient_id == TreatmentDetails.patient_id)
            .where(func.date(Appointment.appointment_date) == func.date(TreatmentDetails.treatment_date))
            .where(Appointment.status != "Cancelled")
        )

        walkins_period = (
            db.query(func.count(TreatmentDetails.id))
            .filter(func.date(TreatmentDetails.treatment_date).between(start_date, end_date))
            .filter(~had_appointment_that_day)
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
    except HTTPException:
        raise
    except Exception as e:
        raise_db_error(e)
