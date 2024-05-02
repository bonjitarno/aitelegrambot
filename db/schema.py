from db.connection import connect_db, close_db_conn

print("Starting database initialization...")

def create_or_reset_database():
    conn = connect_db()
    cursor = conn.cursor()

    # Drop existing tables with CASCADE to handle dependencies
    cursor.execute('''
        DROP TABLE IF EXISTS questionnaire CASCADE;
        DROP TABLE IF EXISTS routines CASCADE;
        DROP TABLE IF EXISTS users CASCADE;
    ''')

    # Recreate the Users table
    cursor.execute('''
        CREATE TABLE users (
            user_id SERIAL PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER,
            gender TEXT   
        );
    ''')

    # Recreate the Questionnaire table
    cursor.execute('''
        CREATE TABLE questionnaire (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            description TEXT,
            goals TEXT,
            challenges TEXT,
            expectations TEXT,
            completed_questionnaire BOOLEAN DEFAULT FALSE
        );
    ''')

    # Recreate the Routines table
    cursor.execute('''
        CREATE TABLE routines (
            routine_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            title TEXT,
            description TEXT,
            days TEXT,
            start_time TIME,
            end_time TIME,
            recurring_type TEXT DEFAULT 'none',
            end_date DATE
        );
    ''')

    conn.commit()
    cursor.close()
    close_db_conn(conn)
    print("Database schema updated successfully.")
    
if __name__ == '__main__':
    print("Running database schema setup...")
    create_or_reset_database()
    
    