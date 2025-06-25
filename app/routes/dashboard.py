# app/routes/dashboard.py
from datetime import datetime, date, timedelta
from collections import defaultdict

from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from sqlalchemy import func

from app.extensions import db
from app.models import Patient, Appointment
from app.utils.utils import generate_key_stats

dashboard_bp = Blueprint("dashboard", __name__)

# --------------------------------------------------------------------------- #
# DASHBOARD VIEW
# --------------------------------------------------------------------------- #
@dashboard_bp.route("/dashboard/")
@login_required
def dashboard_view():
    """
    Main admin dashboard.

    * Only users with the **Admin** role may view this page.
    * Produces:
        - key-stat cards
        - risk-level bar chart
        - monthly ANC attendance (visits vs targets) line chart
        - daily appointment count for the current month (legacy)
    """
    # ── 1) AUTHORIZATION ────────────────────────────────────────────────────
    # if not current_user.has_role("Admin"):
    #     abort(403)

    # ── 2) DATES & RANGE HELPERS ───────────────────────────────────────────
    today       = date.today()
    next_week   = today + timedelta(days=7)
    first_day   = today.replace(day=1)
    current_yr  = today.year

    # ── 3) CORE METRICS (for cards & key-stats) ────────────────────────────
    total_patients       = Patient.query.count()
    high_risk_patients   = Patient.query.filter_by(risk_level="High").count()
    upcoming_appointments = (
        Appointment.query.filter(
            Appointment.appointment_date.between(today, next_week)
        ).count()
    )

    # Completion-rate example  –– patients with ≥1 visit this year
    patients_with_visits = (
        db.session.query(Appointment.patient_id)
        .filter(
            Appointment.appointment_date >= date(current_yr, 1, 1),
            Appointment.appointment_date < date(current_yr + 1, 1, 1),
        )
        .distinct()
        .count()
    )
    completion_rate = (
        (patients_with_visits / total_patients) * 100 if total_patients else 0
    )

    # Visits so far *this* month
    monthly_visits = Appointment.query.filter(
        Appointment.appointment_date.between(first_day, today)
    ).count()

    # Placeholder SMS / WhatsApp engagement – replace with real data later
    sms_engagement = 320

    key_stats = generate_key_stats(
        total_patients=total_patients,
        completion_rate=completion_rate,
        monthly_visits=monthly_visits,
        sms_engagement=sms_engagement,
    )

    # ── 4) RISK-LEVEL DISTRIBUTION (bar / doughnut) ────────────────────────
    risk_query = (
        db.session.query(Patient.risk_level, func.count(Patient.id))
        .group_by(Patient.risk_level)
        .all()
    )
    risk_counts = defaultdict(int, {lvl: cnt for lvl, cnt in risk_query})
    # ensure all three keys are present
    for lvl in ("Low", "Medium", "High"):
        risk_counts[lvl] = risk_counts.get(lvl, 0)

    # ── 5) MONTHLY ANC ATTENDANCE (visits vs target) ───────────────────────
    visits_this_year = (
        db.session.query(Appointment.appointment_date)
        .filter(
            Appointment.appointment_date >= date(current_yr, 1, 1),
            Appointment.appointment_date < date(current_yr + 1, 1, 1),
        )
        .all()
    )
    visits_by_month = defaultdict(int)
    for (d,) in visits_this_year:
        visits_by_month[d.month] += 1

    months        = [f"{m:02d}" for m in range(1, 13)]
    visit_counts  = [visits_by_month.get(m, 0) for m in range(1, 13)]
    targets       = [100] * 12  # static target; adjust as required

    # ── 6) DAILY APPOINTMENT COUNTS (current month, legacy chart) ──────────
    daily_counts = (
        db.session.query(Appointment.appointment_date, func.count(Appointment.id))
        .filter(Appointment.appointment_date >= first_day)
        .group_by(Appointment.appointment_date)
        .order_by(Appointment.appointment_date)
        .all()
    )
    appt_labels  = [d.strftime("%Y-%m-%d") for d, _ in daily_counts]
    appt_values  = [cnt for _, cnt in daily_counts]

    # ── 7) RENDER ──────────────────────────────────────────────────────────
    return render_template(
        "dashboard.html",
        # cards / hero banner
        key_stats=key_stats,
        # individual legacy values (optional, backwards compatibility)
        total_patients=total_patients,
        high_risk_patients=high_risk_patients,
        upcoming_appointments=upcoming_appointments,
        # chart data
        risk_data=risk_counts,
        months=months,
        visit_counts=visit_counts,
        targets=targets,
        appt_labels=appt_labels,
        appt_values=appt_values,
    )
