from flask import request, jsonify
from db.queries import add_user, get_user, update_user, delete_user
from db.question_queries import add_questionnaire, delete_questionnaire, get_questionnaire
from db.validators import validate_age

def setup_routes(app):
    @app.route('/add_user', methods=['POST'])
    def add_user_endpoint():
        data = request.get_json()
        required_fields = ['first_name', 'last_name', 'email', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({"status": "error", "message": "Required fields are missing: " + ", ".join(missing_fields)}), 400

        try:
            user_id = add_user(data['first_name'], data['last_name'], data['email'], data['password'], data.get('age'), data.get('gender'))
            return jsonify({"status": "success", "message": "User added", "user_id": user_id}), 200
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 400
        except RuntimeError as e:
            return jsonify({"status": "error", "message": "Internal server error: " + str(e)}), 500



    @app.route('/get_user/<int:user_id>', methods=['GET'])
    def get_user_endpoint(user_id):
        user_data = get_user(user_id)
        if user_data:
            response = {"status": "success", "user_data": user_data}
        else:
            response = {"status": "error", "message": "User not found"}
        return jsonify(response)

    @app.route('/update_user/<int:user_id>', methods=['PUT'])
    def update_user_endpoint(user_id):
        data = request.get_json()
        email = data.get('email')  # Get the email from the request body
        password = data.get('password')  # Get the password from the request body

        try:
        # Update user will only process email and password updates
            updated_user = update_user(user_id, email=email, password=password)
            response = {
                "status": "success",
                "message": "User updated successfully",
                "updated_user": {
                    "user_id": updated_user['user_id'],
                    "email": updated_user['email']
                }  # Exclude password info from the response for security
            }
        except ValueError as e:
            response = {
                "status": "error",
                "message": str(e)
            }
        return jsonify(response)

    @app.route('/delete_user/<int:user_id>', methods=['DELETE'])
    def delete_user_endpoint(user_id):
        try:
            message = delete_user(user_id)
            response = {"status": "success", "message": message}
        except ValueError as e:
            response = {"status": "error", "message": str(e)}
        return jsonify(response)
    
    @app.route('/add_questionnaire', methods=['POST'])
    def submit_questionnaire():
        data = request.json

    # List of required fields
        required_fields = ['user_id', 'description', 'goals', 'challenges', 'expectations']
        # Initialize a list to keep track of any missing or improperly formatted fields
        missing_fields = []
        invalid_fields = []

    # Check for missing or improperly formatted fields
        for field in required_fields:
            if field not in data or data[field] is None:
                invalid_fields.append(f"{field} is missing")
            elif isinstance(data[field], str) and not data[field].strip():
                invalid_fields.append(f"{field} is empty or contains only whitespace")
            elif field == 'user_id':
                try:
                    data['user_id'] = int(data['user_id'])
                    if data['user_id'] <= 0:
                        invalid_fields.append("user_id (invalid value: must be greater than 0)")
                except ValueError:
                    invalid_fields.append("user_id (not an integer)")

    # Construct an error message if there are issues with the input data
        if invalid_fields:
            return jsonify({'error': 'Validation failed', 'details': invalid_fields}), 400

        # Try to add the questionnaire data to the database
        try:
            questionnaire_id = add_questionnaire(
                data['user_id'], 
                data['description'], 
                data['goals'], 
                data['challenges'], 
                data['expectations']
            )
            return jsonify({'status': 'success', 'questionnaire_id': questionnaire_id, 'message': 'Questionnaire added successfully'}), 201
        except Exception as e:
            # Log the exception and return a server error
            app.logger.error(f"Unexpected error when adding questionnaire: {e}")
            return jsonify({'error': 'Unexpected error', 'message': str(e)}), 500
        
        
    @app.route('/get_questionnaire/<int:user_id>', methods=['GET'])
    def get_questionnaire_endpoint(user_id):
        try:
            user_data = get_questionnaire(user_id)
            if user_data:
                response = {"status": "success", "user_data": user_data}
                return jsonify(response), 200  # Explicitly stating the 200 status
            else:
                response = {"status": "error", "message": "User not found"}
                return jsonify(response), 404  # Not found
        except Exception as e:
            # Handle unexpected issues, e.g., database connection errors
            return jsonify({"status": "error", "message": str(e)}), 500  # Internal server error
    
    @app.route('/delete_questionnaire/<int:user_id>', methods=['DELETE'])
    def delete_questionnaire_endpoint(user_id):
        try:
            if delete_questionnaire(user_id):
                return jsonify({'status': 'success', 'message': 'Questionnaire deleted successfully'}), 200
        except ValueError as e:
            return jsonify({'status': 'error', 'message': str(e)}), 404
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'Failed to delete questionnaire'}), 500
