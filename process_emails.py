import os
import json
import datetime
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from database import fetch_all_emails
from fetch_and_save_emails import authenticate_gmail

# Constants
CLIENT_SECRET_FILE = 'auth/credentials.json'
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]

# Load the Rules from JSON
with open('action_rules/rules.json', 'r') as rules_file:
    rules_data = json.load(rules_file)

def fetch_emails_from_database(gmail_service):
    """
    Fetch emails from the database and initiate processing.

    Args:
        gmail_service (googleapiclient.discovery.Resource): Gmail API service.

    Returns:
        None
    """
    try:
        print("=" * 60)
        print("Fetching Emails From Database")
        print("=" * 60) 
        emails = fetch_all_emails()
        if not emails:
            print('No emails found in the database.')
        else:
            print(f'Total emails in the database: {len(emails)}')
            print("=" * 60)
            print("Processing Emails")
            print("=" * 60) 
            for email in emails:
                process_email(gmail_service, email)
    
    except Exception as e:
        print(f"Error fetching emails from the database: {str(e)}")

def process_email(gmail_service, email_data):
    """
    Process an email based on predefined rules.

    Args:
        gmail_service (googleapiclient.discovery.Resource): Gmail API service.
        email_data (tuple): Tuple containing email details.

    Returns:
        None
    """

    Id = email_data[0]
    email_id = email_data[1]
    email_subject = email_data[2]
    email_sender = email_data[3]
    email_receiver = email_data[4]
    email_date = email_data[5]
    email_message = email_data[6]

    for rule in rules_data:
        for rule_name, rule_data in rule.items():
            if rule_data.get('active') == 1 and rule_data.get('collective_predicate') == "Any":
                if any(check_rule_condition(email_data, condition) for condition in rule_data.get("conditions")):
                    perform_rule_actions(gmail_service, email_id, rule_data["actions"])

            if rule_data.get('active') == 1 and rule_data.get('collective_predicate') == "All":
                if all(check_rule_condition(email_data, condition) for condition in rule_data.get("conditions")):
                    perform_rule_actions(gmail_service, email_id, rule_data["actions"])

def perform_rule_actions(gmail_service, email_id, actions):
    """
    Perform actions based on rule conditions.

    Args:
        gmail_service (googleapiclient.discovery.Resource): Gmail API service.
        email_id (str): ID of the email.
        actions (dict): Dictionary containing rule actions.

    Returns:
        None
    """
    try:
        if actions["mark_as_read"]:
            mark_email_as_read(gmail_service, email_id)
        else:
            mark_email_as_unread(gmail_service, email_id)

        if "move_to_folder" in actions:
            move_email_to_folder(gmail_service, email_id, actions['move_to_folder'])

        print("=" * 60)
        print("Rule Condition Checked and Action Performed for Email : ", email_id)
        print("=" * 60)

    except Exception as e:
        print(f"Error performing rule actions: {str(e)}")

def check_rule_condition(email_data, condition):
    """
    Check if an email satisfies a rule condition.

    Args:
        email_data (tuple): Tuple containing email details.
        condition (dict): Dictionary representing a rule condition.

    Returns:
        bool: True if the condition is satisfied, False otherwise.
    """
    field = condition["field"]
    predicate = condition["predicate"]
    value = condition["value"]

    if field == "subject":
        if predicate == "contains" and value in email_data[2]:
            print("Condition matched: subject contains value")
            return True
        elif predicate == "does not contain" and value not in email_data[2]:
            return True
    elif field == "sender":
        if predicate == "contains" and value in email_data[3]:
            return True
        elif predicate == "does not contain" and value not in email_data[3]:
            return True
    elif field == "receiver":
        if predicate == "contains" and value in email_data[4]:
            return True
        elif predicate == "does not contain" and value not in email_data[4]:
            return True
    elif field == "message":
        if predicate == "contains" and value in email_data[6]:
            return True
        elif predicate == "does not contain" and value not in email_data[6]:
            return True
    elif field == "date":
        email_date = datetime.datetime.strptime(str(email_data[5]), "%Y-%m-%d %H:%M:%S")
        rule_date = datetime.datetime.strptime(value, "%Y-%m-%d")
        if predicate == "greater than" and email_date > rule_date:
            return True
        elif predicate == "lesser than" and email_date < rule_date:
            return True
    return False

def mark_email_as_read(gmail_service, email_id):
    """
    Mark an email as read.

    Args:
        gmail_service (googleapiclient.discovery.Resource): Gmail API service.
        email_id (str): ID of the email.

    Returns:
        None
    """
    try:
        gmail_service.users().messages().modify(userId='me', id=email_id, body={'removeLabelIds': ['UNREAD']}).execute()
    except Exception as e:
        print(f"Error marking email as read: {str(e)}")

def mark_email_as_unread(gmail_service, email_id):
    """
    Mark an email as unread.

    Args:
        gmail_service (googleapiclient.discovery.Resource): Gmail API service.
        email_id (str): ID of the email.

    Returns:
        None
    """
    try:
        gmail_service.users().messages().modify(userId='me', id=email_id, body={'addLabelIds': ['UNREAD']}).execute()
    except Exception as e:
        print(f"Error marking email as unread: {str(e)}")

def move_email_to_folder(gmail_service, email_id, folder_name):
    """
    Move an email to a specific folder.

    Args:
        gmail_service (googleapiclient.discovery.Resource): Gmail API service.
        email_id (str): ID of the email.
        folder_name (str): Name of the folder.

    Returns:
        None
    """
    try:
        label_id = get_label_id(gmail_service, folder_name)
        if label_id:
            gmail_service.users().messages().modify(userId='me', id=email_id, body={'addLabelIds': [label_id]}).execute()
        else:
            print(f"Error: Label '{folder_name}' not found.")
    except Exception as e:
        print(f"Error moving email to folder: {str(e)}")

def get_label_id(gmail_service, folder_name):
    """
    Get the label ID for a specific folder.

    Args:
        gmail_service (googleapiclient.discovery.Resource): Gmail API service.
        folder_name (str): Name of the folder.

    Returns:
        str: Label ID for the folder.
    """
    try:
        labels = gmail_service.users().labels().list(userId='me').execute()
        for label in labels['labels']:
            if label['name'] == folder_name:
                return label['id']
        return None
    except Exception as e:
        print(f"Error getting label ID for folder: {str(e)}")
        return None


def main():
    creds = authenticate_gmail()

    # Gmail API service
    gmail_service = build('gmail', 'v1', credentials=creds)
    fetch_emails_from_database(gmail_service)

if __name__ == '__main__':
    main()
    print("=" * 60)
    print("Completed Processing Emails")
    print("=" * 60)
