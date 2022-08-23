from distutils import util
from website_pinger import *
from flask import request, redirect, render_template, session, url_for

# Import login and authentication modules
from flask_login import (
    login_user,
    login_required,
    logout_user,
    LoginManager,
    current_user,
)

# Password hashing.
from passlib.hash import sha256_crypt
from datetime import datetime, timedelta

# Main application starting config
from application import app, db

# Import all database models from models.py file to create and interact with data.
from models import Users, RegisteredServices, ServiceRecords


def save_data(*args):
    # Check if the any data parameter is passed.
    if args:
        for ar in args:
            # If passed then add the data to db sessions before committing.
            db.session.add(ar)
    db.session.commit()


@app.route("/service/<service_id>", methods=["GET", "POST"])
@login_required
def service(service_id):
    # TODO: Add logic for only showing certain logs per page.
    page = 0
    if not request.args.get("page"):
        page = request.args.get("page")

    serviceLogs = (
        ServiceRecords.query.filter(ServiceRecords.ServiceId == service_id)
        .order_by(ServiceRecords.Timestamp.desc())
        .offset(0 * 10)
        .limit(20)
        .all()
    )
    registeredService = RegisteredServices.query.filter(
        RegisteredServices.Id == service_id
    ).first()
    return render_template(
        "service/service_view.html",
        title="Service",
        ServiceLogs=serviceLogs,
        ServiceName=registeredService.ServiceName,
        ServiceId=registeredService.Id,
        page=0,
        datePicker=0,
    )


@app.route("/manage/account", methods=["GET", "POST"])
@login_required
def my_profile():
    flashMessage = ""
    if request.method == "POST":
        if request.form.get("password") == request.form.get("confirm_password"):
            userFound = Users.query.filter(Users.Id == current_user.get_id()).first()
            userFound.Password = sha256_crypt.encrypt(request.form.get("password"))
            save_data(userFound)
            flashMessage = "Your password has been updated, Please logout and sign back in with new credentials."

    return render_template("authentication/my_account.html", flashMessage=flashMessage)


