"""
Help functions to use from command line to setup authentication database and users.
"""
import os
from . import db, app, User
from werkzeug.security import generate_password_hash
from getpass import getpass

FLASK_ROOT=os.path.abspath(os.path.dirname(__file__))

def create_database():
    with app.app_context():
        db.create_all()

def add_user(name, email, admin=False, password=None):
    with app.app_context():
        user = User.query.filter_by(email=email).first()

        if user:
            print("User with email %s already exists"%email)
            return

        if password is None:
            password=getpass('Password:')
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'),
                        admin=admin)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

def generate_secret():
    # create a random secret key for the application
    # WARNING: this key file should never be checked into the git repository
    open(os.path.join(FLASK_ROOT, 'secret.key'), 'wb').write(os.urandom(16))

def initial_setup():
    # Generate initial credential setup
    if os.path.exists(os.path.join(FLASK_ROOT, 'db.sqlite')):
        print("Removing old authentication database.")
        os.remove(os.path.join(FLASK_ROOT, 'db.sqlite'))
    print("Generating new secret key.")
    generate_secret()
    print("Setup new databse.")
    create_database()
    print("Create initial user initial.admin@orso.org (pw=ORSO4all).\n"
          "Please remove after adding the first real user!")
    add_user('initial_admin', 'initial.admin@orso.org', admin=True, password='ORSO4all')

if __name__=='__main__':
    # when run as script, generate initial setup
    initial_setup()
