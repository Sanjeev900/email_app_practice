import unittest
from unittest.mock import MagicMock, patch
from process_emails import fetch_emails_from_database, process_email, perform_rule_actions, check_rule_condition, mark_email_as_read, mark_email_as_unread, move_email_to_folder, get_label_id

class TestProcessEmails(unittest.TestCase):

    @patch('process_emails.fetch_all_emails')
    @patch('process_emails.process_email')
    def test_fetch_emails_from_database(self, mock_process_email, mock_fetch_all_emails):
        mock_fetch_all_emails.return_value = [('1', 'email1', 'test_subject', 'sender1', 'test_receiver', '2023-01-01 00:00:00', 'message1'), ('2', 'email2', 'subject2', 'sender2', 'receiver2', '2023-01-02 00:00:00', 'message2')]
        gmail_service = MagicMock()

        fetch_emails_from_database(gmail_service)

        mock_fetch_all_emails.assert_called_once()
        assert mock_process_email.call_count > 0
        mock_process_email.assert_called_with(gmail_service, ('2', 'email2', 'subject2', 'sender2', 'receiver2', '2023-01-02 00:00:00', 'message2'))

    @patch('process_emails.mark_email_as_read')
    @patch('process_emails.move_email_to_folder')
    def test_perform_rule_actions(self, mock_move_email_to_folder, mock_mark_email_as_read):
        gmail_service = MagicMock()
        email_id = '1'
        actions = {'mark_as_read': True, 'move_to_folder': 'SPAM'}

        perform_rule_actions(gmail_service, email_id, actions)

        mock_mark_email_as_read.assert_called_with(gmail_service, email_id)
        mock_move_email_to_folder.assert_called_with(gmail_service, email_id, 'SPAM')

    def test_check_rule_condition(self):
        email_data = ('1', 'email1', 'test_subject', 'sender1', 'test_receiver', '2023-01-01 00:00:00', 'message1')
        
        condition = {'field': 'subject', 'predicate': 'contains', 'value': 'test'}
        self.assertTrue(check_rule_condition(email_data, condition))
        condition = {'field': 'subject', 'predicate': 'does not contain', 'value': '2'}
        self.assertTrue(check_rule_condition(email_data, condition))
        condition = {'field': 'sender', 'predicate': 'contains', 'value': '1'}
        self.assertTrue(check_rule_condition(email_data, condition))
        condition = {'field': 'sender', 'predicate': 'does not contain', 'value': '2'}
        self.assertTrue(check_rule_condition(email_data, condition))
        condition = {'field': 'receiver', 'predicate': 'contains', 'value': 'test'}
        self.assertTrue(check_rule_condition(email_data, condition))
        condition = {'field': 'receiver', 'predicate': 'does not contain', 'value': '2'}
        self.assertTrue(check_rule_condition(email_data, condition))
        condition = {'field': 'message', 'predicate': 'contains', 'value': '1'}
        self.assertTrue(check_rule_condition(email_data, condition))
        condition = {'field': 'message', 'predicate': 'does not contain', 'value': '2'}
        self.assertTrue(check_rule_condition(email_data, condition))
        condition = {'field': 'date', 'predicate': 'greater than', 'value': '2021-01-01'}
        self.assertTrue(check_rule_condition(email_data, condition))
        condition = {'field': 'date', 'predicate': 'lesser than', 'value': '2024-01-01'}
        self.assertTrue(check_rule_condition(email_data, condition))
        
    @patch('process_emails.get_label_id')
    def test_move_email_to_folder(self, mock_get_label_id):
        gmail_service = MagicMock()
        email_id = '1'
        folder_name = 'SPAM'
        mock_get_label_id.return_value = 'label1'

        move_email_to_folder(gmail_service, email_id, folder_name)
        
        mock_get_label_id.assert_called_with(gmail_service, folder_name)
        gmail_service.users().messages().modify.assert_called_with(userId='me', id=email_id, body={'addLabelIds': ['label1']})

    def test_get_label_id(self):
        gmail_service = MagicMock()
        folder_name = 'SPAM'
        labels = {'labels': [{'name': 'SPAM', 'id': 'SPAM'}, {'name': 'folder2', 'id': 'label2'}]}
        gmail_service.users().labels().list.return_value.execute.return_value = labels
        
        self.assertEqual(get_label_id(gmail_service, folder_name), 'SPAM')
        
        folder_name = 'folder3'
        self.assertIsNone(get_label_id(gmail_service, folder_name))

if __name__ == '__main__':
    unittest.main()