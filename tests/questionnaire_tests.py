import unittest
from unittest import mock
from unittest.mock import patch
from flask import Flask
from api.app import setup_routes
from db.connection import get_db_connection
from db.queries import add_user, delete_user  # Make sure to import your actual functions
from uuid import uuid4

class TestQuestionnaireEndpoints(unittest.TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        setup_routes(app)
        return app

    def setUp(self):
        self.app = self.create_app().test_client()
        # Adding a test user to use in the tests
        email = f"test_{uuid4()}@example.com"
        self.user_id = add_user("Test", "User", email, "password", 25, "Male")
        self.app.post('/add_questionnaire', json={
        'user_id': self.user_id,
        'description': 'Initial setup questionnaire',
        'goals': 'Lose weight, gain muscle',
        'challenges': 'Limited time to exercise',
        'expectations': 'Improve within 6 months'
    })

    def tearDown(self):
        # Remove the test user after tests
        delete_user(self.user_id)

    def test_add_questionnaire_success(self):
        """Test successful addition of a questionnaire."""
        response = self.app.post('/add_questionnaire', json={
            'user_id': self.user_id,
            'description': 'Initial setup questionnaire',
            'goals': 'Lose weight, gain muscle',
            'challenges': 'Limited time to exercise',
            'expectations': 'Improve within 6 months'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')

    def test_get_questionnaire(self):
        """Test retrieving a questionnaire."""
        # Assume a questionnaire has already been added for this user
        response = self.app.get(f'/get_questionnaire/{self.user_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('success', data['status'])

    def test_delete_questionnaire(self):
        """Test deleting a questionnaire."""
        # First, add a questionnaire to ensure there is something to delete
        self.app.post('/add_questionnaire', json={
            'user_id': self.user_id,
            'description': 'Setup questionnaire',
            'goals': 'Lose weight',
            'challenges': 'No gym access',
            'expectations': 'Get fit'
        })
        # Then attempt to delete the questionnaire
        response = self.app.delete(f'/delete_questionnaire/{self.user_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
 
    
    @patch('db.connection.get_db_connection', side_effect=ConnectionError("Connection failed"))
    def test_db_connection_failure(self, get_db_connection):
        """
        Test to ensure the application properly handles a database connection failure.
        """
        with self.assertRaises(ConnectionError) as context:
            # Your function that should raise a ConnectionError
            get_db_connection()
        # Assert to check if the error message is correct
        self.assertIn("Connection failed", str(context.exception))

    def test_invalid_user_id_type(self):
        response = self.app.post('/add_questionnaire', json={
            'user_id': 'not-an-integer'})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('Validation failed', data['error'])
        self.assertIn('user_id (not an integer)', data['details'])

    

if __name__ == '__main__':
    unittest.main()
