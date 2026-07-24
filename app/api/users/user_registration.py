import datetime

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.utils import token_generator
from app.utils.token_generator import require_auth, require_role

from app.modals.users import User, UserRegister, ChangePassword

load_dotenv()
router = APIRouter()

# Only an existing admin can create new staff logins. The first admin account
# is provisioned by migrating the pre-existing user row to the "admin" role
# (see add_role_column.py) rather than through this endpoint.
@router.post("/user/register/")
def register_user(user_register: UserRegister, db: Session = Depends(get_db),
                   user: dict = Depends(require_role("admin"))):
    try:
        existing_user = db.query(User).filter(User.username == user_register.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists for this username")
        new_user = User(
            username = user_register.username,
            password_hash = user_register.password_hash,
            password_reset_time = datetime.datetime.utcnow(),
            role = user_register.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User registered successfully, login again to proceed"}
    except HTTPException:
        raise
    except Exception as e:
        if "SQLDriverConnect" in str(e) or "Cannot open server" in str(e):
             raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/list/")
def list_users(db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    users = db.query(User).order_by(User.id).all()
    return {
        "status": "success",
        "data": [{"id": u.id, "username": u.username, "role": u.role} for u in users],
    }


@router.post("/user/login/")
def login_user(user_register: UserRegister, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(
            User.username == user_register.username,
            User.password_hash == user_register.password_hash
        ).first()
        if not existing_user:
            raise HTTPException(status_code=400, detail="Username, password is incorrect, "
                                                        "please retry or register as a new user")
        access_token = token_generator.create_access_token(
            data={"sub": existing_user.username, "user_id": existing_user.id, "role": existing_user.role},
            expires_delta=datetime.timedelta(hours=1)
        )
        return {
            "message": "User Logged in Successfully",
            "access_token": access_token,
            "role": existing_user.role,
        }
    except HTTPException:
        raise
    except Exception as e:
        if "SQLDriverConnect" in str(e) or "Cannot open server" in str(e):
             raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/user/change-password/")
def change_password(payload: ChangePassword, db: Session = Depends(get_db),
                     user: dict = Depends(require_auth)):
    try:
        existing_user = db.query(User).filter(User.id == user.get("user_id")).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        if existing_user.password_hash != payload.old_password:
            raise HTTPException(status_code=400, detail="Current password is incorrect")

        existing_user.password_hash = payload.new_password
        existing_user.password_reset_time = datetime.datetime.utcnow()
        db.commit()
        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        if "SQLDriverConnect" in str(e) or "Cannot open server" in str(e):
             raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
        raise HTTPException(status_code=500, detail=str(e))
