# run.py

from app import create_app, db  # ✅ Use db from app package

app = create_app()

# Shell context so we can work with `flask shell`
@app.shell_context_processor
def make_shell_context():
    from app.models import User, Patient, Appointment
    return {'db': db, 'User': User, 'Patient': Patient, 'Appointment': Appointment}

if __name__ == '__main__':
    app.run(debug=True)
