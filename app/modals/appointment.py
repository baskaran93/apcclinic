from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from app.db.database import Base


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


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(10), ForeignKey("patient_details.id"), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    doctor_name = Column(String(100), nullable=True)
    notes = Column(String(1000), nullable=True)
    status = Column(String(20), nullable=False, default="Scheduled")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
