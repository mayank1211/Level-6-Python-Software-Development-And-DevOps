import unittest
from flask_testing import TestCase
from application import app, db
from models import create_database_and_data, Users, RegisteredServices, ServiceRecords

class TestBase(TestCase):
    def create_app(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        self.app = app.test_client()
        return app

    def setUp(self):
        """
        Create tables and data
        """
        db.session.remove()
        db.drop_all()
        create_database_and_data()

    def tearDown(self):
        """
        Will be called after every test
        """
        db.session.remove()
        db.drop_all()

class TestModels(TestBase):
    def test_admin_user_model(self):
        """
        Test single admin account added to Users table
        """
        adminUser = Users.query.filter_by(UserRole="Admin").first()
        
        self.assertEqual(adminUser.Name, "Mayank Patel")
        self.assertEqual(adminUser.Email, "mayank.patel@admin.com")
        self.assertEqual(adminUser.UserRole, "Admin")

    def test_standard_user_model(self):
        """
        Test single standard account added to Users table
        """
        standardUser = Users.query.filter_by(UserRole="Standard").first()
    
        self.assertEqual(standardUser.Name, "Mayank Patel Standard")
        self.assertEqual(standardUser.Email, "mayank.patel@standard.com")
        self.assertEqual(standardUser.UserRole, "Standard")

    def test_registered_services_model(self):
        """
        Test registered services
        """
        registered_service = RegisteredServices.query.filter_by(Id=1).first()
        
        self.assertEqual(registered_service.Id, 1)
        self.assertEqual(registered_service.ServiceName, "Stack Overflow Website")
        self.assertEqual(registered_service.Domain, "https://www.stackoverflow.com")
        self.assertEqual(registered_service.RunTimeInterval, 60)
        self.assertEqual(registered_service.NotificationEmail, "mayank.patel@admin.com")
        self.assertEqual(registered_service.EmailSentToggle, False)
        self.assertEqual(registered_service.ServiceMonitorToggle, True)

    def test_passed_service_records_model(self):
        """
        Test ping_dom records for a passed ping_dom with 200 status code
        """
        service_record = ServiceRecords.query.filter_by(Id=1).first()
        
        self.assertEqual(service_record.Id, 1)
        self.assertEqual(service_record.ServiceId, 1)
        self.assertEqual(service_record.Domain, "https://www.stackoverflow.com")
        self.assertEqual(service_record.ServerIpAddress, "192.168.1.1")
        self.assertTrue(service_record.ServiceOnlineStatus)

    def test_failed_service_records_model(self):
        """
        Test ping_dom records for a failed ping_dom with 400 status code
        """
        service_record = ServiceRecords.query.filter_by(Id=2).first()
        
        self.assertEqual(service_record.Id, 2)
        self.assertEqual(service_record.ServiceId, 1)
        self.assertEqual(service_record.Domain, "https://www.stackoverflow.com")
        self.assertEqual(service_record.ServerIpAddress, "192.168.1.1")
        self.assertEqual(service_record.ConnectionError, "Unable to connect to the server")
        self.assertFalse(service_record.ServiceOnlineStatus)

if __name__ == '__main__':
    unittest.main()
