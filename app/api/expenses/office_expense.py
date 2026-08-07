import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.database import get_db
from app.modals.office_expense import OfficeExpense, OfficeExpenseCreate
from app.utils.token_generator import require_role
from app.utils.error_handling import raise_db_error

router = APIRouter()


def _serialize(e: OfficeExpense):
    return {
        "id": e.id,
        "expense_date": e.expense_date.strftime("%Y-%m-%d"),
        "description": e.description,
        "amount": e.amount,
        "remarks": e.remarks,
    }


def _parse_date(value: str) -> datetime.datetime:
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format, expected YYYY-MM-DD")


@router.post("/office_expenses/", response_model=dict)
def create_office_expense(expense: OfficeExpenseCreate, db: Session = Depends(get_db),
                           user: dict = Depends(require_role("admin"))):
    try:
        db_expense = OfficeExpense(
            expense_date=_parse_date(expense.expense_date),
            description=expense.description,
            amount=expense.amount,
            remarks=expense.remarks,
        )
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        result = _serialize(db_expense)
        result["message"] = "Expense added successfully"
        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise_db_error(e)


@router.get("/office_expenses/", response_model=list)
def get_office_expenses(db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    try:
        expenses = db.query(OfficeExpense).order_by(desc(OfficeExpense.expense_date), desc(OfficeExpense.id)).all()
        return [_serialize(e) for e in expenses]
    except Exception as e:
        raise_db_error(e)


@router.put("/office_expenses/{expense_id}/", response_model=dict)
def update_office_expense(expense_id: int, expense: OfficeExpenseCreate, db: Session = Depends(get_db),
                           user: dict = Depends(require_role("admin"))):
    try:
        db_expense = db.query(OfficeExpense).filter(OfficeExpense.id == expense_id).first()
        if not db_expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        db_expense.expense_date = _parse_date(expense.expense_date)
        db_expense.description = expense.description
        db_expense.amount = expense.amount
        db_expense.remarks = expense.remarks

        db.commit()
        db.refresh(db_expense)
        result = _serialize(db_expense)
        result["message"] = "Expense updated successfully"
        return result
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise_db_error(e)


@router.delete("/office_expenses/{expense_id}/", response_model=dict)
def delete_office_expense(expense_id: int, db: Session = Depends(get_db),
                           user: dict = Depends(require_role("admin"))):
    try:
        db_expense = db.query(OfficeExpense).filter(OfficeExpense.id == expense_id).first()
        if not db_expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        db.delete(db_expense)
        db.commit()
        return {"message": "Expense deleted successfully", "id": expense_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise_db_error(e)
