from datetime import datetime, timedelta
from distutils import util
# Import login and auth modules
import flask_login
from flask import request, redirect, render_template, url_for
# Password hashing.
from passlib.hash import sha256_crypt
# Main application starting config
from application import app, db
from website_pinger import is_web_service_alive
# Import all database models from models.py file to create and interact with data.
from models import Users, RegisteredServices, ServiceRecords


def save_data_to_db(*args):
    # Check if the any data parameter is passed.
    if args:
        for ar in args:
            # If passed then add the data to db sessions before committing.
            db.session.add(ar)
    db.session.commit()

@app.route("/")
@app.route("/index", methods=["GET", "POST"])
@flask_login.login_required
def index():
    # fetch all registered ping_dom
    all_registered_services = RegisteredServices.query.filter(
        RegisteredServices.ServiceMonitorToggle != False
    ).all()

    # add them to existing registered ping_dom array
    for registeredService in all_registered_services:
        service_log_exists = (
                ServiceRecords.query.filter(
                    ServiceRecords.ServiceId == registeredService.Id,
                    ServiceRecords.ServiceOnlineStatus == True,
                ).first()
                is not None
        )

        if service_log_exists:
            # work latest ping_dom failure timestamp
            registeredService.Success = (
                ServiceRecords.query.filter(
                    ServiceRecords.ServiceId == registeredService.Id,
                    ServiceRecords.ServiceOnlineStatus == True,
                )
                    .order_by(ServiceRecords.Id.desc())
                    .first()
                    .Timestamp.strftime('%d/%m/%Y %I:%M:%S')
            )
            service_failure = (
                    ServiceRecords.query.filter(
                        ServiceRecords.ServiceId == registeredService.Id,
                        ServiceRecords.ServiceOnlineStatus == False,
                    )
                    .order_by(ServiceRecords.Id.desc())
                    .first()
                    is not None
            )
            if service_failure:
                registeredService.Failure = (
                    ServiceRecords.query.filter(
                        ServiceRecords.ServiceId == registeredService.Id,
                        ServiceRecords.ServiceOnlineStatus == False,
                    )
                        .order_by(ServiceRecords.Id.desc())
                        .first()
                        .Timestamp.strftime('%d/%m/%Y %I:%M:%S')
                )
            # 30 days fail
            thirty_days_failure_count = (
                ServiceRecords.query.filter(
                    ServiceRecords.ServiceId == registeredService.Id,
                    ServiceRecords.ServiceOnlineStatus == False,
                    ServiceRecords.Timestamp >= (datetime.today() - timedelta(days=30)),
                )
                    .order_by(ServiceRecords.Id.desc())
                    .all()
            )

            # 24 hour fail
            twenty_four_hrs_failures_count = (
                ServiceRecords.query.filter(
                    ServiceRecords.ServiceId == registeredService.Id,
                    ServiceRecords.ServiceOnlineStatus == False,
                    ServiceRecords.Timestamp >= (datetime.today() - timedelta(days=1)),
                )
                    .order_by(ServiceRecords.Id.desc())
                    .all()
            )

            # 30 days pass
            thirty_days_pass_count = (
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
                        len(thirty_days_pass_count)
                        * 100
                        / (len(thirty_days_pass_count) + len(thirty_days_failure_count))
                    ),
                    ".2f",
                )
            except ZeroDivisionError:
                registeredService.thirtyDaysFailureCount = 0

            try:
                registeredService.twentyFourHrsFailuresCount = format(
                    float(
                        len(twenty_four_hrs_failures_count)
                        * 100
                        / (len(twenty_four_hrs_failures_count) + len(thirty_days_pass_count))
                    ),
                    ".2f",
                )
            except ZeroDivisionError:
                registeredService.twentyFourHrsFailuresCount = 0

    return render_template(
        "ping_dom/index.html", title="Homepage", allRegisteredServices=all_registered_services
    )


@app.route("/service/<service_id>", methods=["GET", "POST"])
@flask_login.login_required
def service(service_id):
    service_logs = (
        ServiceRecords.query.filter(ServiceRecords.ServiceId == service_id)
        .order_by(ServiceRecords.Timestamp.desc())
        .all()
    )
    registered_service = RegisteredServices.query.filter(
        RegisteredServices.Id == service_id
    ).first()
    return render_template(
        "ping_dom/service_view.html",
        title="Service",
        ServiceLogs=service_logs,
        ServiceName=registered_service.ServiceName,
        ServiceId=registered_service.Id,
        page=0,
        datePicker=0,
    )


