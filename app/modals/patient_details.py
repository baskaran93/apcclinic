from sqlalchemy.orm import declarative_base
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Text

from app.db.database import Base

class PatientRegister(BaseModel):
    name: str
    phone_number: str
    alternative_number: Optional[str] = None
    age: int = Field(default=0, ge=0, le=150)
    address: str = ""
    city: str = ""
    pincode: str = ""
    mode_of_referral: Optional[str] = None



class PatientDetails(Base):
    __tablename__ = "patient_details"
    id = Column(String(10), primary_key=True)
    name = Column(String, nullable=False)
    registeration_date = Column(DateTime, nullable=False)
    phone_number = Column(String, nullable=False)
    alternative_number = Column(String, nullable=True)
    age =  Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    pincode = Column(String, nullable=False)
    mode_of_referral = Column(String, nullable=True)




class TreatmentItemCreate(BaseModel):
    treatment_name: str
    cost: float = Field(ge=0)

class TreatmentCreate(BaseModel):
    patient_id: str
    diagnosis: str
    treatment_plan: Optional[str] = None
    doctor_name: Optional[str] = None
    notes: Optional[str] = None
    items: list[TreatmentItemCreate] = []
    assessment_file_name: Optional[str] = None
    assessment_file_base64: Optional[str] = None

    class Config:
        from_attributes = True

class TreatmentDetails(Base):
    __tablename__ = "treatment_details"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(10), ForeignKey("patient_details.id"), nullable=False)  # FK to patient_details.id
    treatment_date = Column(DateTime, nullable=False, server_default=func.now())
    diagnosis = Column(String(500), nullable=False)
    treatment_plan = Column(String(1000), nullable=True)
    doctor_name = Column(String(100), nullable=True)
    notes = Column(String(2000), nullable=True)
    assessment_file_name = Column(String(255), nullable=True)
    assessment_file_base64 = Column(Text, nullable=True)

class TreatmentItem(Base):
    __tablename__ = "treatment_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("treatment_details.id"), nullable=False)
    treatment_name = Column(String(500), nullable=False)
    cost = Column(Float, nullable=False)