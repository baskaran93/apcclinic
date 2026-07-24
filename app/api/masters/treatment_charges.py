from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.modals.treatment_charges import TreatmentCharge, TreatmentChargeCreate
from app.utils.permissions import require_permission
from typing import List

router = APIRouter()

@router.post("/masters/treatment_charges/", response_model=dict)
def create_treatment_charge(charge: TreatmentChargeCreate, db: Session = Depends(get_db),
                             user: dict = Depends(require_permission("treatment_charges", "add"))):
    try:
        db_charge = TreatmentCharge(
            treatment_name=charge.treatment_name,
            cost=charge.cost,
            description=charge.description
        )
        db.add(db_charge)
        db.commit()
        db.refresh(db_charge)
        return {
            "id": db_charge.id,
            "treatment_name": db_charge.treatment_name,
            "cost": db_charge.cost,
            "description": db_charge.description,
            "message": "Treatment charge added successfully"
        }
    except Exception as e:
        db.rollback()
        error_str = str(e)
        if "SQLDriverConnect" in error_str or "Cannot open server" in error_str:
             raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
        raise HTTPException(status_code=500, detail=error_str)

@router.get("/masters/treatment_charges/", response_model=List[dict])
def get_treatment_charges(db: Session = Depends(get_db), user: dict = Depends(require_permission("treatment_charges", "view"))):
    try:
        charges = db.query(TreatmentCharge).all()
        return [
            {
                "id": charge.id,
                "treatment_name": charge.treatment_name,
                "cost": charge.cost,
                "description": charge.description
            }
            for charge in charges
        ]
    except Exception as e:
        error_str = str(e)
        if "SQLDriverConnect" in error_str or "Cannot open server" in error_str:
             raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
        raise HTTPException(status_code=500, detail=error_str)


@router.put("/masters/treatment_charges/{charge_id}/", response_model=dict)
def update_treatment_charge(charge_id: int, charge: TreatmentChargeCreate, db: Session = Depends(get_db),
                             user: dict = Depends(require_permission("treatment_charges", "edit"))):
    try:
        db_charge = db.query(TreatmentCharge).filter(TreatmentCharge.id == charge_id).first()
        if not db_charge:
            raise HTTPException(status_code=404, detail="Treatment charge not found")

        db_charge.treatment_name = charge.treatment_name
        db_charge.cost = charge.cost
        db_charge.description = charge.description

        db.commit()
        db.refresh(db_charge)
        return {
            "id": db_charge.id,
            "treatment_name": db_charge.treatment_name,
            "cost": db_charge.cost,
            "description": db_charge.description,
            "message": "Treatment charge updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_str = str(e)
        if "SQLDriverConnect" in error_str or "Cannot open server" in error_str:
             raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
        raise HTTPException(status_code=500, detail=error_str)


@router.delete("/masters/treatment_charges/{charge_id}/", response_model=dict)
def delete_treatment_charge(charge_id: int, db: Session = Depends(get_db),
                             user: dict = Depends(require_permission("treatment_charges", "delete"))):
    try:
        db_charge = db.query(TreatmentCharge).filter(TreatmentCharge.id == charge_id).first()
        if not db_charge:
            raise HTTPException(status_code=404, detail="Treatment charge not found")

        db.delete(db_charge)
        db.commit()
        return {"message": "Treatment charge deleted successfully", "id": charge_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_str = str(e)
        if "SQLDriverConnect" in error_str or "Cannot open server" in error_str:
             raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
        raise HTTPException(status_code=500, detail=error_str)
