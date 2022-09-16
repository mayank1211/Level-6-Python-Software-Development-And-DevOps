from datetime import timedelta

# Import login and auth modules
import flask_login
from flask import request, redirect, render_template, url_for, session
# Password hashing.
from flask_login import current_user, login_user, logout_user
from passlib.hash import sha256_crypt

# Main application starting config
from application import app, db
# Import all database models from models.py file to create and interact with data.
from ping_dom import save_data_to_db
from models import Users

@app.before_first_request  # runs before FIRST request (only once)
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)

@app.route('/login', methods=['GET', 'POST'])
def login():
    errorMessage = ''
    if request.method == 'POST':
        userFound = (
            db.session.query(Users)
                .filter_by(Email=request.form.get('email_address'))
                .first()
        )
        # Check if the input email address matches any users email storeed in database, if not show error message to the user
        if not userFound:
            errorMessage = 'User does not exist, register the user before logging in.'
        else:
            # If matching email is found try sign in the user, if both email address and password match.
            # Comparing the hashed password with hashed input.
            if sha256_crypt.verify(request.form.get('auth_pass'), userFound.Password):
                login_user(userFound, remember=True)
                session.modified = True
                app.permanent_session_lifetime = timedelta(minutes=1)
                return redirect(url_for('.index'))
            else:
                errorMessage = 'Incorrect details, please check and try again later'
    return render_template(
        'auth/login.html', title='Sign in', errorMessage=errorMessage
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('.index'))

    errorMessage = ''
    if request.method == 'POST':
        if (
                db.session.query(Users)
                        .filter_by(Email=request.form.get('email_address'))
                        .first()
        ):
            errorMessage = 'Email entered alread exists.'
        else:
            # Create the standard user
            newUser = Users(
                Name=request.form.get('full_name'),
                Email=request.form.get('email_address'),
                Password=sha256_crypt.encrypt(request.form.get('password')),
            )
            save_data_to_db(newUser)
            # Redirect the user to login page to sign with their details
            return redirect(url_for('.login'))
    # Render the register form page on the GET request
    return render_template(
        'auth/register.html', title='Register', errorMessage=errorMessage
    )


@app.route('/signout')
@flask_login.login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('.login'))
