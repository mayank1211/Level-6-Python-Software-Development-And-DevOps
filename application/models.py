import datetime
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime
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
    JobRole = db.Column(db.String(100), nullable=True)
    CurrentTeam = db.Column(db.String(100), nullable=True)
    LastUpdatedAt = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    UserRole = db.Column(db.String(8), nullable=False, default="Standard")

    def get_id(self):
        """Return the user id to satisfy Flask-Login's requirements."""
        return self.Id


# class Skills(db.Model):
#     """ Skills Model """
#     __tablename__ = "skills"
#     Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     UserId = db.Column(db.Integer, db.ForeignKey('users.Id'), nullable=False)
#     SkillName = db.Column(db.String(120), nullable=False)
#     SkillRating = db.Column(db.Integer, nullable=False)


# class Comments(db.Model):
#     """ Comments Model """
#     __tablename__ = "comments"
#     Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     UserId = db.Column(db.Integer, db.ForeignKey('users.Id'), nullable=False)
#     Comments = db.Column(db.String(120), nullable=True)


def create_database_and_data():
    db.create_all()

    adminUser = db.session.query(Users).filter_by(
        Email="mayank.patel@admin.com").first()

    standardUser = db.session.query(Users).filter_by(
        Email="mayank.patel@standard.com").first()


    if not standardUser:
        newUser = Users(
            Name="Mayank Patel Standard",
            Email="mayank.patel@standard.com",
            Password=sha256_crypt.encrypt("standard"),
            JobRole="Software Developer - Standard",
            CurrentTeam="NHS.UK - Service Profiles",
        )
        db.session.add(newUser)
        db.session.commit()

    if not adminUser:
        newUser = Users(
            Name="Mayank Patel",
            Email="mayank.patel@admin.com",
            Password=sha256_crypt.encrypt("admin"),
            JobRole="Software Developer",
            CurrentTeam="NHS.UK - Service Profiles",
            UserRole="Admin",
        )
        db.session.add(newUser)
        db.session.commit()

        # registeredUser = db.session.query(Users).filter_by(
        #     Email="mayank.patel@admin.com").first()

        # skill_one = Skills(
        #     UserId=registeredUser.Id,
        #     SkillName="Kubernetes",
        #     SkillRating=5
        # )
        # skill_two = Skills(
        #     UserId=registeredUser.Id,
        #     SkillName="C# dotnet",
        #     SkillRating=4
        # )
        # comment = Comments(
        #     UserId=registeredUser.Id,
        #     Comments="I also do performance testing for NHS.UK on varies Covid and Non-Covid related services."
        # )

        # db.session.add(comment)
        # db.session.add(skill_one)
        # db.session.add(skill_two)
        # db.session.commit()
