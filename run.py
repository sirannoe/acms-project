# run.py

from app import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

# Shell context for `flask shell`
@app.shell_context_processor
def make_shell_context():
    from app.models import User, Patient, Appointment
    return {'db': db, 'User': User, 'Patient': Patient, 'Appointment': Appointment}

# Only run locally; Render will use gunicorn
if __name__ == '__main__':
    app.run(debug=True)