@app.route("/delete/account/<user_id>", methods=["GET", "POST"])
@login_required
def delete_profile(user_id):
    Users.query.filter(Users.Id == user_id).delete()
    save_data()
    logout_user()
    session.clear()
    return redirect(url_for(".login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    errorMessage = ""
    if request.method == "POST":
        userFound = (
            db.session.query(Users)
            .filter_by(Email=request.form.get("email_address"))
            .first()
        )
        # Check if the input email address matches any users email storeed in database, if not show error message to the user
        if not userFound:
            errorMessage = "User does not exist, register the user before logging in."
        else:
            # If matching email is found try sign in the user, if both email address and password match.
            # Comparing the hashed password with hashed input.
            if sha256_crypt.verify(request.form.get("auth_pass"), userFound.Password):
                login_user(userFound, remember=True)
                session.modified = True
                app.permanent_session_lifetime = timedelta(minutes=1)
                return redirect(url_for(".index"))
            else:
                errorMessage = "Incorrect details, please check and try again later"
    return render_template(
        "authentication/login.html", title="Sign in", errorMessage=errorMessage
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(".index"))

    errorMessage = ""
    if request.method == "POST":
        if (
            db.session.query(Users)
            .filter_by(Email=request.form.get("email_address"))
            .first()
        ):
            errorMessage = "Email entered alread exists."
        else:
            # Create the standard user
            newUser = Users(
                Name=request.form.get("full_name"),
                Email=request.form.get("email_address"),
                Password=sha256_crypt.encrypt(request.form.get("password")),
            )
            save_data(newUser)
            # Redirect the user to login page to sign with their details
            return redirect(url_for(".login"))
    # Render the register form page on the GET request
    return render_template(
        "authentication/register.html", title="Register", errorMessage=errorMessage
    )


@app.route("/signout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for(".login"))


@app.route("/services", methods=["GET"])
@login_required
def services():
    allRegisteredServices = RegisteredServices.query.all()
    return render_template(
        "service/services.html",
        allRegisteredServices=allRegisteredServices,
        ServiceLog="",
        User="",
    )


@app.route("/services/<service_id>", methods=["POST"])
@login_required
def services_toggle(service_id):
    RegisteredServices.query.filter(RegisteredServices.Id == service_id).update(
        {"ServiceMonitorToggle": util.strtobool(request.form.get("service-toggle"))}
    )
    db.session.commit()
    isWebServiceAlive("update", service_id)
    return redirect(url_for("services"))


@app.route("/service/update/<service_id>", methods=["GET", "POST"])
@login_required
def service_update(service_id):
    service = RegisteredServices.query.filter(
        RegisteredServices.Id == service_id
    ).first()

    if request.method == "POST":
        service.ServiceName = request.form.get("Service_Name")
        service.Domain = request.form.get("Domain")
        service.RunTimeInterval = request.form.get("Runtime")
        service.NotificationEmail = request.form.get("Email")
        save_data(service)
        isWebServiceAlive("update", service.Id)
        return redirect(url_for(".service", service_id=service.Id))

    return render_template("service/service_update.html", service=service)


@app.route("/")
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    # fetch all registered service
    allRegisteredServices = RegisteredServices.query.filter(
        RegisteredServices.ServiceMonitorToggle != False
    ).all()

    # add them to existing registerede serevice array
    for registeredService in allRegisteredServices:
        serviceLogExists = (
            ServiceRecords.query.filter(
                ServiceRecords.ServiceId == registeredService.Id,
                ServiceRecords.ServiceOnlineStatus == True,
            ).first()
            is not None
        )

        if serviceLogExists:
            # work latest service failure timestamp
            registeredService.Success = (
                ServiceRecords.query.filter(
                    ServiceRecords.ServiceId == registeredService.Id,
                    ServiceRecords.ServiceOnlineStatus == True,
                )
                .order_by(ServiceRecords.Id.desc())
                .first()
                .Timestamp
            )
            serviceFailure = (
                ServiceRecords.query.filter(
                    ServiceRecords.ServiceId == registeredService.Id,
                    ServiceRecords.ServiceOnlineStatus == False,
                )
                .order_by(ServiceRecords.Id.desc())
                .first()
                is not None
            )
            if serviceFailure:
                registeredService.Failure = (
                    ServiceRecords.query.filter(
                        ServiceRecords.ServiceId == registeredService.Id,
                        ServiceRecords.ServiceOnlineStatus == False,
                    )
                    .order_by(ServiceRecords.Id.desc())
                    .first()
                    .Timestamp
                )
            # 30 days fail
            thirtyDaysFailureCount = (
                ServiceRecords.query.filter(
                    ServiceRecords.ServiceId == registeredService.Id,
                    ServiceRecords.ServiceOnlineStatus == False,
                    ServiceRecords.Timestamp >= (datetime.today() - timedelta(days=30)),
                )
                .order_by(ServiceRecords.Id.desc())
                .all()
            )

            # 24 hour fail
            twentyFourHrsFailuresCount = (
                ServiceRecords.query.filter(
                    ServiceRecords.ServiceId == registeredService.Id,
                    ServiceRecords.ServiceOnlineStatus == False,
                    ServiceRecords.Timestamp >= (datetime.today() - timedelta(days=1)),
                )
                .order_by(ServiceRecords.Id.desc())
                .all()
            )

            # 30 days pass
            thirtyDaysPassCount = (
                ServiceRecords.query.filter(
                    ServiceRecords.ServiceId == registeredService.Id,
                    ServiceRecords.ServiceOnlineStatus == True,
                    ServiceRecords.Timestamp >= (datetime.today() - timedelta(days=1)),
                )
                .order_by(ServiceRecords.Id.desc())
                .all()
            )

            try:
                registeredService.thirtyDaysFailureCount = format(
                    float(
                        len(thirtyDaysFailureCount)
                        * 100
                        / (len(thirtyDaysFailureCount) + len(thirtyDaysPassCount))
                    ),
                    ".2f",
                )
            except ZeroDivisionError:
                registeredService.thirtyDaysFailureCount = 0

            try:
                registeredService.twentyFourHrsFailuresCount = format(
                    float(
                        len(twentyFourHrsFailuresCount)
                        * 100
                        / (len(twentyFourHrsFailuresCount) + len(thirtyDaysPassCount))
                    ),
                    ".2f",
                )
            except ZeroDivisionError:
                registeredService.twentyFourHrsFailuresCount = 0

    return render_template(
        "service/index.html", allRegisteredServices=allRegisteredServices
    )


@app.route("/service/add", methods=["GET", "POST"])
@app.route("/service/new", methods=["GET", "POST"])
@login_required
def service_add():
    if request.method == "POST":
        RegisteredServiceExists = RegisteredServices.query.filter(
            RegisteredServices.ServiceName == request.form.get("Service_Name"),
            RegisteredServices.Domain == request.form.get("Domain"),
        ).first()

        if not RegisteredServiceExists:
            service = RegisteredServices(
                ServiceName=request.form.get("Service_Name"),
                Domain=request.form.get("Domain"),
                RunTimeInterval=request.form.get("Runtime"),
                NotificationEmail=request.form.get("Email"),
                EmailSentToggle=True,
                ServiceMonitorToggle=True,
                Timestamp=datetime.today().now(),
            )
            save_data(service)
            service = RegisteredServices.query.filter(
                RegisteredServices.Domain == request.form.get("Domain")
            ).first()
            isWebServiceAlive("add", service.Id)

    return render_template("service/service_add.html", title="Register")


@app.route("/service/delete/<service_id>", methods=["GET", "POST"])
@login_required
def service_remove(service_id):
    serviceExists = RegisteredServices.query.filter(
        RegisteredServices.Id == service_id
    ).first()
    if serviceExists:
        RegisteredServices.query.filter(RegisteredServices.Id == service_id).delete()
        ServiceRecords.query.filter(ServiceRecords.ServiceId == service_id).delete()
        db.session.commit()
    return redirect(url_for("index"))


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error_handling/404.html"), 404


# TODO:
# FIX SERVICE VIEW PAGINATION 
# ADD BASIC UNIT TESTS
# ADD SOME INTEGRATION TEST
# DOCKERFILE
# REFACTOR AND RENAMING
# ADD APPLCATION MONITORING
# COMPRESS OVERALL APPLICATION
# ALL DB QUERY REFACTORED INTO FUNCTIONS WHERE POSSIBLE


# CREATE WIREFRAMES
# CREATE TRELLO TICKETS

# ADD MAILING NOTIFICATION