from simple_salesforce import Salesforce
import os
import requests
from dotenv import load_dotenv

load_dotenv()
auth_url = os.getenv("AUTH_URL")
session_url = os.getenv("SANDBOX_URL")
    
def auth_token():
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


def create_ticket_utility(acces_token, data):
    try:
        sf = Salesforce(instance_url=session_url, session_id=acces_token)
        print(data)
        try:
            result = sf.Case.create(data)
            pass
        except Exception as e:
            print(e)

        print(f"Case created successfully: {result}")
        case_id = result['id']
        print(f"Case ID: {case_id}")
        return case_id
    except Exception as e:
        print(f"An error occurred: {e}")
        try:
            retrieved_case = sf.Case.get(case_id)
            print(f"Retrieved case details: {retrieved_case}")
        except Exception as e:
            print(f"Error retrieving case: {e}")
            