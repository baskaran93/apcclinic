from app.db.database import Base
from pydantic import BaseModel, field_validator
from sqlalchemy import Boolean, Column, Integer, String, UniqueConstraint

CONFIGURABLE_ROLES = ("doctor", "receptionist")
MENUS = ("patients", "appointments", "treatment_charges", "patient_treatment")


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(20), nullable=False)
    menu = Column(String(30), nullable=False)
    can_view = Column(Boolean, nullable=False, default=False)
    can_add = Column(Boolean, nullable=False, default=False)
    can_edit = Column(Boolean, nullable=False, default=False)
    can_delete = Column(Boolean, nullable=False, default=False)

    __table_args__ = (UniqueConstraint("role", "menu", name="uq_role_menu"),)


class RolePermissionUpdate(BaseModel):
    role: str
    menu: str
    can_view: bool = False
    can_add: bool = False
    can_edit: bool = False
    can_delete: bool = False

    @field_validator("role")
    @classmethod
    def validate_role(cls, value):
        if value not in CONFIGURABLE_ROLES:
            raise ValueError(f"role must be one of {CONFIGURABLE_ROLES}")
        return value

    @field_validator("menu")
    @classmethod
    def validate_menu(cls, value):
        if value not in MENUS:
            raise ValueError(f"menu must be one of {MENUS}")
        return value
