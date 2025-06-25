# app/utils/forms.py

from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, StringField, SubmitField
from wtforms.validators import DataRequired

class AppointmentForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    appointment_date = DateField('Appointment Date', format='%Y-%m-%d', validators=[DataRequired()])
    reason = StringField('Reason for Appointment', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('Scheduled', 'Scheduled'),
        ('Confirmed', 'Confirmed'),
        ('Pending', 'Pending')
    ], validators=[DataRequired()])
    submit = SubmitField('Schedule Appointment')

class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')