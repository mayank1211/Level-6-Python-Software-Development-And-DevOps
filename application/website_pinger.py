import threading
import time
from datetime import datetime

import requests
import schedule
# Import all database models from models.py file to create and interact with data.
from models import RegisteredServices, ServiceRecords

# Main application starting config
from application import db


def run_continuously(interval):
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


def ping_server(service):
    service_log = ""
    registered_service = RegisteredServices.query.filter(RegisteredServices.Id == service.Id).first()
    try:
        server_response = requests.get(service.Domain)

        if server_response.status_code == 200:
            service_log = ServiceRecords(
                ServiceId=service.Id,
                Domain=service.Domain,
                ServerIpAddress="192.168.1.1",
                ServiceOnlineStatus=True,
                Timestamp=datetime.today().now(),
            )
        server_response.close()

        if server_response.status_code == 200 and registered_service.EmailSentToggle == True:
            registered_service.EmailSentToggle = False
            db.session.commit()

    except requests.exceptions.HTTPError as err:
        server_response_error = err
        service_log = ServiceRecords(
            ServiceId=service.Id,
            Domain=service.Domain,
            ServerIpAddress="N/A",
            ConnectionError=server_response_error,
            ServiceOnlineStatus=False,
            Timestamp=datetime.today().now(),
        )

        if not registered_service.EmailSentToggle:
            registered_service.EmailSentToggle = True
            db.session.commit()

    if service_log:
        db.session.add(service_log)
        db.session.commit()


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
        print("Stopped")
        schedule.clear(service_id)
        schedule.cancel_job(service_id)


def start_background_thread(service):
    run_continuously(service.RunTimeInterval)
    schedule.every(service.RunTimeInterval).seconds.do(ping_server, service=service).tag(
        service.Id
    )
    # Start the background thread
    stop_run_continuously = run_continuously(service.RunTimeInterval)
    # Stop the background thread
    stop_run_continuously.set()
#
#
# def send_simple_message(service_id, service_status, timestamp):
#     registered_service = RegisteredServices.query.filter(RegisteredServices.Id == service_id).first()
#     api_key = '13b06f2ff7ff9a39a2d899a34b4aef37'
#     api_secret = '47afa4523e88057ff64e60046a6c8124'
#
#     if service_status:
#         service_status = "Online"
#     else:
#         service_status = "Offline"
#
#     mailjet = Client(auth=(api_key, api_secret), version='v3.1')
#     data = {
#         'Messages': [
#             {
#                 "From": {
#                     "Email": "hlcsasmjiz@arxxwalls.com",
#                     "Name": "Service Monitoring"
#                 },
#                 "To": [
#                     {
#                         "Email": registered_service.NotificationEmail,
#                         "Name": "None"
#                     }
#                 ],
#                 "Subject": "Greetings from Mailjet.",
#                 "TextPart": "My first Mailjet email",
#                 "HTMLPart": f"<strong>The following ping_dom is {service_status}</strong> <br><br> Service Name: ${registered_service.ServiceName} <br><br> Domain URL: ${registered_service.Domain} <br><br> Timestamp: ${timestamp}",
#                 "CustomID": "AppGettingStartedTest"
#             }
#         ]
#     }
#     mailjet.send.create(data=data)
