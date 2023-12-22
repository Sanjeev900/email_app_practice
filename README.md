# email_app_practice

This repository contains Python scripts designed for seamless Gmail integration, including OAuth authentication, email fetching, and real-time application of customizable rules.

## Prerequisite

- python
- docker

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
First and foremost, run the below command to run the database using docker in the project's root directory.
```bash

   docker compose up -d --build
```

To fetch and process emails, follow these steps:

Add your credentials.json file in the *auth* folder. To configure and create your credentials.json file, follow the steps here: https://support.google.com/cloud/answer/6158849?hl=en 

Run the first script to connect to Gmail and fetch emails:

```bash
python fetch_and_save_emails.py
```

Run the second script to process emails, apply rules, and perform actions:

```bash
python process_emails.py
```

## Rules
Path to rules.json file - ```action_rules/rules.json```. Rules files looks like - 

```json
[
    {
        "rule1": {
            "collective_predicate": "All",
            "conditions": [
                {
                    "field": "message",
                    "predicate": "contains",
                    "value": "Hello"
                },
                {
                    "field": "sender",
                    "predicate": "contains",
                    "value": "example@gmail.com"
                },
                {
                    "field": "date",
                    "predicate": "greater than",
                    "value": "2023-12-18"
                }
            ],
            "actions": {
                "mark_as_read": true,
                "move_to_folder": "SPAM"
            },
            "active": 1
        }
    }
]

```

## Testing

Run the following script - 

```bash
python -m unittest 
```
