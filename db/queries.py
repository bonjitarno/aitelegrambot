import psycopg2
from db.validators import validate_email, hash_password, validate_password, is_email_unique
from db.connection import get_db_cursor  # Import the new cursor manager

def add_user(first_name, last_name, email, password, age=None, gender=None):
    # Validate email format
    if not validate_email(email):
        raise ValueError("Invalid email format")
    
    # Check if the email is unique
    if not is_email_unique(email):
        raise ValueError("Email already exists")

    # Validate data types for age and gender
    if age is not None:
        if not isinstance(age, int) or age < 0 or age > 120:  # Assuming age should be between 0 and 120
            raise ValueError("must be an integer.")
    
    if gender is not None:
        if not isinstance(gender, str) or gender not in ['Male', 'Female', 'Other']:  # Example gender validation
            raise ValueError("Gender must be either 'Male', 'Female', or 'Other'.")

    # Hash the password securely
    hashed_password = hash_password(password)
    
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute('''
                INSERT INTO users (first_name, last_name, email, password, age, gender)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING user_id
            ''', (first_name, last_name, email, hashed_password, age, gender))
            user_id = cursor.fetchone()[0]
            return user_id
    except psycopg2.IntegrityError as e:
        if 'unique constraint' in str(e).lower():
            raise ValueError("Email already exists")  # More specific exception if the unique constraint is violated
        else:
            raise RuntimeError("Failed to add user due to an integrity error")  # General integrity error
    except Exception as e:
        print(f"Unexpected error when adding user: {e}")
        raise RuntimeError("Failed to add user due to an unexpected error")  # Raise a general runtime error for other exceptions
    
def get_user(user_id):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT user_id, first_name, last_name, email, password, age, gender FROM users WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            return {
                'user_id': user_data[0],
                'first_name': user_data[1],
                'last_name': user_data[2],
                'email': user_data[3],
                'password': user_data[4],
                'age': user_data[5],
                'gender': user_data[6]
            }
        return None

def update_user(user_id, email=None, password=None):
    updates = []
    params = []
    if email:
        if not validate_email(email):
            raise ValueError("Invalid email format")
        updates.append("email = %s")
        params.append(email)

    if password:
        if not validate_password(password):
            raise ValueError("Password does not meet complexity requirements")
        hashed_password = hash_password(password)
        updates.append("password = %s")
        params.append(hashed_password)

    if not updates:
        raise ValueError("No valid field to update")

    params.append(user_id)
    update_query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s RETURNING user_id, email, password"

    with get_db_cursor(commit=True) as cursor:
        cursor.execute(update_query, params)
        updated_user = cursor.fetchone()
        if not updated_user:
            raise ValueError("User not found or no update made")
        return {
            'user_id': updated_user[0],
            'email': updated_user[1],
            'password': updated_user[2]  # Be cautious with returning sensitive data like passwords
        }

def delete_user(user_id):
    with get_db_cursor(commit=True) as cursor:
        try:
            # First, delete any questionnaires associated with the user.
            # This step assumes that there are no further nested foreign key dependencies in the questionnaire table.
            cursor.execute("DELETE FROM questionnaire WHERE user_id = %s", (user_id,))
            print(f"Deleted questionnaires for user with ID {user_id}.")  # Log for successful deletion of questionnaires

            # Proceed to delete the user.
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            deleted_count = cursor.rowcount
            if deleted_count == 0:
                print(f"User with ID {user_id} not found.")  # Log for debugging
                raise ValueError("User not found")

            print(f"User with ID {user_id} deleted successfully.")  # Log for successful deletion
            return "User deleted successfully"

        except Exception as e:
            print(f"Failed to delete user with ID {user_id}: {e}")  # Log any exception that arises
            raise RuntimeError(f"Failed to delete user due to: {str(e)}")  # Raise a more generic error for external handling

def is_email_unique(email):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
        count = cursor.fetchone()[0]
        return count == 0