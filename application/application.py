import os
from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


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
    u"Session timedout, please login again")
login_manager.needs_refresh_message_category = "info"


# Function to redirect the user to login page if not already logged in.
@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return Users.query.get(int(user_id))


from models import Users, create_database_and_data
import my_routes
from  website_pinger import isWebServiceAlive
# Call function from models.py file to required create tables and users
create_database_and_data()
# Start register service monitoring on application launch
isWebServiceAlive("start", 0)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=5000)