from db.connection import get_db_connection, get_db_cursor

def create_or_reset_database():
    # Get a database connection
    with get_db_connection() as conn:
        # Get a cursor
        with get_db_cursor(connection=conn) as cursor:

            # Drop existing tables with CASCADE to handle dependencies
            cursor.execute('''
                DROP TABLE IF EXISTS questionnaire CASCADE;
                DROP TABLE IF EXISTS routines CASCADE;
                DROP TABLE IF EXISTS users CASCADE;
                DROP TABLE IF EXISTS CalendarEvents CASCADE;
                DROP TABLE IF EXISTS Workouts CASCADE;
                DROP TABLE IF EXISTS Exercises CASCADE;
                DROP TABLE IF EXISTS SleepRecords CASCADE;
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

            # Recreate the Questionnaire table with user_id as a foreign key
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

            # Create the CalendarEvents table
            cursor.execute('''
                CREATE TABLE CalendarEvents (
                    event_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id),
                    title TEXT,
                    description TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    location TEXT,
                    event_type TEXT
                );
            ''')

            # Create the Workouts table
            cursor.execute('''
                CREATE TABLE Workouts (
                    workout_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id),
                    date DATE,
                    duration INTEGER,
                    intensity TEXT,
                    notes TEXT
                );
            ''')

            # Create the Exercises table
            cursor.execute('''
                CREATE TABLE Exercises (
                    exercise_id SERIAL PRIMARY KEY,
                    workout_id INTEGER REFERENCES Workouts(workout_id),
                    name TEXT,
                    reps INTEGER,
                    sets INTEGER,
                    weight DECIMAL(10, 2)
                );
            ''')

            # Create the SleepRecords table
            cursor.execute('''
                CREATE TABLE SleepRecords (
                    sleep_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id),
                    sleep_start TIMESTAMP,
                    sleep_end TIMESTAMP,
                    quality TEXT,
                    notes TEXT
                );
            ''')

    print("Database schema updated successfully.")

if __name__ == '__main__':
    print("Running database schema setup...")
    create_or_reset_database()