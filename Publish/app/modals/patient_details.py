from sqlalchemy.orm import declarative_base
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

BASE = declarative_base()

class PatientRegister(BaseModel):
    name: str
    phone_number: str
    age: int
    address: str
    city: str
    pincode: str
    mode_of_referral: Optional[str]



class PatientDetails(BASE):
    __tablename__ = "patient_details"
    id = Column(String(10), primary_key=True)
    name = Column(String, unique=True, nullable=False)
    registeration_date = Column(DateTime, nullable=False)
    phone_number = Column(String, nullable=False)
    age =  Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    pincode = Column(String, nullable=False)
    mode_of_referral = Column(String, nullable=True)




class Treatment(BaseModel):
    patient_id : str
    treatment_date : Optional[datetime] = datetime.utcnow()
    diagnosis : str
    treatment_plan : Optional[str] = None
    doctor_name : Optional[str] = None
    notes : Optional[str] = None

    class Config:
        from_attributes = True

class TreatmentDetails(BASE):
    __tablename__ = "treatment_details"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(10), ForeignKey("patient_details.id"), nullable=False)  # FK to patient_details.id
    treatment_date = Column(DateTime, nullable=False, server_default=func.now())
    diagnosis = Column(String(500), nullable=False)
    treatment_plan = Column(String(1000), nullable=True)
    doctor_name = Column(String(100), nullable=True)
    notes = Column(String(2000), nullable=True)