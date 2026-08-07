from sqlalchemy import Column, Integer, String
from app.db.database import Base
from pydantic import BaseModel
from typing import Optional

class ReferralType(Base):
    __tablename__ = "referral_types"
    id = Column(Integer, primary_key=True, autoincrement=True)
    referral_type_name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)

class ReferralTypeCreate(BaseModel):
    referral_type_name: str
    description: Optional[str] = None
