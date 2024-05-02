import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
import os
from dotenv import load_dotenv

username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")

if not (username and password):
    raise EnvironmentError("DB_USERNAME or DB_PASSWORD environment variables are not set.")

connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    user= username,
    password= password,
    host="127.0.0.1",
    port="5432",
    database="user_data"
)

@contextmanager
def get_db_connection():
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)

@contextmanager
def get_db_cursor(connection=None, commit=False):
    # If connection is not provided, acquire a new one
    if connection is None:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                if commit:
                    conn.commit()
            finally:
                cursor.close()
    else:
        cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()