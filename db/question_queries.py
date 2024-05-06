import psycopg2
import logging
from db.connection import get_db_cursor  # Import the new cursor manager

def add_questionnaire(user_id, description, goals, challenges, expectations):
    """
    Inserts a completed questionnaire into the database for a specified user.
    Assumes that user_id is valid and that the caller has verified user existence.
    """
    try:
        with get_db_cursor(commit=True) as cursor:  # Assuming get_db_cursor is imported from db.connection
            cursor.execute('''
                INSERT INTO questionnaire (user_id, description, goals, challenges, expectations, completed_questionnaire)
                VALUES (%s, %s, %s, %s, %s, TRUE) RETURNING id
            ''', (user_id, description, goals, challenges, expectations))
            questionnaire_id = cursor.fetchone()[0]
            return questionnaire_id
    except psycopg2.IntegrityError as e:
        if 'foreign key constraint' in str(e).lower():
            raise ValueError("Invalid user ID - user does not exist")  # Specific exception if the user ID does not exist
        else:
            raise RuntimeError("Failed to add questionnaire due to a database integrity error")
    except Exception as e:
        print(f"Unexpected error when adding questionnaire: {e}")
        raise RuntimeError("Failed to add questionnaire due to an unexpected error")
    
def get_questionnaire(user_id):
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT user_id, description, goals, challenges, expectations, completed_questionnaire FROM questionnaire WHERE user_id = %s", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                return {
                    'user_id': user_data[0],
                    'description': user_data[1],
                    'goals': user_data[2],
                    'challenges': user_data[3],
                    'expectations': user_data[4],
                    'completed_questionnaire': user_data[5]                
                }
    except Exception as e:
        print(f"Error fetching questionnaire data: {e}")
        return None  # Optionally, raise an error or handle it as needed
    
def delete_questionnaire(user_id):
    with get_db_cursor(commit=True) as cursor:
        try:
            cursor.execute("DELETE FROM questionnaire WHERE user_id = %s", (user_id,))
            deleted_count = cursor.rowcount

            if deleted_count == 0:
                logging.info(f"Attempt to delete questionnaire for user with ID {user_id} failed: User not found.")
                raise ValueError("User not found")

            logging.info(f"Questionnaire for user with ID {user_id} deleted successfully.")
            return True  # Indicating success programmatically

        except Exception as e:
            # Ensuring any database error is caught and logged
            logging.error(f"Error deleting questionnaire for user ID {user_id}: {str(e)}")
            raise  # Optionally re-raise the exception after logging