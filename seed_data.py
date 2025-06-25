# seed_data.py
from app import create_app, db
from app.models import Role, User

app = create_app()
with app.app_context():
    # -- 1. Roles ----------------------------------------
    role_admin  = Role.query.filter_by(name='Admin').first()  or Role(name='Admin')
    role_clinic = Role.query.filter_by(name='Clinician').first() or Role(name='Clinician')
    role_data   = Role.query.filter_by(name='DataOfficer').first() or Role(name='DataOfficer')
    db.session.add_all([role_admin, role_clinic, role_data])

    # -- 2. Admin user -----------------------------------
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@acms.local')
        admin.set_password('ChangeMe123!')
        admin.roles.append(role_admin)
        db.session.add(admin)
        print("🟢  Created default admin user (username=admin / password=ChangeMe123!)")

    db.session.commit()
    print("🟢  Seeding complete.")
