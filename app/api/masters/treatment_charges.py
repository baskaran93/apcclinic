from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.modals.treatment_charges import TreatmentCharge, TreatmentChargeCreate
from typing import List

router = APIRouter()

@router.post("/masters/treatment_charges/", response_model=dict)
def create_treatment_charge(charge: TreatmentChargeCreate, db: Session = Depends(get_db)):
    db_charge = TreatmentCharge(
        treatment_name=charge.treatment_name,
        cost=charge.cost,
        description=charge.description
    )
    db.add(db_charge)
    db.commit()
    db.refresh(db_charge)
    return {"message": "Treatment charge added successfully", "id": db_charge.id}

@router.get("/masters/treatment_charges/", response_model=List[dict])
def get_treatment_charges(db: Session = Depends(get_db)):
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
