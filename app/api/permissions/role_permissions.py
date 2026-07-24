from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.modals.role_permission import CONFIGURABLE_ROLES, MENUS, RolePermission, RolePermissionUpdate
from app.utils.token_generator import require_auth, require_role

router = APIRouter(prefix="/permissions", tags=["Permissions"])


def _serialize(perm=None, role=None, menu=None):
    if perm:
        return {
            "role": perm.role,
            "menu": perm.menu,
            "can_view": perm.can_view,
            "can_add": perm.can_add,
            "can_edit": perm.can_edit,
            "can_delete": perm.can_delete,
        }
    return {
        "role": role,
        "menu": menu,
        "can_view": False,
        "can_add": False,
        "can_edit": False,
        "can_delete": False,
    }


@router.get("/")
def list_permissions(db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    """Full role x menu matrix (admin only), missing rows default to all-False."""
    existing = {(p.role, p.menu): p for p in db.query(RolePermission).all()}
    data = [
        _serialize(existing.get((role, menu)), role, menu)
        for role in CONFIGURABLE_ROLES
        for menu in MENUS
    ]
    return {"status": "success", "data": data}


@router.put("/")
def update_permission(payload: RolePermissionUpdate, db: Session = Depends(get_db),
                       user: dict = Depends(require_role("admin"))):
    """Upsert a single role+menu permission row (admin only)."""
    perm = db.query(RolePermission).filter(
        RolePermission.role == payload.role,
        RolePermission.menu == payload.menu,
    ).first()
    if not perm:
        perm = RolePermission(role=payload.role, menu=payload.menu)
        db.add(perm)

    perm.can_view = payload.can_view
    perm.can_add = payload.can_add
    perm.can_edit = payload.can_edit
    perm.can_delete = payload.can_delete

    db.commit()
    db.refresh(perm)
    return {"status": "success", "data": _serialize(perm)}


@router.get("/me/")
def my_permissions(db: Session = Depends(get_db), user: dict = Depends(require_auth)):
    """Effective permissions for the current user, used by the app to gate the UI."""
    role = user.get("role")

    if role == "admin":
        data = {menu: {"can_view": True, "can_add": True, "can_edit": True, "can_delete": True} for menu in MENUS}
        return {"status": "success", "role": role, "data": data}

    rows = {p.menu: p for p in db.query(RolePermission).filter(RolePermission.role == role).all()}
    data = {}
    for menu in MENUS:
        p = rows.get(menu)
        data[menu] = {
            "can_view": p.can_view if p else False,
            "can_add": p.can_add if p else False,
            "can_edit": p.can_edit if p else False,
            "can_delete": p.can_delete if p else False,
        }
    return {"status": "success", "role": role, "data": data}
