import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from database import connect, create_email_table, insert_email, fetch_all_emails

class TestDatabase(unittest.TestCase):

    @patch('psycopg2.connect')
    def test_connect(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        with connect() as conn:
            pass  # Do nothing

        mock_connect.assert_called_once_with(
            host='localhost', database='postgres', user='sanjeev', password='sanjeevemail'
        )
        mock_connection.close.assert_called_once()

    @patch('psycopg2.connect')
    def test_create_email_table(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        create_email_table()
        mock_connection.commit.assert_called_once()

    @patch('psycopg2.connect')
    def test_insert_email(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        insert_email('123', 'test_subject', 'sender1', 'test_receiver', '2023-12-20 12:30:00', 'message1')

        mock_connection.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
