# app/routes/patients.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models import db, Patient
from datetime import datetime
from flask_login import login_required, current_user

patients_bp = Blueprint('patients', __name__)

# --- Utility Functions ---

def calculate_gestational_age(lmp_date):
    """Calculate gestational age in weeks from the last menstrual period (LMP)."""
    today = datetime.today().date()
    delta = today - lmp_date
    return round(delta.days / 7, 1)

def assess_risk(age, gestational_age_weeks):
    """Determine pregnancy risk level based on simple age and gestation logic."""
    if age < 18 or age > 35 or gestational_age_weeks > 40:
        return 'High'
    elif 18 <= age <= 35 and 20 <= gestational_age_weeks <= 40:
        return 'Medium'
    else:
        return 'Low'

# --- Patient List and Registration ---

@patients_bp.route('/patients', methods=['GET', 'POST'])
@login_required
def patients():
    # if not current_user.has_role('Admin') and not current_user.has_role('Nurse'):
    #     abort(403)

    if request.method == 'POST':
        try:
            # Collect and validate form data
            name = request.form['name']
            age = int(request.form['age'])
            phone = request.form['phone']
            address = request.form['address']
            lmp_date = datetime.strptime(request.form['lmp_date'], '%Y-%m-%d').date()
            emergency_contact_name = request.form['emergency_contact_name']
            emergency_contact_phone = request.form['emergency_contact_phone']

            # Derived fields
            gestational_age = calculate_gestational_age(lmp_date)
            risk_level = assess_risk(age, gestational_age)

            # Create and save new patient
            patient = Patient(
                name=name,
                age=age,
                phone=phone,
                address=address,
                lmp_date=lmp_date,
                emergency_contact_name=emergency_contact_name,
                emergency_contact_phone=emergency_contact_phone,
                gestational_age=gestational_age,
                risk_level=risk_level,
                visit_count=0
            )

            db.session.add(patient)
            db.session.commit()
            flash(f'Patient {name} registered successfully!', 'success')

        except Exception as e:
            flash('Error registering patient: ' + str(e), 'danger')

        return redirect(url_for('patients.patients'))

    # GET: show all patients, optionally filtered by name
    search_query = request.args.get('search', '')
    if search_query:
        patients = Patient.query.filter(Patient.name.ilike(f'%{search_query}%')).all()
    else:
        patients = Patient.query.all()

    return render_template('patients.html', patients=patients, search_query=search_query)

# --- Edit Patient ---

@patients_bp.route('/patients/edit/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        try:
            # Update patient details
            patient.name = request.form['name']
            patient.age = int(request.form['age'])
            patient.phone = request.form['phone']
            patient.address = request.form['address']
            patient.lmp_date = datetime.strptime(request.form['lmp_date'], '%Y-%m-%d').date()
            patient.emergency_contact_name = request.form['emergency_contact_name']
            patient.emergency_contact_phone = request.form['emergency_contact_phone']

            # Recalculate derived fields
            patient.gestational_age = calculate_gestational_age(patient.lmp_date)
            patient.risk_level = assess_risk(patient.age, patient.gestational_age)

            db.session.commit()
            flash('Patient updated successfully!', 'success')
        except Exception as e:
            flash('Error updating patient: ' + str(e), 'danger')

        return redirect(url_for('patients.patients'))

    return render_template('edit_patient.html', patient=patient)

# --- Delete Patient ---

@patients_bp.route('/patients/delete/<int:patient_id>', methods=['POST'])
@login_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    flash('Patient deleted successfully!', 'success')
    return redirect(url_for('patients.patients'))

# --- Log Visit ---

@patients_bp.route('/patients/visit/<int:patient_id>', methods=['POST'])
@login_required
def log_visit(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    patient.visit_count += 1
    db.session.commit()
    flash(f"Visit logged for {patient.name}.", "info")
    return redirect(url_for('patients.patients'))

