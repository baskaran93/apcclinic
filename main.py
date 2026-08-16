from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health_check import router as health_check
from app.api.users.user_registration import router as user_registration
from app.api.patient.patient_registration import router as patient_details
from app.api.patient.treatment_details import router as treatment_details
from app.api.patient.get_patient_list import router as patient_list
from app.api.masters.treatment_charges import router as treatment_charges
from app.api.masters.designation import router as designation_master
from app.api.masters.referral_type import router as referral_type_master
from app.api.masters.expense_type import router as expense_type_master
from app.api.expenses.office_expense import router as office_expenses
from app.api.appointments.appointment import router as appointments
from app.api.enquiry.enquiry import router as enquiry
from app.api.dashboard.summary import router as dashboard_summary
from app.api.permissions.role_permissions import router as role_permissions

app = FastAPI(
    title="APC Clinic API",
    description="API for APC Clinic Management System",
    version="1.0.0",
)

@app.on_event("startup")
def startup_event():
    print("[INFO] Creating database tables if they do not exist...")
    try:
        from app.modals.users import User
        from app.modals.patient_details import PatientDetails, TreatmentDetails, TreatmentItem
        from app.modals.treatment_charges import TreatmentCharge
        from app.modals.designation import Designation
        from app.modals.referral_type import ReferralType
        from app.modals.expense_type import ExpenseType
        from app.modals.office_expense import OfficeExpense
        from app.modals.appointment import Appointment
        from app.modals.enquiry import Enquiry
        from app.modals.role_permission import RolePermission
        from app.db.database import engine, Base
        Base.metadata.create_all(bind=engine)
        print("[INFO] Database tables checked/created successfully.")

        from app.db.migrations import run_startup_migrations
        run_startup_migrations()
        print("[INFO] Startup migrations checked/applied successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to create tables: {e}")
        import traceback
        traceback.print_exc()

@app.get("/")
def read_root():
    return {"message": "Backend is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

# CORS: auth is Bearer-token based (no cookies), so credentials aren't
# needed here. allow_credentials=True combined with a wildcard origin is
# invalid per the CORS spec and was never actually required.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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
app.include_router(designation_master)
app.include_router(referral_type_master)
app.include_router(expense_type_master)
app.include_router(office_expenses)
app.include_router(appointments)
app.include_router(enquiry)
app.include_router(dashboard_summary)
app.include_router(role_permissions)
