from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from app.db.database import Base

VALID_APPOINTMENT_STATUSES = ("Scheduled", "Completed", "Cancelled")


class AppointmentCreate(BaseModel):
    patient_id: str
    appointment_date: datetime
    doctor_name: Optional[str] = None
    notes: Optional[str] = None


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    doctor_name: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if value is not None and value not in VALID_APPOINTMENT_STATUSES:
            raise ValueError(f"status must be one of {VALID_APPOINTMENT_STATUSES}")
        return value


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(10), ForeignKey("patient_details.id"), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    doctor_name = Column(String(100), nullable=True)
    notes = Column(String(1000), nullable=True)
    status = Column(String(20), nullable=False, default="Scheduled")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
