# app/routes/appointments.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import db, Appointment, Patient
from datetime import datetime
from app.utils.sms import send_sms
from flask_login import login_required

appointments_bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@appointments_bp.route('/')
@login_required
def appointments():
    # Get search and filter params from URL query string
    search_query = request.args.get('search', '', type=str).strip()
    status_filter = request.args.get('status', '', type=str).strip()

    # Base query joining Patient (to filter by patient name)
    query = Appointment.query.join(Patient)

    if search_query:
        query = query.filter(Patient.name.ilike(f'%{search_query}%'))
    if status_filter:
        query = query.filter(Appointment.status == status_filter)

    all_appointments = query.order_by(Appointment.appointment_date).all()

    return render_template(
        'appointments.html',
        appointments=all_appointments,
        search_query=search_query,
        status_filter=status_filter
    )


@appointments_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_appointment():
    if request.method == 'POST':
        try:
            patient_id = int(request.form['patient_id'])
            date = datetime.strptime(request.form['appointment_date'], '%Y-%m-%d').date()
            reason = request.form.get('reason', '').strip()
            status = request.form.get('status', 'Scheduled')

            new_appt = Appointment(
                patient_id=patient_id,
                appointment_date=date,
                reason=reason,
                status=status
            )
            db.session.add(new_appt)
            db.session.commit()
            flash('Appointment scheduled successfully.', 'success')
            return redirect(url_for('appointments.appointments'))
        
            # After saving appointment to the database
            message = f"Dear {patient.full_name}, your ANC appointment is scheduled for {appointment.appointment_date.strftime('%d %b %Y')}."
            send_sms(patient.phone_number, message)
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}", 'danger')

    patients = Patient.query.all()
    return render_template('create_appointment.html', patients=patients)


@appointments_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_appointment(id):
    appointment = Appointment.query.get_or_404(id)

    if request.method == 'POST':
        try:
            appointment.patient_id = int(request.form['patient_id'])
            appointment.appointment_date = datetime.strptime(
                request.form['appointment_date'], '%Y-%m-%d').date()
            appointment.reason = request.form.get('reason', '').strip()
            appointment.status = request.form.get('status', 'Scheduled')

            db.session.commit()
            flash('Appointment updated successfully.', 'success')
            return redirect(url_for('appointments.appointments'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}", 'danger')

    patients = Patient.query.all()
    return render_template('edit_appointment.html', appointment=appointment, patients=patients)


@appointments_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    try:
        db.session.delete(appointment)
        db.session.commit()
        flash('Appointment deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting appointment: {e}", 'danger')
    return redirect(url_for('appointments.appointments'))


@appointments_bp.route('/calendar/events')
@login_required
def calendar_events():
    # Return JSON list of events for FullCalendar
    appts = Appointment.query.all()
    events = []
    for appt in appts:
        events.append({
            'id': appt.id,
            'title': f"{appt.patient.name} - {appt.reason or 'No reason'}",
            'start': appt.appointment_date.isoformat(),
            'url': url_for('appointments.edit_appointment', id=appt.id)
        })
    return jsonify(events)

@appointments_bp.route('/calendar')
@login_required
def calendar_view():
    return render_template('calendar.html')
