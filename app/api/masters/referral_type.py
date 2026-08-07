from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.modals.referral_type import ReferralType, ReferralTypeCreate
from app.utils.token_generator import require_role
from app.utils.error_handling import raise_db_error
from typing import List

router = APIRouter()

@router.post("/masters/referral_types/", response_model=dict)
def create_referral_type(referral_type: ReferralTypeCreate, db: Session = Depends(get_db),
                          user: dict = Depends(require_role("admin"))):
    try:
        db_referral_type = ReferralType(
            referral_type_name=referral_type.referral_type_name,
            description=referral_type.description
        )
        db.add(db_referral_type)
        db.commit()
        db.refresh(db_referral_type)
        return {
            "id": db_referral_type.id,
            "referral_type_name": db_referral_type.referral_type_name,
            "description": db_referral_type.description,
            "message": "Referral type added successfully"
        }
    except Exception as e:
        db.rollback()
        raise_db_error(e)

@router.get("/masters/referral_types/", response_model=List[dict])
def get_referral_types(db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    try:
        referral_types = db.query(ReferralType).order_by(ReferralType.referral_type_name.asc()).all()
        return [
            {
                "id": r.id,
                "referral_type_name": r.referral_type_name,
                "description": r.description
            }
            for r in referral_types
        ]
    except Exception as e:
        raise_db_error(e)


@router.put("/masters/referral_types/{referral_type_id}/", response_model=dict)
def update_referral_type(referral_type_id: int, referral_type: ReferralTypeCreate, db: Session = Depends(get_db),
                          user: dict = Depends(require_role("admin"))):
    try:
        db_referral_type = db.query(ReferralType).filter(ReferralType.id == referral_type_id).first()
        if not db_referral_type:
            raise HTTPException(status_code=404, detail="Referral type not found")

        db_referral_type.referral_type_name = referral_type.referral_type_name
        db_referral_type.description = referral_type.description

        db.commit()
        db.refresh(db_referral_type)
        return {
            "id": db_referral_type.id,
            "referral_type_name": db_referral_type.referral_type_name,
            "description": db_referral_type.description,
            "message": "Referral type updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise_db_error(e)


@router.delete("/masters/referral_types/{referral_type_id}/", response_model=dict)
def delete_referral_type(referral_type_id: int, db: Session = Depends(get_db),
                          user: dict = Depends(require_role("admin"))):
    try:
        db_referral_type = db.query(ReferralType).filter(ReferralType.id == referral_type_id).first()
        if not db_referral_type:
            raise HTTPException(status_code=404, detail="Referral type not found")

        db.delete(db_referral_type)
        db.commit()
        return {"message": "Referral type deleted successfully", "id": referral_type_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise_db_error(e)
