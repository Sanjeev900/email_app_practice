import psycopg2
from psycopg2 import sql
from contextlib import contextmanager

# PostgreSQL credentials
DB_HOST = 'localhost'
DB_NAME = 'postgres'
DB_USER = 'sanjeev'
DB_PASSWORD = 'sanjeevemail'

@contextmanager
def connect():
    """
    Establish a connection to the PostgreSQL database.

    Yields:
        psycopg2.extensions.connection: Connection to the PostgreSQL database.
    """
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    try:
        yield conn 
    finally:
        conn.close()

def create_email_table():
    """
    Create the 'email_details' table if it does not exist.
    """
    print("Checking if 'email_details' table exists and creating if not...")
    with connect() as conn:
        with conn.cursor() as cursor:
            # Create the 'email_details' table if it does not exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_details (
                    id SERIAL PRIMARY KEY,
                    emailid VARCHAR,
                    subject TEXT,
                    sender TEXT,
                    receiver TEXT,
                    date TIMESTAMP,
                    message TEXT
                )
            ''')
            conn.commit()

def insert_email(email_id, subject, sender, receiver, date, message):
    """
    Insert email details into the 'email_details' table.

    Args:
        email_id (str): Email ID.
        subject (str): Email subject.
        sender (str): Sender's email address.
        receiver (str): Receiver's email address.
        date (str): Email date.
        message (str): Email message.
    """
    with connect() as conn:
        with conn.cursor() as cursor:
            # Insert email details into the 'email_details' table
            query = sql.SQL('''
                INSERT INTO email_details (emailid, subject, sender, receiver, date, message)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''')
            cursor.execute(query, (email_id, subject, sender, receiver, date, message))
            conn.commit()

def fetch_all_emails():
    """
    Fetch all emails from the 'email_details' table.

    Returns:
        list: List of tuples representing email details.
    """
    with connect() as conn:
        with conn.cursor() as cursor:
            # Fetch all emails from the 'email_details' table
            cursor.execute('SELECT * FROM email_details')
            return cursor.fetchall()
