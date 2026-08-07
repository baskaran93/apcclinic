from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.db.database import Base
from pydantic import BaseModel, Field
from typing import Optional

class OfficeExpense(Base):
    __tablename__ = "office_expenses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    expense_date = Column(DateTime, nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    remarks = Column(String(1000), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

class OfficeExpenseCreate(BaseModel):
    expense_date: str  # "YYYY-MM-DD"
    description: str
    amount: float = Field(ge=0)
    remarks: Optional[str] = None
