# # tests/test_back_end.py

# import unittest

# from flask import abort, url_for
# from flask_testing import TestCase
# from bs4 import BeautifulSoup
# from run import app, db

# class TestBase(TestCase):

#     def create_app(self):
#         # pass in test configurations
#         app.config["TESTING"] = True
#         app.config["DEBUG"] = False
#         self.app = app.test_client()
#         return app

# class TestViews(TestBase):

#     def test_login_view(self):
#         """
#         Test that login page is accessible
#         """
#         response = self.client.get(url_for('.login'))
#         soup = BeautifulSoup(response.data, "html.parser")
#         self.assertEqual(response.status_code, 200)
#         # print the HTML elements as text
#         self.assertEqual("Sign in", soup.find("h1", {"id": "title"}).text.strip())
#         self.assertEqual("Email", soup.find("label", {"id": "email"}).text.strip())
#         self.assertEqual("Password", soup.find("label", {"id": "password"}).text.strip())
        

#     def test_register_view(self):
#         """
#         Test that register is accessible
#         """
#         response = self.client.get(url_for('.register'))
#         soup = BeautifulSoup(response.data, "html.parser")
#         self.assertEqual(response.status_code, 200)
#         # print the HTML elements as text
#         self.assertEqual("Register", soup.find("h1", {"id": "title"}).text.strip())
#         self.assertEqual("Email", soup.find("label", {"id": "email"}).text.strip())
#         self.assertEqual("Password", soup.find("label", {"id": "password"}).text.strip())

#     def test_homepage_view(self):
#         """
#         Test that homepage is accessible without login
#         """
#         response = self.client.get(url_for('.index'))
#         soup = BeautifulSoup(response.data, "html.parser")
#         self.assertEqual(response.status_code, 302)

# if __name__ == '__main__':
#     unittest.main()
