# email_app_practice

This repository contains Python scripts designed for seamless Gmail integration, including OAuth authentication, email fetching, and real-time application of customizable rules.

## Installation
Clone the repository to your local machine:
 ```bash
    git clone git@github.com:Sanjeev900/email_app_practice.git

    cd email_app_practice

    virtualenv venv

    source venv/bin/activate

    pip install -r requirements.txt
```

## How to use
First and foremost, run the below command to run database using docker in the project's root directory.
```bash

   docker compose up -d --build
```

To fetch and process emails, follow these steps:

Run the first script to connect to Gmail and fetch emails:

```bash
python fetch_and_save_emails.py
```

Run the second script to process emails, apply rules, and perform actions:

```bash
python process_emails.py
```
