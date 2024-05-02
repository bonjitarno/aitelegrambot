import re
from validators import email as email_validator
from db.connection import get_db_cursor

def validate_email(email):
    return email_validator(email)

def validate_password(password):
    # Implement password complexity requirements
    if re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
        return True
    return False

def hash_password(password):
    import bcrypt
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def is_email_unique(email):
    with get_db_cursor() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
            count = cursor.fetchone()[0]
            return count == 0
        
def validate_age(age):
    if age is not None:
        if not 18 <= age <= 100:
            raise ValueError("Age must be between 18 and 100.")
