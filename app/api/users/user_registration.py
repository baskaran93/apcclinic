import datetime

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.utils import token_generator

from app.modals.users import User, UserRegister

load_dotenv()
router = APIRouter()

@router.post("/user/register/")
def register_user(user_register: UserRegister, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(User.username == user_register.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists for this username")
        new_user = User(
            username = user_register.username,
            password_hash = user_register.password_hash,
            password_reset_time = datetime.datetime.utcnow()
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User registered successfully, login again to proceed"}
    except Exception as e:
        if "SQLDriverConnect" in str(e) or "Cannot open server" in str(e):
             raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
        raise HTTPException(status_code=500, detail=str(e))


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
            data={"sub": existing_user.username, "user_id": existing_user.id},
            expires_delta=datetime.timedelta(hours=1)
        )
        return {"message": "User Logged in Successfully", "access_token":access_token}
    except HTTPException:
        raise
    except Exception as e:
        if "SQLDriverConnect" in str(e) or "Cannot open server" in str(e):
             raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
        raise HTTPException(status_code=500, detail=str(e))
