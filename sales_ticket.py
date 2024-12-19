from simple_salesforce import Salesforce
import os
import requests
from dotenv import load_dotenv

load_dotenv()
# Retrieve credentials from environment variables (recommended)
username = os.getenv("SALESFORCE_USERNAME")
password = os.getenv("SALESFORCE_PASSWORD")
auth_url = os.getenv("AUTH_URL")
session_url = os.getenv("SANDBOX_URL")

def auth_token():
# Define the authentication API endpoint and payload
    # Optional: Specify headers if required (e.g., Content-Type)
    headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
    }

    # Make the POST request to get the access token
    response = requests.post(auth_url, headers=headers)

    # Check the response status
    if response.status_code == 200:
        access_token = response.json().get("access_token")  # Adjust key if different
        print(f"Access Token: {access_token}")
        return access_token
    else:
        print(f"Failed to authenticate: {response.status_code}")
        print(f"Response: {response.text}")


def create_ticket(acces_token, data):
    
    try:
        sf = Salesforce(instance_url=session_url, session_id=acces_token)

        # Data for the new Case (Ticket)
        case_data = {
            'Subject': data["subject"],
            'Description': data["description"],
            'Status': 'New', # Or 'Working', 'Closed', etc.
            'Priority': 'High', # Or 'Medium', 'Low'
            'Origin': 'Web',     # Or 'Phone', 'Email'
            # Add other required or custom fields as needed
        }

        # Create the Case
        try:
            result = sf.Case.create(case_data)
        except Exception as e:
            print(e)

        # Print the result (contains the new Case ID)
        print(f"Case created successfully: {result}")
        case_id = result['id']
        print(f"Case ID: {case_id}")

    except Exception as e:
        print(f"An error occurred: {e}")

    # Example of how to query for the newly created case (optional):
        try:
            retrieved_case = sf.Case.get(case_id)
            print(f"Retrieved case details: {retrieved_case}")
        except Exception as e:
            print(f"Error retrieving case: {e}")
            