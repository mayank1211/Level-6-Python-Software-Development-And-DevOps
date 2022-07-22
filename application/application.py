import os
from flask import Flask, request, redirect, abort, render_template, session, url_for
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import null



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flask.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "asdasdas_asdasd989"
# Initialize SQLAlchemy connection with sqlite database locally
db = SQLAlchemy(app)





# Initialize flask login manager to authentication and sessions expiry
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
login_manager.refresh_view = 'relogin'
login_manager.needs_refresh_message = (
    u"Session timedout, please re-login to access the application")
login_manager.needs_refresh_message_category = "info"

# Function to redirect the user to login page if not already logged in.
@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)








# Password hashing.
from passlib.hash import sha256_crypt
# Import login and authentication modules
from flask_login import login_user, login_required, logout_user, LoginManager, current_user
# Import all database models from models.py file to create and interact with data.
from models import Users
def find_user_with_email(email):
    return db.session.query(Users).filter_by(Email=email).first()

def save_data(*args):
    # Check if the any data parameter is passed.
    if args:
        for ar in args:
            # If passed then add the data to db sessions before committing.
            db.session.add(ar)
    db.session.commit()

# TODO: MOVE ALL THE ROUTES TO DIFFERENT FILE
@app.route("/login", methods=["GET", "POST"])
def login():
    errorMessage = ""
    if request.method == "POST":
        userFound = find_user_with_email(request.form.get("email_address"))
        # Check if the input email address matches any users email storeed in database, if not show error message to the user
        if not userFound:
            errorMessage = "User does not exist, please register the user first."
        else:
            # If matching email is found try sign in the user, if both email address and password match.
            # Comparing the hashed password with hashed input.
            if sha256_crypt.verify(request.form.get("auth_pass"), userFound.Password):
                login_user(userFound)
                session.modified = True
                app.permanent_session_lifetime = timedelta(minutes=1)
                return redirect(url_for('.index'))
            else:
                errorMessage = "Incorrect details, please check and try again later"
    return render_template("authentication/login.html", title="Sign in", errorMessage=errorMessage)

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(".index"))

    errorMessage = ""
    if request.method == "POST":
        if find_user_with_email(request.form.get("email_address")):
            errorMessage = "Email entered alread exists."
        else:
            # Create the standard user
            newUser = Users(
                Name=request.form.get("full_name"),
                Email=request.form.get("email_address"),
                Password=sha256_crypt.encrypt(request.form.get("password")),
                JobRole=request.form.get("role"),
                CurrentTeam=request.form.get("current_team"),
            )
            save_data(newUser)
            # Redirect the user to login page to sign with their details
            return redirect(url_for(".login"))
    # Render the register form page on the GET request
    return render_template("authentication/register.html", title="Register", errorMessage=errorMessage)

@app.route("/signout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('.login'))

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('service/index.html')
    
@app.route('/services', methods=['GET', 'POST'])
def services():
    return render_template("service/services.html", listDomains="", ServiceLog="", User="")

@app.route('/services/<service_id>', methods=['GET', 'POST'])
def services_toggle():
    return 'Service Offline - Online Toggle'

@app.route('/service/new', methods=['GET', 'POST'])
def service_add():
    return render_template("service/service_add.html", title="Register")

@app.route('/service/update', methods=['GET', 'POST'])
def service_update():
    return render_template("service/service_update.html", title="Register", editService="")

@app.route('/service/delete', methods=['GET', 'POST'])
def service_remove():
    return "SERVICE DELETE"

@app.route('/service/<service_id>', methods=['GET', 'POST'])
def service(service_id):
    return render_template("service/service_view.html", title="Register", Service=service_id, ServiceLog="", page=1)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_handling/404.html'), 404






from models import create_database_and_data
# Call function from models.py file to required create tables and users
create_database_and_data()


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=5000)