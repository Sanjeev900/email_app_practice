import string
import re
import os
import datetime
import email.utils
import json
import html
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from database import create_email_table, insert_email, fetch_all_emails

# Constants
CLIENT_SECRET_FILE = 'auth/credentials.json'
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]

def clean_email_content(content):
    """
    Remove HTML tags and non-printable characters from the email content.

    Args:
        content (str): Email content to be cleaned.

    Returns:
        str: Cleaned email content.
    """
    # Remove HTML tags
    cleaned_content = html.unescape(content)
    cleaned_content = re.sub(r'<.*?>', '', cleaned_content)

    # Remove non-printable characters
    cleaned_content = ''.join(filter(lambda x: x in string.printable, cleaned_content))

    return cleaned_content

def retrieve_and_insert_email_details(message_id, credentials):
    """
    Fetch email details using the Gmail API, clean content, and insert it into the database.

    Args:
        message_id (str): The ID of the Gmail message.
        credentials (google.auth.credentials.Credentials): Google API credentials.

    Returns:
        None
    """
    try:
        gmail_service = build('gmail', 'v1', credentials=credentials)
        
        response = get_email_details(message_id, gmail_service)

        cleaned_email = clean_email_content(response['message'])
        insert_email(response['email_id'], response['subject'], response['sender'], response['receiver'], response['date'], cleaned_email)

    except Exception as e:
        print(f"Error fetching email details: {str(e)}")

def fetch_detailed_email(message_id, gmail_service):
    return gmail_service.users().messages().get(userId='me', id=message_id, format='full').execute()

def get_email_details(message_id, gmail_service):
    """
    Fetch email details using the Gmail API.

    Returns:
        dict: Dictionary containing email details.
    """
    msg = fetch_detailed_email(message_id, gmail_service)
    headers = msg['payload']['headers']
    subject = [header['value'] for header in headers if header['name'] == 'Subject'][0]
    sender = [header['value'] for header in headers if header['name'] == 'From'][0]
    receiver = [header['value'] for header in headers if header['name'] == 'To'][0]
    date = [header['value'] for header in headers if header['name'] == 'Date'][0]
    formatted_date = email.utils.parsedate_to_datetime(date)
    email_date = formatted_date.strftime('%Y-%m-%d %H:%M:%S')
    message_body = msg['snippet']
    email_id = msg['id']
    
    response_json = {
        "email_id": email_id,
        "sender": sender,
        "receiver": receiver,
        "date": email_date,
        "subject": subject,
        "message": message_body
    }
    return response_json


def authenticate_gmail():
    """
    Authenticate the Gmail API and obtain credentials.

    Returns:
        google.auth.credentials.Credentials: Google API credentials.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = credentials.Credentials.from_authorized_user_file('token.json', GMAIL_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def main():
    """
    Main function to fetch and save emails using the Gmail API.

    Returns:
        None
    """
    create_email_table()
    gmail_credentials = authenticate_gmail()

    gmail_api_service = build('gmail', 'v1', credentials=gmail_credentials)
    gmail_results = gmail_api_service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10).execute()
    gmail_messages = gmail_results.get('messages', [])

    if gmail_messages:
        print("=" * 60)
        print("Fetching & Saving Emails")
        print("=" * 60) 
        temp = 1
        for message in gmail_messages:
            print (" Processed email - ", temp, "/", len(gmail_messages))
            temp += 1 
            retrieve_and_insert_email_details(message['id'], gmail_credentials) 
    else:
        print("No Emails")

if __name__ == '__main__':
    main()
    print("=" * 60)
    print("Completed Saving Emails")
    print("=" * 60)
