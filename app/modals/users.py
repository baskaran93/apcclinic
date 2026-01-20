from sqlalchemy.orm import declarative_base
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime

BASE = declarative_base()

class UserRegister(BaseModel):
    username: str
    password_hash: str


class User(BASE):
    __tablename__ = "login"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    password_reset_time = Column(DateTime, nullable=True)