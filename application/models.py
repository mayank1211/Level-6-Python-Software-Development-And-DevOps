import datetime

from flask_login import UserMixin
from application import db, login_manager

# Password hashing.
from passlib.hash import sha256_crypt


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


class Users(UserMixin, db.Model):
    """ User Table Model """

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
    """Registered Services Table Model"""

    __tablename__ = "registered-services"
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ServiceName = db.Column(db.String(), nullable=False)
    Domain = db.Column(db.String(), nullable=False)
    RunTimeInterval = db.Column(db.Integer, nullable=False)
    NotificationEmail = db.Column(db.String(), nullable=False)
    EmailSentToggle = db.Column(db.Boolean, nullable=False, default=False)
    ServiceMonitorToggle = db.Column(db.Boolean, nullable=False, default=True)
    Timestamp = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.utcnow()
    )

    def get_id(self):
        return self.Id


class ServiceRecords(db.Model):
    """Service Records Table Model"""

    __tablename__ = "ping_dom-records"
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ServiceId = db.Column(
        db.Integer, db.ForeignKey("registered-services.Id"), nullable=False
    )
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
    admin_user = (
        db.session.query(Users).filter_by(Email="mayank.patel@admin.com").first()
    )

    standard_user = (
        db.session.query(Users).filter_by(Email="mayank.patel@standard.com").first()
    )

    # Create the users if they don't exist in the database already.
    if not standard_user:
        new_user = Users(
            Name="Mayank Patel Standard",
            Email="mayank.patel@standard.com",
            Password=sha256_crypt.hash("standard"),
        )
        db.session.add(new_user)
        db.session.commit()

    if not admin_user:
        new_user = Users(
            Name="Mayank Patel",
            Email="mayank.patel@admin.com",
            Password=sha256_crypt.hash("admin"),
            UserRole="Admin",
        )
        db.session.add(new_user)
        db.session.commit()

    has_registered_service = (
        db.session.query(RegisteredServices)
        .filter_by(
            ServiceName="Stack Overflow Website", Domain="https://www.stackoverflow.com"
        )
        .first()
    )

    if not has_registered_service:
        new_registered_service = RegisteredServices(
            ServiceName="Stack Overflow Website",
            Domain="https://www.stackoverflow.com",
            RunTimeInterval="60",
            NotificationEmail="mayank.patel@admin.com",
            EmailSentToggle=False,
            ServiceMonitorToggle=True,
            Timestamp=datetime.datetime.utcnow(),
        )

        service_passed_record = ServiceRecords(
            ServiceId=1,
            Domain="https://www.stackoverflow.com",
            ServerIpAddress="192.168.1.1",
            ServiceOnlineStatus=True,
            Timestamp=datetime.datetime.utcnow(),
        )

        service_failed_record = ServiceRecords(
            ServiceId=1,
            Domain="https://www.stackoverflow.com",
            ServerIpAddress="192.168.1.1",
            ServiceOnlineStatus=False,
            ConnectionError="Unable to connect to the server",
            Timestamp=datetime.datetime.utcnow(),
        )
        db.session.add(new_registered_service)
        db.session.add(service_passed_record)
        db.session.add(service_failed_record)
        db.session.commit()
