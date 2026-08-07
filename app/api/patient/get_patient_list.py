from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.utils.permissions import require_permission
from app.utils.error_handling import raise_db_error
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
    user: dict = Depends(require_permission("patients", "view")),
):
    try:
        patients_query = db.query(PatientDetails).order_by(PatientDetails.registeration_date.desc()).all()

        patients = []
        for p in patients_query:
            patients.append({
                "id": p.id,
                "name": p.name,
                "phone_number": p.phone_number,
                "alternative_number": p.alternative_number,
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
        raise_db_error(e)
