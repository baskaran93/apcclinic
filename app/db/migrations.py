from sqlalchemy import text
from app.db.database import engine


def _column_exists(conn, table: str, column: str) -> bool:
    result = conn.execute(
        text(
            "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_NAME = :table AND COLUMN_NAME = :column"
        ),
        {"table": table, "column": column},
    ).scalar()
    return bool(result)


def run_startup_migrations():
    """
    Idempotent column additions for tables that predate a given column.

    Base.metadata.create_all() (see main.py) only creates missing tables,
    never alters existing ones, so new columns on existing tables need to be
    added explicitly. This runs on every startup and is safe to repeat.
    """
    with engine.begin() as conn:
        if not _column_exists(conn, "login", "role"):
            print("[MIGRATE] Adding 'role' column to login table")
            conn.execute(text("ALTER TABLE login ADD COLUMN role VARCHAR(20);"))
            conn.execute(text("UPDATE login SET role = 'admin' WHERE role IS NULL;"))
            conn.execute(text("ALTER TABLE login ALTER COLUMN role SET NOT NULL;"))
            conn.execute(text("ALTER TABLE login ALTER COLUMN role SET DEFAULT 'receptionist';"))

        if not _column_exists(conn, "login", "designation_id"):
            print("[MIGRATE] Adding 'designation_id' column to login table")
            conn.execute(text("ALTER TABLE login ADD COLUMN designation_id INTEGER;"))

        if not _column_exists(conn, "treatment_details", "assessment_file_name"):
            print("[MIGRATE] Adding assessment file columns to treatment_details table")
            conn.execute(text("ALTER TABLE treatment_details ADD COLUMN assessment_file_name VARCHAR(255);"))
            conn.execute(text("ALTER TABLE treatment_details ADD COLUMN assessment_file_base64 TEXT;"))

        if not _column_exists(conn, "patient_details", "alternative_number"):
            print("[MIGRATE] Adding 'alternative_number' column to patient_details table")
            conn.execute(text("ALTER TABLE patient_details ADD COLUMN alternative_number VARCHAR(15);"))

        _seed_referral_types_from_patients(conn)


def _seed_referral_types_from_patients(conn):
    """
    Backfills the referral_types master with any distinct mode_of_referral
    values already present in patient_details, so the master isn't empty
    the first time mode_of_referral becomes a select-from-master field.
    Skips names already in referral_types, so it's safe to run every startup.
    """
    existing = {
        row[0].strip().lower()
        for row in conn.execute(text("SELECT referral_type_name FROM referral_types")).fetchall()
    }
    distinct_referrals = conn.execute(
        text("SELECT DISTINCT mode_of_referral FROM patient_details WHERE mode_of_referral IS NOT NULL")
    ).fetchall()

    for row in distinct_referrals:
        name = row[0].strip()
        if name and name.lower() not in existing:
            print(f"[MIGRATE] Seeding referral type '{name}' from patient_details")
            conn.execute(
                text("INSERT INTO referral_types (referral_type_name) VALUES (:name)"),
                {"name": name},
            )
            existing.add(name.lower())
