"""
Help functions to use from command line to setup authentication database and users.
"""
import os
from . import db, app, User
from werkzeug.security import generate_password_hash
from getpass import getpass

def create_database():
    with app.app_context():
        db.create_all()

def add_user(name, email, admin=False):
    with app.app_context():
        user = User.query.filter_by(email=email).first()

        if user:
            print("User with email %s already exists"%email)
            return

        password=getpass('Password:')
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'),
                        admin=admin)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

def generate_secret():
    # create a random secret key for the application
    # WARNING: this key file should never be checked into the git repository
    open('flaskr/secret.key', 'wb').write(os.urandom(16))