from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.modals.designation import Designation, DesignationCreate
from app.utils.token_generator import require_role
from typing import List

router = APIRouter()

@router.post("/masters/designations/", response_model=dict)
def create_designation(designation: DesignationCreate, db: Session = Depends(get_db),
                        user: dict = Depends(require_role("admin"))):
    try:
        db_designation = Designation(
            designation_name=designation.designation_name,
            description=designation.description
        )
        db.add(db_designation)
        db.commit()
        db.refresh(db_designation)
        return {
            "id": db_designation.id,
            "designation_name": db_designation.designation_name,
            "description": db_designation.description,
            "message": "Designation added successfully"
        }
    except Exception as e:
        db.rollback()
        error_str = str(e)
        if "SQLDriverConnect" in error_str or "Cannot open server" in error_str:
             raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
        raise HTTPException(status_code=500, detail=error_str)

@router.get("/masters/designations/", response_model=List[dict])
def get_designations(db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    try:
        designations = db.query(Designation).all()
        return [
            {
                "id": d.id,
                "designation_name": d.designation_name,
                "description": d.description
            }
            for d in designations
        ]
    except Exception as e:
        error_str = str(e)
        if "SQLDriverConnect" in error_str or "Cannot open server" in error_str:
             raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
        raise HTTPException(status_code=500, detail=error_str)


@router.put("/masters/designations/{designation_id}/", response_model=dict)
def update_designation(designation_id: int, designation: DesignationCreate, db: Session = Depends(get_db),
                        user: dict = Depends(require_role("admin"))):
    try:
        db_designation = db.query(Designation).filter(Designation.id == designation_id).first()
        if not db_designation:
            raise HTTPException(status_code=404, detail="Designation not found")

        db_designation.designation_name = designation.designation_name
        db_designation.description = designation.description

        db.commit()
        db.refresh(db_designation)
        return {
            "id": db_designation.id,
            "designation_name": db_designation.designation_name,
            "description": db_designation.description,
            "message": "Designation updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_str = str(e)
        if "SQLDriverConnect" in error_str or "Cannot open server" in error_str:
             raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
        raise HTTPException(status_code=500, detail=error_str)


@router.delete("/masters/designations/{designation_id}/", response_model=dict)
def delete_designation(designation_id: int, db: Session = Depends(get_db),
                        user: dict = Depends(require_role("admin"))):
    try:
        db_designation = db.query(Designation).filter(Designation.id == designation_id).first()
        if not db_designation:
            raise HTTPException(status_code=404, detail="Designation not found")

        db.delete(db_designation)
        db.commit()
        return {"message": "Designation deleted successfully", "id": designation_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_str = str(e)
        if "SQLDriverConnect" in error_str or "Cannot open server" in error_str:
             raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
        raise HTTPException(status_code=500, detail=error_str)
