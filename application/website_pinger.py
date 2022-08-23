import urllib.request
import requests
import ssl
from datetime import datetime, timedelta

# Main application starting config
from application import app, db

# Import all database models from models.py file to create and interact with data.
from models import Users, RegisteredServices, ServiceRecords
from multiprocessing import Process
import threading
import json
import schedule
from schedule import every, repeat
import time
import threading

# This restores the same behavior as before.
context = ssl._create_unverified_context()


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


def pingServer(service):
    try:
        server_response = requests.get(service.Domain)
        if server_response.status_code == 200:
            serviceLog = ServiceRecords(
                ServiceId=service.Id,
                Domain=service.Domain,
                ServerIpAddress="192.168.1.1",
                ServiceOnlineStatus=True,
                Timestamp=datetime.today().now(),
            )
        server_response.close()
    except requests.exceptions.HTTPError as err:
        server_response_error = err
        serviceLog = ServiceRecords(
            ServiceId=service.Id,
            Domain=service.Domain,
            ServerIpAddress="N/A",
            ConnectionError=server_response_error,
            ServiceOnlineStatus=False,
            Timestamp=datetime.today().now(),
        )

    db.session.add(serviceLog)
    db.session.commit()
    print("Server Status Code: ", server_response.status_code)


def isWebServiceAlive(isUpdateOrStart, service_id):
    if isUpdateOrStart == "start":
        # Fetch all the registered services
        registeredServices = RegisteredServices.query.filter(
            RegisteredServices.ServiceMonitorToggle == True
        ).all()
        for service in registeredServices:
            startBackgroundThread(service)
    else:
        print("Job cancelled!")
        schedule.clear(service_id)
        schedule.cancel_job(service_id)
        service = RegisteredServices.query.filter(
            RegisteredServices.Id == service_id,
            RegisteredServices.ServiceMonitorToggle == True,
        ).first()
        if service is not None:
            startBackgroundThread(service)


def startBackgroundThread(service):
    run_continuously(service.RunTimeInterval)
    schedule.every(service.RunTimeInterval).seconds.do(pingServer, service=service).tag(
        service.Id
    )
    # Start the background thread
    stop_run_continuously = run_continuously(service.RunTimeInterval)
    # Stop the background thread
    stop_run_continuously.set()
