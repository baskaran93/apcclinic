from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health_check import router as health_check
from app.api.users.user_registration import router as user_registration
from app.api.patient.patient_registration import router as patient_details
from app.api.patient.treatment_details import router as treatment_details
from app.api.patient.get_patient_list import router as patient_list
from app.api.masters.treatment_charges import router as treatment_charges

app = FastAPI(
    title="APC Clinic API",
    description="API for APC Clinic Management System",
    version="1.0.0",
)

@app.get("/")
def read_root():
    return {"message": "DoubleManda Backend is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health_check)
app.include_router(user_registration)
app.include_router(patient_details)
app.include_router(treatment_details)
app.include_router(patient_list)
app.include_router(treatment_charges)
