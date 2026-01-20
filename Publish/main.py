from fastapi import FastAPI
from app.api.health_check import router as health_check
from app.api.users.user_registration import router as user_registration
from app.api.patient.patient_registration import router as patient_details
from app.api.patient.treatment_details import router as treatment_details
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

app = FastAPI()
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_check)
app.include_router(user_registration)
app.include_router(patient_details)
app.include_router(treatment_details)
