from typing import Optional

from app.db.database import Base
from pydantic import BaseModel, field_validator
from sqlalchemy import Column, Integer, String, DateTime

VALID_ROLES = ("admin", "doctor", "receptionist")


class UserRegister(BaseModel):
    username: str
    password_hash: str
    role: str = "receptionist"

    @field_validator("role")
    @classmethod
    def validate_role(cls, value):
        if value not in VALID_ROLES:
            raise ValueError(f"role must be one of {VALID_ROLES}")
        return value


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class UserUpdate(BaseModel):
    role: Optional[str] = None
    new_password: Optional[str] = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, value):
        if value is not None and value not in VALID_ROLES:
            raise ValueError(f"role must be one of {VALID_ROLES}")
        return value


class User(Base):
    __tablename__ = "login"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    password_reset_time = Column(DateTime, nullable=True)
    role = Column(String, nullable=False, server_default="receptionist")