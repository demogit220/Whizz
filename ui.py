import streamlit as st
import requests

# Backend API URL
API_URL = "http://127.0.0.1:5000/v1/query"
API_URL_CREATE_TICKET = "http://127.0.0.1:5000/v1/create_ticket"

def create_ticket(payload):
    try:
        response = requests.post(API_URL_CREATE_TICKET, json=payload)
        if response.status_code == 200:
            data = response.json()
            st.success(f"Ticket created successfully! Ticket ID: {data['ticket_id']}")
            # Add the response to chat history
            st.session_state.chat_history.append(("Ticket creation", f"Ticket created successfully! Ticket ID: {data['ticket_id']}"))
        else:
            error = response.json().get("error", "An error occurred.")
            st.error(f"Failed to create ticket: {error}")
            # Add the error response to chat history
            st.session_state.chat_history.append(("Ticket creation", f"Failed to create ticket: {error}"))
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        # Add error to chat history
        st.session_state.chat_history.append(("Ticket creation", f"An error occurred: {str(e)}"))

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # List of (user_message, bot_response) tuples
if "stage" not in st.session_state:
    st.session_state.stage = "greeting"

# Function to display chat history
def display_chat_history():
    if st.session_state.chat_history:
        for user_message, bot_response in st.session_state.chat_history:
            st.markdown(f"**You:** {user_message}")
            st.markdown(f"**Bot:** {bot_response}")
            st.markdown("---")
# Function to send query to the backend
def send_query(query):
    response = requests.post(API_URL, json={"query": query})
    if response.status_code == 200:
        data = response.json()
        return data.get("response", "No response received.")
    else:
        return f"Error: {response.status_code}"

# Streamlit app layout
st.title("Whizz")

# Display chat history
display_chat_history()

# Main app logic
if st.session_state.stage == "greeting":
    st.write("Hello! How may I help you?")
    st.session_state.stage = "menu"

if st.session_state.stage == "menu":
    st.write("Please select an option for further assistance:")
    options = ["RN", "BN", "Release Notes", "RMA", "Salesforce Ticket Creation", "Feedback"]
    choice = st.radio("Choose an option:", options)

    if st.button("Proceed"):
        if choice == "BN":
            st.session_state.stage = "bn"
        elif choice == "Salesforce Ticket Creation":
            st.session_state.stage = "ticket_basics"
        elif choice == "Feedback":
            st.session_state.stage = "feedback"

# BN Handling
if st.session_state.stage == "bn":
    st.write("Enter your query for BN:")
    query = st.chat_input("Your query:")
    if query:
        # Send query to backend
        response = send_query(query)
        # Update chat history
        st.session_state.chat_history.append((query, response))
        # Display response
        st.markdown(f"**Bot:** {response}")
        # Ask for satisfaction
        satisfied = st.radio("Are you satisfied with the response?", ["No", "Yes"])
        if satisfied:
            if satisfied == "Yes":
                st.markdown("**Bot:** Thank you!")
                st.session_state.chat_history.append(("Are you satisfied with the response?", "Thank you!"))
                st.session_state.stage = "menu"
            elif satisfied == "No":
                st.markdown("I apologize if my previous response wasn't helpful. Please file salesforce ticket")
                st.session_state.chat_history.append(("Are you satisfied with the response?", "Creating a Salesforce ticket..."))
                st.markdown("**Bot:** Ticket created!")
                st.session_state.stage = "menu"
        if satisfied == "":
                st.session_state.stage = "menu"
elif st.session_state.stage == "ticket_basics":
    st.write("Please fill the below data")
    
    with st.form("ticket_form"):
        subject = st.text_input("Subject")
        description = st.text_input("Description")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        origin = st.selectbox("Origin", ["Web", "Mobile"])
        account_id = st.text_input("AccountId")
        # Submit button
        submitted = st.form_submit_button("Submit")

    if submitted:
        # Validate if all required fields are filled
        if not subject or not description or not account_id:
            st.error("Please fill in all required fields.")
        else:
            # Create payload for ticket creation
            payload = {
                "Origin": origin,
                "Status": "New",
                "Description": description,
                "Subject": subject,
                "Priority": priority,
            }

            # Add form data to chat history as a user message
            st.session_state.chat_history.append(("User", f"Subject: {subject}"))
            st.session_state.chat_history.append(("User", f"Description: {description}, Priority: {priority}, Shipping Address: {account_id if account_id else 'N/A'}"))

            # Call the API to create the ticket and then clear the form
            create_ticket(payload)

            # After submission, reset the stage to avoid displaying the form again
            st.session_state.stage = "menu"
