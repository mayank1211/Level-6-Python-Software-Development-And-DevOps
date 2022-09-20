import os

from flask import Flask, request, redirect
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

app = Flask(__name__)
# TODO: use ENV 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flask.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get("APP_SECRET", 'keepMeSecret!')
# Initialize SQLAlchemy connection with sqlite database locally
db = SQLAlchemy(app)

# Setup Flask Mail for sending notifications
app.config['MAIL_SERVER'] = os.environ.get("EMAIL_SMTP_SERVER", 'smtp.sendgrid.net')
app.config['MAIL_PORT'] = os.environ.get("EMAIL_SMTP_PORT", 25)
app.config['MAIL_USERNAME'] = os.environ.get("EMAIL_SMTP_EMAIL_ADDRESS", 'apikey')
app.config['MAIL_PASSWORD'] = os.environ.get("EMAIL_SMTP_APP_PASSWORD", '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')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'mayank.patel1211.mp@gmail.com'
mail = Mail(app)

# Initialize flask login manager to auth and sessions expiry
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
login_manager.refresh_view = 'relogin'
login_manager.needs_refresh_message = "Session timedout, please login again"
login_manager.needs_refresh_message_category = "info"


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

import auth
import ping_dom
from models import Users, create_database_and_data
from website_pinger import is_web_service_alive
# Call function from models.py file to required create tables and users
create_database_and_data()

# Start register ping_dom monitoring on application launch
if os.environ.get("START_THREADING"):
    is_web_service_alive("start", 0)

if __name__ == "__main__":
    port = os.environ.get("PORT", 5000)
    app.run(debug=False, host="0.0.0.0", port=port)
