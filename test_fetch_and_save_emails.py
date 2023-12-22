import unittest
from unittest.mock import patch, MagicMock
from fetch_and_save_emails import clean_email_content, retrieve_and_insert_email_details, get_email_details, authenticate_gmail, main

class TestFetchAndSaveEmails(unittest.TestCase):

    def test_clean_email_content(self):
        content = "Sample <b>content</b> with <script>alert('danger')</script> tags."
        cleaned_content = clean_email_content(content)
        self.assertEqual(cleaned_content, "Sample content with alert('danger') tags.")

    @patch('fetch_and_save_emails.build')
    @patch('fetch_and_save_emails.insert_email')
    @patch('fetch_and_save_emails.get_email_details')
    def test_retrieve_and_insert_email_details(self, mock_get_email_details, mock_insert_email, mock_build):
        credentials_mock = MagicMock()
        gmail_service_mock = mock_build.return_value
        message_id = '123'

        mock_get_email_details.return_value = {
            'email_id': '456',
            'subject': 'test_subject',
            'sender': 'sender1',
            'receiver': 'test_receiver',
            'date': '2023-01-01 12:00:00',
            'message': '<script>message1'
        }

        retrieve_and_insert_email_details(message_id, credentials_mock)

        mock_get_email_details.assert_called_once_with(message_id, gmail_service_mock)
        mock_insert_email.assert_called_once_with(
            '456', 'test_subject', 'sender1', 'test_receiver', '2023-01-01 12:00:00', 'message1')

    @patch('fetch_and_save_emails.fetch_detailed_email')
    def test_get_email_details(self, mock_fetch_detailed_email):
        gmail_service_mock = MagicMock()
        message_id = '123'

        msg_mock = {
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'test_subject'},
                    {'name': 'From', 'value': 'sender1'},
                    {'name': 'To', 'value': 'test_receiver'},
                    {'name': 'Date', 'value': 'Sat, 01 Jan 2022 12:00:00 +0000'},
                ],
            },
            'snippet': 'message1',
            'id': '123',
        }

        mock_fetch_detailed_email.return_value = msg_mock

        response = get_email_details(message_id, gmail_service_mock)

        self.assertEqual(response['email_id'], '123')
        self.assertEqual(response['subject'], 'test_subject')
        self.assertEqual(response['sender'], 'sender1')
        self.assertEqual(response['receiver'], 'test_receiver')
        self.assertEqual(response['date'], '2022-01-01 12:00:00')
        self.assertEqual(response['message'], 'message1')

    @patch('fetch_and_save_emails.credentials.Credentials.from_authorized_user_file')
    def test_authenticate_gmail(self, mock_credentials):
        creds_mock = MagicMock()
        creds_mock.valid = True
        mock_credentials.return_value = creds_mock

        credentials = authenticate_gmail()

        mock_credentials.assert_called_once_with('token.json', ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.labels'])
        self.assertEqual(credentials, creds_mock)

    @patch('fetch_and_save_emails.build')
    @patch('fetch_and_save_emails.authenticate_gmail')
    @patch('fetch_and_save_emails.create_email_table')
    def test_main(self, mock_create_email_table, mock_authenticate_gmail, mock_build):
        credentials_mock = MagicMock()
        gmail_service_mock = mock_build.return_value
        gmail_results_mock = {'messages': [{'id': '123'}, {'id': '456'}]}
        gmail_service_mock.users.return_value.messages.return_value.list.return_value.execute.return_value = gmail_results_mock
        mock_authenticate_gmail.return_value = credentials_mock

        with patch('fetch_and_save_emails.retrieve_and_insert_email_details') as mock_retrieve_insert:
            main()

            mock_create_email_table.assert_called_once()
            mock_authenticate_gmail.assert_called_once()
            mock_build.assert_called_once_with('gmail', 'v1', credentials=credentials_mock)
            
            gmail_service_mock.users.return_value.messages.return_value.list.assert_called_once_with(
                userId='me', labelIds=['INBOX'], maxResults=10)
            
            assert gmail_service_mock.users.return_value.messages.return_value.list.return_value.execute.call_count > 0
            
            mock_retrieve_insert.assert_has_calls([
                unittest.mock.call('123', credentials_mock),
                unittest.mock.call('456', credentials_mock)
            ])

if __name__ == '__main__':
    unittest.main()
