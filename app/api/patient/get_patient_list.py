from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.utils.token_generator import require_auth
from app.modals.patient_details import PatientDetails

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

        patients_query = db.query(PatientDetails).order_by(PatientDetails.registeration_date.desc()).all()

        patients = []
        for p in patients_query:
            patients.append({
                "id": p.id,
                "name": p.name,
                "phone_number": p.phone_number,
                "age": p.age,
                "address": p.address,
                "city": p.city,
                "pincode": p.pincode,
                "mode_of_referral": p.mode_of_referral,
                "registeration_date": p.registeration_date
            })

        return {
            "status": "success",
            "count": len(patients),
            "data": patients
        }

    except Exception as e:
        error_str = str(e)
        print(f"[ERROR] {error_str}")
        if "SQLDriverConnect" in error_str or "Cannot open server" in error_str:
             raise HTTPException(status_code=503, detail="Database connection failed. Please check firewall settings.")
        raise HTTPException(
            status_code=500,
            detail=error_str
        )
