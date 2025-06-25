# app/routes/reports.py
from flask import (
    Blueprint, render_template, send_file, Response, abort, current_app
)
from app.models import Patient, Appointment
from app.extensions import db
from flask_login import login_required, current_user
import csv, io
from datetime import datetime

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

# ──────────────────────────────────────────────────────────────────────────
def _admin_or_nurse():
    if not current_user.is_authenticated or (
        not current_user.has_role("Admin") and not current_user.has_role("Nurse")
    ):
        abort(403)

def _csv_response(filename: str, rows, header):
    """Helper: wrap iterable rows -> CSV download"""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)
    writer.writerows(rows)
    output = buf.getvalue()
    buf.close()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

# ──────────────────────────────────────────────────────────────────────────
@reports_bp.route("/")
@login_required
def index():
    _admin_or_nurse()
    # quick counts just for the cards
    total_patients   = Patient.query.count()
    high_risk        = Patient.query.filter_by(risk_level="High").count()
    total_appointments = Appointment.query.count()
    return render_template(
        "reports/index.html",
        total_patients=total_patients,
        high_risk=high_risk,
        total_appointments=total_appointments,
    )

# ---- CSV ENDPOINTS -------------------------------------------------------
@reports_bp.route("/patients.csv")
@login_required
def patients_csv():
    _admin_or_nurse()
    rows = [
        (
            p.id,
            p.name,
            p.age,
            p.phone,
            p.risk_level,
            p.visit_count,
            p.lmp_date.strftime("%Y-%m-%d"),
        )
        for p in Patient.query.order_by(Patient.name).all()
    ]
    header = [
        "ID",
        "Name",
        "Age",
        "Phone",
        "Risk level",
        "Visits",
        "LMP date",
    ]
    return _csv_response("patients.csv", rows, header)


@reports_bp.route("/appointments.csv")
@login_required
def appointments_csv():
    _admin_or_nurse()
    rows = [
        (
            a.id,
            a.patient.name,
            a.appointment_date.strftime("%Y-%m-%d"),
            a.reason or "",
            a.status,
        )
        for a in Appointment.query.order_by(Appointment.appointment_date).all()
    ]
    header = ["ID", "Patient", "Date", "Reason", "Status"]
    return _csv_response("appointments.csv", rows, header)


@reports_bp.route("/high_risk.csv")
@login_required
def high_risk_csv():
    _admin_or_nurse()
    rows = [
        (p.id, p.name, p.age, p.phone, p.visit_count)
        for p in Patient.query.filter_by(risk_level="High").all()
    ]
    header = ["ID", "Name", "Age", "Phone", "Visits"]
    return _csv_response("high_risk_patients.csv", rows, header)
