import streamlit as st

conversation_flow = {
    "start": {
        "message": "Hi there! How can I help you today?",
        "options": {
            "Issue related to BN": "BN",
            "Issue related to RN": "RN",
            "Do you want to replace the radio device?": "RMA",
        "Do you want to talk with our customer team executive" : "customer_on_call",
        "Query related to particular release" : "release_query",
        "Congiuration issue?" : "configuration_issue",
        "Your issue is not listed" : "other"
        },
    },
    "BN": {
        "message": "What kind of technical issue are you experiencing on BN?",
        "options": {
            "Is it related to latency?": "BN_LATENCY",
            "Issue to login into device?": "BN_LOGIN",
            "My issue is not mentioned here!!": "other"
        },
    },
    "RN": {
        "message": "What kind of technical issue are you experiencing on RN?",
        "options": {
            "Is it related to latency?": "RN_LATENCY",
            "Issue to login into device?": "RN_LOGIN",
            "My issue is not mentioned here!!": "other"
        },
    },
    "RMA": {
        "message": "Please provide below details",
        "input": True,
    },
    "customer_on_call": {
        "message": "This feature is not live please create ticket we will connect you asap!!",
        "input": True
    },
    "release_query": {
        "message": "Can you please provide the release number?",
        "input": True
    },
    "configuration_issue": {
        "message": "Please describe your issue!",
        "input": True
    },
    "other": {  
        "message": "Please enter your further query:",
        "input": True
    },
    "leaf_node" : {
    "message": "Please describe your issue!",
    "input" : True
    }
}

def main():
    st.title("XYZ Whizz Bot")
    st.write("Hi there, thank you for reaching out. I am XYZ Whizz Bot and I am here to help you.")

    if "current_state" not in st.session_state:
        st.session_state.current_state = "start"
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

    current_state = conversation_flow[st.session_state.current_state]

    for message in st.session_state.chat_history:
        if message.startswith("User:"):
            with st.chat_message("user"):
                st.write(message[5:])
        elif message.startswith("Bot:"):
            with st.chat_message("assistant"):
                st.write(message[4:])

    if "options" in current_state:
        for option, next_state in current_state["options"].items():
            if st.button(option):
                st.session_state.chat_history.append(f"User: {option}")  # Add to history ONLY HERE
                try:
                    if "input" in conversation_flow[next_state] and conversation_flow[next_state]["input"]:
                        st.session_state.current_state = next_state
                        st.rerun()
                    else:
                        st.session_state.chat_history.append(f"Bot: {conversation_flow[next_state]['message']}")
                        st.session_state.current_state = next_state
                        st.rerun()
                except KeyError:
                        st.session_state.current_state = "leaf_node"
                        st.rerun()
    elif "input" in current_state and current_state["input"]:
        st.session_state.user_input = st.text_input("Enter your query:", value=st.session_state.user_input)
        if st.button("Submit"):
            user_query = st.session_state.user_input
            st.session_state.chat_history.append(f"User: {user_query}")
            st.session_state.chat_history.append(f"Bot: Thank you for your question.")
            st.session_state.current_state = "start"
            st.session_state.user_input = ""
            st.rerun()
    elif "leaf" in current_state and current_state["leaf"]:
        if st.button("Do you have any further queries?"):
            st.session_state.current_state = "leaf_query"
            st.rerun()
        if st.button("Go to Main Menu"):
            st.session_state.current_state = "start"
            st.rerun()
    elif st.session_state.current_state == "leaf_query":
        st.session_state.user_input = st.text_input("Enter your query:", value=st.session_state.user_input)

        if st.button("Submit Query"):
            user_query = st.session_state.user_input
            st.session_state.chat_history.append(f"User: {user_query}")
            st.session_state.chat_history.append(f"Bot: Thank you for your question.")
            st.session_state.current_state = "start"
            st.session_state.user_input = ""
            st.rerun()

if __name__ == "__main__":
    main()