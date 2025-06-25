import csv
import os
from datetime import datetime, timedelta
from faker import Faker
from app import create_app
from app.models import db, Patient

fake = Faker()

# Initialize the app and app context
app = create_app()

def generate_mock_data(filename='mock_patients.csv', count=50):
    headers = [
        'name', 'age', 'phone', 'address',
        'lmp_date', 'risk_level', 'emergency_contact_name',
        'emergency_contact_phone'
    ]
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for _ in range(count):
            lmp = fake.date_between(start_date='-8M', end_date='today')
            risk = fake.random_element(elements=('Low', 'Moderate', 'High'))
            writer.writerow({
                'name': fake.name(),
                'age': fake.random_int(min=18, max=45),
                'phone': fake.phone_number(),
                'address': fake.address().replace("\n", ", "),
                'lmp_date': lmp.strftime('%Y-%m-%d'),
                'risk_level': risk,
                'emergency_contact_name': fake.name(),
                'emergency_contact_phone': fake.phone_number()
            })

def load_mock_data():
    with app.app_context():
        # Generate CSV file with fake patients
        generate_mock_data()

        with open('zim_mock_patients.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Check if patient with same phone exists
                existing = Patient.query.filter_by(phone=row['phone']).first()
                if not existing:
                    lmp = datetime.strptime(row['lmp_date'], '%Y-%m-%d')
                    next_appt = lmp + timedelta(weeks=4)
                    patient = Patient(
                        name=row['name'],
                        age=int(row['age']),
                        phone=row['phone'],
                        address=row['address'],
                        lmp_date=lmp,
                        risk_level=row['risk_level'],
                        emergency_contact_name=row['emergency_contact_name'],
                        emergency_contact_phone=row['emergency_contact_phone'],
                        next_appointment=next_appt
                    )
                    db.session.add(patient)
            db.session.commit()
        print("✅ 30 mock patients loaded into the database successfully.")

if __name__ == "__main__":
    load_mock_data()
