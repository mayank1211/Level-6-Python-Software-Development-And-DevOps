# # tests/test_back_end.py
# import unittest
# from flask import abort, url_for
# from flask_testing import TestCase
# # Password hashing.
# from passlib.hash import sha256_crypt
# from run import app, db
# from models import create_database_and_data, Users, Skills, Comments

# class TestBase(TestCase):

#     def create_app(self):
#         # pass in test configurations
#         app.config["TESTING"] = True
#         app.config["DEBUG"] = False
#         self.app = app.test_client()
#         return app

#     def setUp(self):
#         """
#         Create tables and data
#         """
#         db.session.remove()
#         db.drop_all()
#         create_database_and_data()

#     def tearDown(self):
#         """
#         Will be called after every test
#         """
#         db.session.remove()
#         db.drop_all()

# class TestModels(TestBase):

#     def test_admin_user_model(self):
#         """
#         Test single admin account added to Users table
#         """
#         adminUser = Users.query.filter_by(UserRole="Admin").all()
        
#         self.assertEqual(len(adminUser), 1)
#         self.assertEqual(adminUser[0].Name, "Mayank Patel")
#         self.assertEqual(adminUser[0].Email, "mayank.patel@admin.com")
#         self.assertEqual(adminUser[0].JobRole, "Software Developer")
#         self.assertEqual(adminUser[0].UserRole, "Admin")
#         self.assertEqual(adminUser[0].CurrentTeam, "NHS.UK - Service Profiles")

#     def test_standard_user_model(self):
#         """
#         Test single standard account added to Users table
#         """
#         standardUser = Users.query.filter_by(UserRole="Standard").all()
        
#         self.assertEqual(len(standardUser), 1)
#         self.assertEqual(standardUser[0].Name, "Mayank Patel Standard")
#         self.assertEqual(standardUser[0].Email, "mayank.patel@standard.com")
#         self.assertEqual(standardUser[0].JobRole, "Software Developer - Standard")
#         self.assertEqual(standardUser[0].UserRole, "Standard")
#         self.assertEqual(standardUser[0].CurrentTeam, "NHS.UK - Service Profiles")

#     def test_skills_model(self):
#         """
#         Test single skill added to admin account
#         """
#         userSkill = Skills.query.filter_by(UserId=2).all()
        
#         self.assertEqual(len(userSkill), 2)
#         self.assertEqual(userSkill[0].Id, 1)
#         self.assertEqual(userSkill[0].UserId, 2)
#         self.assertEqual(userSkill[0].SkillName, "Kubernetes")
#         self.assertEqual(userSkill[0].SkillRating, 5)

#     def test_comments_model(self):
#         """
#         Test single comment added to admin account
#         """
#         userComment = Comments.query.filter_by(UserId=2).all()
        
#         self.assertEqual(len(userComment), 1)
#         self.assertEqual(userComment[0].Id, 1)
#         self.assertEqual(userComment[0].UserId, 2)
#         self.assertEqual(userComment[0].Comments, "I also do performance testing for NHS.UK on varies Covid and Non-Covid related services.")

# if __name__ == '__main__':
#     unittest.main()
