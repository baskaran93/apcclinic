from app.db.database import Base
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime

class UserRegister(BaseModel):
    username: str
    password_hash: str


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class User(Base):
    __tablename__ = "login"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    password_reset_time = Column(DateTime, nullable=True)