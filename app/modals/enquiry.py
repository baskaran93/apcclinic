from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from app.db.database import Base

VALID_ENQUIRY_STATUSES = ("Open", "Converted")


class EnquiryCreate(BaseModel):
    name: str
    phone_number: str
    alternative_number: Optional[str] = None
    reason: Optional[str] = None


class Enquiry(Base):
    __tablename__ = "enquiries"
    id = Column(String(10), primary_key=True)  # e.g. ENQ0001
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    alternative_number = Column(String, nullable=True)
    reason = Column(String(500), nullable=True)
    enquiry_date = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="Open")  # Open | Converted
    converted_patient_id = Column(String(10), ForeignKey("patient_details.id"), nullable=True)
