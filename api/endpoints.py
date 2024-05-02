from flask import request, jsonify
from db.queries import add_user, get_user, update_user, delete_user
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
