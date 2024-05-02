import unittest
from flask import Flask, jsonify
from uuid import uuid4
from api.app import setup_routes  # Ensure this import suits your project structure
from db.connection import get_db_cursor
from db.queries import add_user, delete_user

class TestUserEndpoints(unittest.TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        setup_routes(app)
        return app

    def setUp(self):
        self.app = self.create_app().test_client()  # Setup the test client
    
    # Adding a test user to use in the tests
        email = f"test_{uuid4()}@example.com"
        self.user_id = add_user("Test", "User", email, "password", 25, "Male")


    def tearDown(self):
        # Remove the test user after tests
        delete_user(self.user_id)

    def test_add_user_success(self):
        response = self.app.post('/add_user', json={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': f"john_{uuid4()}@example.com",
            'password': 'securePassword123',
            'age': 30,
            'gender': 'Male'
        })
        data = response.get_json()
        print(data)  # Debug output
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', data['status'])
        
    
    def test_add_user_failure(self):
        """Test adding a user with an existing email."""
        existing_email = "deik@ee.com"
        response_initial = self.app.post('/add_user', json={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': existing_email,
            'password': 'securePassword123',
            'age': 25,
            'gender': 'Male'
        })
    
    # Print out the response data for debugging
        print("Initial response data:", response_initial.json)
    
    # Ensure the first addition is successful for test setup
        assert response_initial.status_code == 200, f"Expected 200 OK, got {response_initial.status_code}: {response_initial.json}"

    # Now, attempt to add the same user again to test the failure
        response = self.app.post('/add_user', json={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': existing_email,
            'password': 'anotherSecure123',
            'age': 25,
            'gender': 'Male'
        })

        # Ensure the response for duplicate email is as expected
        assert response.status_code == 400, "Should return a status code of 400 for duplicate email"
        assert 'error' in response.json['status'], "Response status should be 'error'"
        assert 'Email already exists' in response.json['message'], "Error message should indicate that the email already exists"


    def test_get_existing_user(self):
        response = self.app.get(f'/get_user/{self.user_id}')
        data = response.get_json()
        print(f'Response for existing user: {data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', data['status'])

    def test_delete_existing_user(self):
        # Create a user explicitly here for this test
        user_id = add_user("John", "Doe", "john.doe@exale.com", "password123", 30, "Male")
        print(f"User created with ID: {user_id}")

        # Now attempt to delete the user
        response = self.app.delete(f'/delete_user/{user_id}')
        data = response.get_json()
        print(f'Delete existing user response: {data}')

    # Assertions to check if the deletion was successful
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'User deleted successfully')

    # Optionally check if the user is really deleted
        response_check = self.app.get(f'/get_user/{user_id}')
        data_check = response_check.get_json()
        self.assertTrue(response_check.status_code in [404, 200], "Status code should be 404 or 200 based on how non-existing users are handled")
        if response_check.status_code == 404:
            self.assertEqual(data_check['status'], 'error')
            self.assertIn('User not found', data_check['message'])
        elif response_check.status_code == 200:
            self.assertIn('error', data_check['status'])  # Assuming 'error' is part of the response for non-found users even if status code is 200

        
    def test_empty_inputs(self):
        """Test adding a user with empty inputs for required fields."""
        response = self.app.post('/add_user', json={
            'first_name': '',
            'last_name': '',
            'email': '',
            'password': ''
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('Required fields are missing', data['message'])
        

    def test_boundary_values(self):
        """Test adding a user with minimum and maximum boundary values for age."""
        # Define boundary values for the age field
        min_age = 18  # Minimum valid age
        max_age = 99  # Maximum valid age

    # Test minimum age
        response_min = self.app.post('/add_user', json={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': f'john_min_{uuid4()}@example.com',
            'password': 'securePassword123',
            'age': min_age,
            'gender': 'Male'
        })
        print(f"Response for minimum age: {response_min.get_json()}")
        self.assertEqual(response_min.status_code, 200, "Should accept minimum age boundary")

    # Test maximum age
        response_max = self.app.post('/add_user', json={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': f'john_max_{uuid4()}@example.com',
            'password': 'securePassword123',
            'age': max_age,
            'gender': 'Male'
        })
        print(f"Response for maximum age: {response_max.get_json()}")
        self.assertEqual(response_max.status_code, 200, "Should accept maximum age boundary")
        
    def test_invalid_data_types(self):
        """Test adding a user with invalid data types for inputs."""
        unique_email = f"unique_{uuid4()}@example.com"  # Ensures the email is unique for the test
        response = self.app.post('/add_user', json={
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': unique_email,
            'password': 'password123',
            'age': 'twenty-five',  # Intentionally wrong data type
            'gender': 'Female'
        })

        print("Response JSON for invalid data types:", response.json)  # Debugging output

    # Check for correct status code and error message
        self.assertEqual(response.status_code, 400, "Expected a 400 status code for invalid input types")
        self.assertIn('must be an integer', response.json['message'], "Expected a specific error message about the age data type")


    # Add more test methods for other scenarios as needed

    
if __name__ == '__main__':
    unittest.main()
