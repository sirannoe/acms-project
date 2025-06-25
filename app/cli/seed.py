import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models import Role, User

@click.command("seed")
@with_appcontext
def seed():
    # roles
    for name in ("Admin", "Nurse"):
        Role.query.filter_by(name=name).first() or db.session.add(Role(name=name))
    db.session.commit()

    # admin user if absent
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", email="admin@example.com")
        admin.set_password("password")
        admin.roles.append(Role.query.filter_by(name="Admin").first())
        db.session.add(admin); db.session.commit()
        click.echo("Created default admin / password")
    else:
        click.echo("Admin already exists")
