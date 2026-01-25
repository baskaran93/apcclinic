from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base
from pydantic import BaseModel
from typing import Optional

class TreatmentCharge(Base):
    __tablename__ = "treatment_charges"
    id = Column(Integer, primary_key=True, autoincrement=True)
    treatment_name = Column(String(200), nullable=False)
    cost = Column(Float, nullable=False)
    description = Column(String(500), nullable=True)

class TreatmentChargeCreate(BaseModel):
    treatment_name: str
    cost: float
    description: Optional[str] = None
