from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.modals.role_permission import RolePermission
from app.utils.token_generator import require_auth


def require_permission(menu: str, action: str):
    """
    Dependency factory for menu-scoped CRUD authorization.
    Admin always passes. Other roles must have an explicit
    can_<action> = True row in role_permissions for this menu
    (default-deny: no row means no access).
    """
    def checker(user: dict = Depends(require_auth), db: Session = Depends(get_db)):
        role = user.get("role")
        if role == "admin":
            return user

        perm = db.query(RolePermission).filter(
            RolePermission.role == role,
            RolePermission.menu == menu,
        ).first()
        allowed = getattr(perm, f"can_{action}", False) if perm else False
        if not allowed:
            raise HTTPException(status_code=403, detail="You do not have permission to perform this action")
        return user

    return checker
