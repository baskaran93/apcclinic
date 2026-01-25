from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.utils.token_generator import require_auth

router = APIRouter(
    prefix="/patient",
    tags=["Patient"],
)

security = HTTPBearer()

@router.get(
    "/list/",
    summary="Get Patient List",
    dependencies=[Security(security)],   # 🔥 THIS MAKES SWAGGER SHOW TOKEN BOX
)
def get_patient_list(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security),
    user: dict = Depends(require_auth),
):
    try:
        print("[INFO] Token received:", credentials.credentials)
        print("[INFO] Authenticated user:", user)

        result = db.execute(text("EXEC GetPatientList"))

        patients = []
        for row in result.mappings():
            patients.append(dict(row))

        return {
            "status": "success",
            "count": len(patients),
            "data": patients
        }

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
