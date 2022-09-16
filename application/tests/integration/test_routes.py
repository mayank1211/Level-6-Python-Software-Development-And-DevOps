import unittest
from flask import url_for
from flask_testing import TestCase
from bs4 import BeautifulSoup
from application import app

class TestBase(TestCase):

    def create_app(self):
        # pass in test configurations
        app.config['TESTING'] = True
        app.config["DEBUG"] = False
        self.app = app.test_client()
        return app

    def setUp(self):
        app.login_manager.init_app(app)
        app.config['LOGIN_DISABLED'] = True

    def tearDown(self):
        """
        Will be called after every test
        """

class TestViews(TestBase):
    def test_login_view(self):
        """
        Test that login page is accessible
        """
        response = self.client.get(url_for('.login'))
        soup = BeautifulSoup(response.data, "html.parser")
        self.assertEqual(response.status_code, 200)
        # print the HTML elements as text
        self.assertEqual("Sign in", soup.find("h1", {"id": "title"}).text.strip())
        self.assertEqual("Email", soup.find("label", {"id": "email"}).text.strip())
        self.assertEqual("Password", soup.find("label", {"id": "password"}).text.strip())

    def test_register_view(self):
        """
        Test that register is accessible
        """
        response = self.client.get(url_for('.register'))
        soup = BeautifulSoup(response.data, "html.parser")
        self.assertEqual(response.status_code, 200)
        # print the HTML elements as text
        self.assertEqual("Register", soup.find("h1", {"id": "title"}).text.strip())
        self.assertEqual("Email", soup.find("label", {"id": "email"}).text.strip())
        self.assertEqual("Password", soup.find("label", {"id": "password"}).text.strip())

    def test_homepage_view_without_authentication(self):
        """
        Test that homepage is accessible without login
        """
        app.config['LOGIN_DISABLED'] = False
        response = self.client.get(url_for('.index'))
        soup = BeautifulSoup(response.data, "html.parser")
        self.assertEqual(response.status_code, 302)

    def test_homepage_view(self):
        """
        Test that homepage is accessible without login
        """
        response = self.client.get(url_for('.index'))
        soup = BeautifulSoup(response.data, "html.parser")
        self.assertEqual(response.status_code, 200)
        self.assertEqual("Monitor Your Services", soup.find("h1", {"class": "nhsuk-u-margin-bottom-3"}).text.strip())
        self.assertEqual("Add New Service", soup.find("a", {"id": "add-service-btn"}).text.strip())

    def test_services_view_(self):
        """
        Test that services is accessible without login
        """
        response = self.client.get(url_for('.services'))
        soup = BeautifulSoup(response.data, "html.parser")
        self.assertEqual(response.status_code, 200)
        self.assertEqual("Services online", soup.find("h2", {"id": "online-services"}).text.strip())
        self.assertEqual("Service currently being monitored", soup.find("caption", {"id": "online-currentl-monitored-service"}).text.strip())

    def test_specific_service_view(self):
        """
        Test that homepage is accessible without login
        """
        response = self.client.get(url_for('.service', service_id=1))
        soup = BeautifulSoup(response.data, "html.parser")
        self.assertEqual(response.status_code, 200)
        self.assertEqual("Update Service", soup.find("a", {"id": "service-update-btn"}).text.strip())
        self.assertEqual("Service Status", soup.find("th", {"id": "service-status-title"}).text.strip())
        self.assertEqual("Host", soup.find("th", {"id": "service-host-title"}).text.strip())
        self.assertEqual("Error", soup.find("th", {"id": "service-error-title"}).text.strip())
        self.assertEqual("Time (UTC)", soup.find("th", {"id": "service-time-title"}).text.strip())


    def test_manage_user_profile_view(self):
        """
        Test that homepage is accessible without login
        """
        response = self.client.get(url_for('.my_profile'))
        soup = BeautifulSoup(response.data, "html.parser")
        self.assertEqual(response.status_code, 200)
        self.assertEqual("My Profile", soup.find("h1", {"class": "nhsuk-fieldset__heading"}).text.strip())
        self.assertEqual("Change Password", soup.find("legend", {"id": "change-password-title"}).text.strip())

if __name__ == '__main__':
    unittest.main()
