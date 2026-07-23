from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health_check import router as health_check
from app.api.users.user_registration import router as user_registration
from app.api.patient.patient_registration import router as patient_details
from app.api.patient.treatment_details import router as treatment_details
from app.api.patient.get_patient_list import router as patient_list
from app.api.masters.treatment_charges import router as treatment_charges
from app.api.appointments.appointment import router as appointments
from app.api.dashboard.summary import router as dashboard_summary

app = FastAPI(
    title="APC Clinic API",
    description="API for APC Clinic Management System",
    version="1.0.0",
)

@app.on_event("startup")
def startup_event():
    print("[INFO] Creating database tables if they do not exist...")
    from app.modals.users import User
    from app.modals.patient_details import PatientDetails, TreatmentDetails, TreatmentItem
    from app.modals.treatment_charges import TreatmentCharge
    from app.modals.appointment import Appointment
    from app.db.database import engine, Base
    Base.metadata.create_all(bind=engine)
    print("[INFO] Database tables checked/created successfully.")

@app.get("/")
def read_root():
    return {"message": "Backend is running"}

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
app.include_router(appointments)
app.include_router(dashboard_summary)
