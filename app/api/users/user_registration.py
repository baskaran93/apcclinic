import datetime

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.utils import token_generator
from app.utils.token_generator import require_auth, require_role

from app.modals.users import User, UserRegister, ChangePassword, UserUpdate
from app.modals.designation import Designation
from app.utils.password_hashing import hash_password, is_hashed, verify_password
from app.utils.error_handling import raise_db_error

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
        if user_register.designation_id is not None:
            designation = db.query(Designation).filter(Designation.id == user_register.designation_id).first()
            if not designation:
                raise HTTPException(status_code=400, detail="Invalid designation_id")
        new_user = User(
            username = user_register.username,
            password_hash = hash_password(user_register.password_hash),
            password_reset_time = datetime.datetime.utcnow(),
            role = user_register.role,
            designation_id = user_register.designation_id
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User registered successfully, login again to proceed"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise_db_error(e)


@router.get("/user/list/")
def list_users(db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    users = db.query(User).order_by(User.id).all()
    designations = {d.id: d.designation_name for d in db.query(Designation).all()}
    return {
        "status": "success",
        "data": [
            {
                "id": u.id,
                "username": u.username,
                "role": u.role,
                "designation_id": u.designation_id,
                "designation_name": designations.get(u.designation_id),
            }
            for u in users
        ],
    }


@router.put("/user/{user_id}/")
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db),
                 user: dict = Depends(require_role("admin"))):
    try:
        target = db.query(User).filter(User.id == user_id).first()
        if not target:
            raise HTTPException(status_code=404, detail="User not found")

        if payload.role is not None:
            target.role = payload.role
        # Use model_fields_set (not `is not None`) so an explicit null clears
        # the designation, while omitting the field entirely leaves it as-is.
        if "designation_id" in payload.model_fields_set:
            if payload.designation_id is not None:
                designation = db.query(Designation).filter(Designation.id == payload.designation_id).first()
                if not designation:
                    raise HTTPException(status_code=400, detail="Invalid designation_id")
            target.designation_id = payload.designation_id
        if payload.new_password:
            target.password_hash = hash_password(payload.new_password)
            target.password_reset_time = datetime.datetime.utcnow()

        db.commit()
        db.refresh(target)
        return {
            "message": "User updated successfully",
            "data": {
                "id": target.id,
                "username": target.username,
                "role": target.role,
                "designation_id": target.designation_id,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise_db_error(e)


@router.post("/user/login/")
def login_user(user_register: UserRegister, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(User.username == user_register.username).first()
        if not existing_user or not verify_password(user_register.password_hash, existing_user.password_hash):
            raise HTTPException(status_code=400, detail="Username, password is incorrect, "
                                                        "please retry or register as a new user")

        # Legacy rows predate hashing and still hold the raw password; a
        # successful legacy match is the only time we have the plaintext in
        # hand, so migrate the row to a bcrypt hash right here.
        if not is_hashed(existing_user.password_hash):
            existing_user.password_hash = hash_password(user_register.password_hash)
            db.commit()

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
        db.rollback()
        raise_db_error(e)


@router.post("/user/change-password/")
def change_password(payload: ChangePassword, db: Session = Depends(get_db),
                     user: dict = Depends(require_auth)):
    try:
        existing_user = db.query(User).filter(User.id == user.get("user_id")).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(payload.old_password, existing_user.password_hash):
            raise HTTPException(status_code=400, detail="Current password is incorrect")

        existing_user.password_hash = hash_password(payload.new_password)
        existing_user.password_reset_time = datetime.datetime.utcnow()
        db.commit()
        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise_db_error(e)
