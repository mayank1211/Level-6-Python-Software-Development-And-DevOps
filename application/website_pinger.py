from re import I
import threading
import time
from datetime import datetime

import requests
import schedule
# Import all database models from models.py file to create and interact with data.
from models import RegisteredServices, ServiceRecords
# Import Flask Mail package
from flask_mail import Message
# Main application starting config
from application import app, db, mail



def run_continuously(interval):
    try:
        cease_continuous_run = threading.Event()

        class ScheduleThread(threading.Thread):
            @classmethod
            def run(cls):
                while not cease_continuous_run.is_set():
                    schedule.run_pending()
                    time.sleep(interval)

        continuous_thread = ScheduleThread()
        continuous_thread.start()
        return cease_continuous_run
    except:
        pass

def save_failed_ping_response(registered_service, error):
    registered_service = RegisteredServices.query.filter(RegisteredServices.Id == registered_service.Id).first()
    service_log = ServiceRecords(
        ServiceId=registered_service.Id,
        Domain=registered_service.Domain,
        ServerIpAddress="N/A",
        ConnectionError=repr(error),
        ServiceOnlineStatus=False,
        Timestamp=datetime.today().now(),
    )

    if not registered_service.EmailSentToggle:
        RegisteredServices.query.filter(RegisteredServices.Id == registered_service.Id).update({RegisteredServices.EmailSentToggle: True})
        db.session.commit()
        send_email_notification(registered_service.Id, service_log.Timestamp)

    db.session.add(service_log)
    db.session.commit()


def ping_server(service):
    registered_service = RegisteredServices.query.filter(RegisteredServices.Id == service.Id).first()
    try:
        with requests.get('http://' + registered_service.Domain, stream=True) as response:
            try:
                service_log = ServiceRecords(
                    ServiceId=registered_service.Id,
                    Domain=registered_service.Domain,
                    ServerIpAddress="192.168.1.1",
                    ServiceOnlineStatus=True,
                    Timestamp=datetime.today().now(),
                )

                if registered_service.EmailSentToggle:
                    RegisteredServices.query.filter(RegisteredServices.Id == registered_service.Id).update({RegisteredServices.EmailSentToggle: False})
                    db.session.commit()
                    send_email_notification(registered_service.Id, service_log.Timestamp)
            
                db.session.add(service_log)
                db.session.commit()
            except requests.exceptions.HTTPError:
                save_failed_ping_response(registered_service, "404 Client Error: Cannot Find the host")
    except requests.exceptions.ConnectionError:
        save_failed_ping_response(registered_service, "Invalid host provided or the server is unreachable (offline)")

def is_web_service_alive(is_update_or_start, service_id):
    if is_update_or_start == "start":
        # Fetch all the registered services
        registered_services = RegisteredServices.query.filter(
            RegisteredServices.ServiceMonitorToggle == True
        ).all()
        for service in registered_services:
            start_background_thread(service)
    elif is_update_or_start == "updated":
        registered_services = RegisteredServices.query.filter(
            RegisteredServices.Id == service_id,
            RegisteredServices.ServiceMonitorToggle == True,
        ).first()

        schedule.clear(service_id)
        schedule.cancel_job(service_id)
        if registered_services is not None:
            start_background_thread(registered_services)
    else:
        registered_services = RegisteredServices.query.filter(
            RegisteredServices.Id == service_id,
            RegisteredServices.ServiceMonitorToggle == True,
        ).first()
        schedule.clear(registered_services)
        schedule.cancel_job(registered_services)


def start_background_thread(service):
    try:
        run_continuously(service.RunTimeInterval)
        schedule.every(service.RunTimeInterval).seconds.do(ping_server, service=service).tag(
            service.Id
        )
        # Start the background thread
        stop_run_continuously = run_continuously(service.RunTimeInterval)
        # Stop the background thread
        stop_run_continuously.set()
    except:
        pass

def send_email_notification(service_id, timestamp):
    service = RegisteredServices.query.filter(RegisteredServices.Id == service_id).first()
    if not service.EmailSentToggle:
        service_status = "Online"
    else:
        service_status = "Offline"
    with app.app_context():
        msg =  Message('Service Monitioring - NHS Digital', recipients = [service.NotificationEmail])
        msg.html = f"<html><body><div> <h2>The following service: {service.ServiceName}</h2> <ul> <li> <a href='https://flask-python-mayank.herokuapp.com/service/{service.Id}'>Service Name: {service.ServiceName}</a> </li> <li>Domain: {service.Domain}</li> <li>Status: {service_status}</li> <li>Time: {timestamp}</li> </ul></div></body></html>"
        mail.send(msg)