@app.route("/service/add", methods=["GET", "POST"])
@app.route("/service/new", methods=["GET", "POST"])
@flask_login.login_required
def service_add():
    errorMessage=""
    if request.method == "POST":
        registered_service_name_exists = RegisteredServices.query.filter(
            RegisteredServices.ServiceName == request.form.get("Service_Name")
        ).first()

        registered_service_domain_exists = RegisteredServices.query.filter(
            RegisteredServices.Domain == request.form.get("Domain")
        ).first()


        if registered_service_name_exists or registered_service_domain_exists:
            errorMessage = "Either the service name or the URL provided is already in use. Please try again using different name or url"
            return render_template("ping_dom/service_add.html", title="Register", errorMessage=errorMessage)

        if request.form.get("Domain").find("http") != -1:
            errorMessage = "Please remove HTTP protocol from the domain and try again."
            return render_template("ping_dom/service_add.html", title="Register", errorMessage=errorMessage)

        if not (registered_service_name_exists or registered_service_domain_exists):
            new_service = RegisteredServices(
                ServiceName=request.form.get("Service_Name"),
                Domain=request.form.get("Domain"),
                RunTimeInterval=request.form.get("Runtime"),
                NotificationEmail=request.form.get("Email"),
                EmailSentToggle=False,
                ServiceMonitorToggle=True,
                Timestamp=datetime.today().now(),
            )
            save_data_to_db(new_service)
            added_new_service_id = RegisteredServices.query.filter(
                RegisteredServices.ServiceName == request.form.get("Service_Name"),
                RegisteredServices.Domain == request.form.get("Domain")
            ).first()
            is_web_service_alive("updated", added_new_service_id.Id)
            return redirect(url_for(".index"))

    return render_template("ping_dom/service_add.html", title="Register")


@app.route("/service/update/<service_id>", methods=["GET", "POST"])
@flask_login.login_required
def service_update(service_id):
    errorMessage=""
    service = RegisteredServices.query.filter(
        RegisteredServices.Id == service_id
    ).first()

    if request.method == "POST":
        if request.form.get("Domain").find("http") != -1:
            errorMessage = "Please remove HTTP protocol from the domain and try again."
            return render_template("ping_dom/service_update.html", title="Service update", service=service, errorMessage=errorMessage)

        service.ServiceName = request.form.get("Service_Name")
        service.Domain = request.form.get("Domain")
        service.RunTimeInterval = request.form.get("Runtime")
        service.NotificationEmail = request.form.get("Email")
        save_data_to_db(service)
        is_web_service_alive("updated", service.Id)
        return redirect(url_for(".service", service_id=service.Id))

    return render_template("ping_dom/service_update.html", title="Service update", service=service, errorMessage=errorMessage)


@app.route("/service/delete/<service_id>", methods=["GET", "POST"])
@flask_login.login_required
def service_remove(service_id):
    service_exists = RegisteredServices.query.filter(
        RegisteredServices.Id == service_id
    ).first()
    if service_exists:
        RegisteredServices.query.filter(RegisteredServices.Id == service_id).delete()
        ServiceRecords.query.filter(ServiceRecords.ServiceId == service_id).delete()
        save_data_to_db()
    return redirect(url_for("services"))


@app.route("/services", methods=["GET"])
@flask_login.login_required
def services():
    all_registered_services = RegisteredServices.query.all()
    return render_template(
        "ping_dom/services.html",
        title="Services",
        allRegisteredServices=all_registered_services,
        ServiceLog="",
        User="",
    )


@app.route("/services/<service_id>", methods=["POST"])
@flask_login.login_required
def services_toggle(service_id):
    RegisteredServices.query.filter(RegisteredServices.Id == service_id).update(
        {"ServiceMonitorToggle": util.strtobool(request.form.get("service-toggle"))}
    )
    save_data_to_db()
    is_service_updated = "updated" if request.form.get("service-toggle") == 'True' else "stopped"
    is_web_service_alive(is_service_updated, service_id)
    return redirect(url_for("services"))


@app.route("/manage/account", methods=["GET", "POST"])
@flask_login.login_required
def my_profile():
    flash_message = ""
    if request.method == "POST":
        if request.form.get("password") == request.form.get("confirm_password"):
            user_found = Users.query.filter(Users.Id == flask_login.current_user.get_id()).first()
            user_found.Password = sha256_crypt.encrypt(request.form.get("password"))
            save_data_to_db(user_found)
            flash_message = "Your password has been updated, Please logout and sign back in with new credentials."

    return render_template("auth/my_account.html", flashMessage=flash_message)


@app.route("/manage/users/account", methods=["GET"])
@flask_login.login_required
def manage_users():
    users = Users.query.all()
    return render_template("ping_dom/admin_control.html", users=users)


@app.route("/delete/user/<user_id>", methods=["GET"])
@flask_login.login_required
def delete_user(user_id):
    Users.query.filter(Users.id == user_id).delete()
    db.session.commit()
    return redirect(url_for(".index"))


@app.route("/delete/account/<user_id>", methods=["GET", "POST"])
@flask_login.login_required
def delete_profile(user_id):
    Users.query.filter(Users.Id == user_id).delete()
    save_data_to_db()
    flask_login.logout_user()
    return redirect(url_for(".login"))


@app.errorhandler(404)
def page_not_found():
    return render_template("error_handling/404.html"), 404
