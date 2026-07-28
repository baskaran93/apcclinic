from sqlalchemy import Column, Integer, String
from app.db.database import Base
from pydantic import BaseModel
from typing import Optional

class Designation(Base):
    __tablename__ = "designations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    designation_name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)

class DesignationCreate(BaseModel):
    designation_name: str
    description: Optional[str] = None
