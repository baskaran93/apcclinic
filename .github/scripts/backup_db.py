"""
Dumps the production Postgres database with pg_dump and emails the
resulting file as an attachment. Runs on a weekly schedule from
.github/workflows/weekly-db-backup.yml, on GitHub's infrastructure
rather than the app server, so it fires reliably even if the backend
is asleep (e.g. Render free tier spin-down).
"""

import os
import smtplib
import ssl
import subprocess
import sys
from datetime import datetime, timezone
from email.message import EmailMessage

MAX_ATTACHMENT_BYTES = 24 * 1024 * 1024  # stay under Gmail's 25MB limit


def run_pg_dump(database_url: str, out_path: str) -> None:
    result = subprocess.run(
        ["pg_dump", "--no-owner", "--no-privileges", "-Fc", "-f", out_path, database_url],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("pg_dump failed:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)


def send_backup_email(smtp_user: str, smtp_password: str, recipient: str, dump_path: str, size_mb: float) -> None:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    dump_filename = os.path.basename(dump_path)

    msg = EmailMessage()
    msg["Subject"] = f"APC Clinic DB Backup - {today}"
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg.set_content(
        "Weekly database backup for APC Clinic.\n\n"
        f"File: {dump_filename}\n"
        f"Size: {size_mb:.2f} MB\n\n"
        "Restore with:\n"
        f"  pg_restore --no-owner --clean --if-exists -d <DATABASE_URL> {dump_filename}\n"
    )

    with open(dump_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename=dump_filename)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(smtp_user, smtp_password)
        server.send_message(msg)


def main() -> None:
    database_url = os.environ["BACKUP_DATABASE_URL"]
    smtp_user = os.environ["BACKUP_SMTP_USER"]
    smtp_password = os.environ["BACKUP_SMTP_PASSWORD"]
    recipient = os.environ["BACKUP_EMAIL_TO"]

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    dump_path = f"apcclinic_backup_{today}.dump"

    print(f"Dumping database to {dump_path} ...")
    run_pg_dump(database_url, dump_path)

    size_mb = os.path.getsize(dump_path) / (1024 * 1024)
    print(f"Dump created: {dump_path} ({size_mb:.2f} MB)")

    if os.path.getsize(dump_path) > MAX_ATTACHMENT_BYTES:
        print(
            f"ERROR: backup is {size_mb:.2f} MB, over the ~25MB email attachment limit. "
            "Switch to uploading it somewhere (e.g. cloud storage) instead of emailing it directly.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Emailing backup to {recipient} ...")
    send_backup_email(smtp_user, smtp_password, recipient, dump_path, size_mb)
    print("Backup email sent successfully.")


if __name__ == "__main__":
    main()
