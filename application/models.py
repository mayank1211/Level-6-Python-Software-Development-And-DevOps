import datetime
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, null
from sqlalchemy import inspect
from flask_login import UserMixin
from application import app, db, login_manager
# Password hashing.
from passlib.hash import sha256_crypt


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


class Users(UserMixin, db.Model):
    """ User Model """
    __tablename__ = "users"
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(80), nullable=True)
    Email = db.Column(db.String(120), nullable=True)
    Password = db.Column(db.String(120), nullable=True)
    LastUpdatedAt = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    UserRole = db.Column(db.String(8), nullable=False, default="Standard")

    def get_id(self):
        return self.Id


class RegisteredServices(db.Model):
    """ Registered Services Model """
    __tablename__ = "registered-services"
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ServiceName = db.Column(db.String(), nullable=False)
    Domain = db.Column(db.String(), nullable=False)
    RunTimeInterval = db.Column(db.Integer, nullable=False)
    NotificationEmail = db.Column(db.String(), nullable=False)
    EmailSentToggle = db.Column(db.Boolean, nullable=False, default=True)
    ServiceMonitorToggle = db.Column(db.Boolean, nullable=False, default=True)
    Timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())

    def get_id(self):
        return self.Id


class ServiceRecords(db.Model):
    """ Service Records Model """
    __tablename__ = "service-records"
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ServiceId = db.Column(db.Integer, db.ForeignKey('registered-services.Id'), nullable=False)
    Domain = db.Column(db.String(400), nullable=False)
    ServerIpAddress = db.Column(db.String(500), nullable=True)
    ServiceOnlineStatus = db.Column(db.Boolean, nullable=False, default=True)
    ConnectionError = db.Column(db.String(500), nullable=True)
    Timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def get_id(self):
        return self.Id


def create_database_and_data():
    db.create_all()

    # Check if admin and standard user exists (Also used for the tests.)
    adminUser = db.session.query(Users).filter_by(
        Email="mayank.patel@admin.com").first()

    standardUser = db.session.query(Users).filter_by(
        Email="mayank.patel@standard.com").first()

    # Create the users if they don't exist in the database already.
    if not standardUser:
        newUser = Users(
            Name="Mayank Patel Standard",
            Email="mayank.patel@standard.com",
            Password=sha256_crypt.encrypt("standard"),
        )
        db.session.add(newUser)
        db.session.commit()

    if not adminUser:
        newUser = Users(
            Name="Mayank Patel",
            Email="mayank.patel@admin.com",
            Password=sha256_crypt.encrypt("admin"),
            UserRole="Admin",
        )
        db.session.add(newUser)
        db.session.commit()

    hasRegisteredService = db.session.query(RegisteredServices).filter_by(ServiceName="Stack Overflow Website", Domain="https://www.stackoverflow.com").first()
    
    if not hasRegisteredService:
        newRegisteredService = RegisteredServices(
            ServiceName="Stack Overflow Website",
            Domain="https://www.stackoverflow.com",
            RunTimeInterval="60",
            NotificationEmail="mayank.patel1211.mp@gmail.com",
            EmailSentToggle=False,
            ServiceMonitorToggle=True,
            Timestamp=datetime.datetime.utcnow(),
        )

        servicePassedRecord = ServiceRecords(
            ServiceId=1,
            Domain="https://www.stackoverflow.com",
            ServerIpAddress="192.168.1.1",
            ServiceOnlineStatus=True,
            Timestamp=datetime.datetime.utcnow(),
        )

        serviceFailedRecord = ServiceRecords(
            ServiceId=1,
            Domain="https://www.stackoverflow.com",
            ServerIpAddress="192.168.1.1",
            ServiceOnlineStatus=False,
            Timestamp=datetime.datetime.utcnow(),
        )
        db.session.add(newRegisteredService)
        db.session.add(servicePassedRecord)
        db.session.add(serviceFailedRecord)
        db.session.commit()
