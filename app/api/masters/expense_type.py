from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.modals.expense_type import ExpenseType, ExpenseTypeCreate
from app.utils.token_generator import require_role
from app.utils.error_handling import raise_db_error
from typing import List

router = APIRouter()

@router.post("/masters/expense_types/", response_model=dict)
def create_expense_type(expense_type: ExpenseTypeCreate, db: Session = Depends(get_db),
                         user: dict = Depends(require_role("admin"))):
    try:
        db_expense_type = ExpenseType(
            expense_type_name=expense_type.expense_type_name,
            description=expense_type.description
        )
        db.add(db_expense_type)
        db.commit()
        db.refresh(db_expense_type)
        return {
            "id": db_expense_type.id,
            "expense_type_name": db_expense_type.expense_type_name,
            "description": db_expense_type.description,
            "message": "Expense type added successfully"
        }
    except Exception as e:
        db.rollback()
        raise_db_error(e)

@router.get("/masters/expense_types/", response_model=List[dict])
def get_expense_types(db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    try:
        expense_types = db.query(ExpenseType).order_by(ExpenseType.expense_type_name.asc()).all()
        return [
            {"id": e.id, "expense_type_name": e.expense_type_name, "description": e.description}
            for e in expense_types
        ]
    except Exception as e:
        raise_db_error(e)


@router.put("/masters/expense_types/{expense_type_id}/", response_model=dict)
def update_expense_type(expense_type_id: int, expense_type: ExpenseTypeCreate, db: Session = Depends(get_db),
                         user: dict = Depends(require_role("admin"))):
    try:
        db_expense_type = db.query(ExpenseType).filter(ExpenseType.id == expense_type_id).first()
        if not db_expense_type:
            raise HTTPException(status_code=404, detail="Expense type not found")

        db_expense_type.expense_type_name = expense_type.expense_type_name
        db_expense_type.description = expense_type.description

        db.commit()
        db.refresh(db_expense_type)
        return {
            "id": db_expense_type.id,
            "expense_type_name": db_expense_type.expense_type_name,
            "description": db_expense_type.description,
            "message": "Expense type updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise_db_error(e)


@router.delete("/masters/expense_types/{expense_type_id}/", response_model=dict)
def delete_expense_type(expense_type_id: int, db: Session = Depends(get_db),
                         user: dict = Depends(require_role("admin"))):
    try:
        db_expense_type = db.query(ExpenseType).filter(ExpenseType.id == expense_type_id).first()
        if not db_expense_type:
            raise HTTPException(status_code=404, detail="Expense type not found")

        db.delete(db_expense_type)
        db.commit()
        return {"message": "Expense type deleted successfully", "id": expense_type_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise_db_error(e)
