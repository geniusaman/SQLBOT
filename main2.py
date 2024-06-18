import streamlit as st
import requests
import time

# Define the URL for the FastAPI endpoint
API_URL = "http://127.0.0.1:8000/query"

# Define the available models
MODELS = [
    "llama3-8b-8192",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma-7b-it",
    "whisper-large-v3"
]

st.markdown(
    """
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #5e17eb; /* Purple background */
    }
    .stApp {
        background-color: #ffffff; /* White background */
    }
    .title {
        color: #5e17eb; /* Purple title */
        text-align: left;
        font-size: 16px;
    }
    .prompt-input input[type="text"] {
        border: 1px solid #1e90ff; /* DodgerBlue border */
        border-radius: 10px;
        padding: 5px;
        color: #ceaad7; /* Custom color for input text */
    }
    .submit-button {
        background-color: #5e17eb; /* Purple */
        color: white;
        border-radius: 10px;
        padding: 10px;
        font-size: 16px;
        margin-top: 10px;
    }
    .reset-button {
        background-color: #ceaad7; /* Purple */
        color: white;
        border-radius: 10px;
        padding: 10px;
        font-size: 16px;
        margin-top: 10px;
    }
    .logo {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 300px; /* Adjust the width as needed */
        height: auto;
        margin-bottom: 20px; /* Adjust margin-bottom as needed */
        border: 2px solid #5e17eb; /* Border around the logo */
        border-radius: 20px; /* Rounded corners */
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); /* Shadow effect */
    }
    .input-text {
        color: #ceaad7; /* Custom color for input text */
        font-size: 18px;
        margin-top: 5px; /* Adjust margin-top as needed */
        margin-bottom: 5px; /* Adjust margin-bottom as needed */
    }
    .result-text {
        background-color: #262730; /* Black background */
        color: #ffffff; /* White text */
        padding: 10px;
        border-radius: 10px;
        font-size: 18px;
        margin-top: 10px;
    }
    .colored-label {
        color: #1e90ff; /* DodgerBlue color for label */
        font-size: 16px;
        margin-bottom: 5px;
    }
    .conversation-container {
        background-color: #f0f2f6; /* Light gray background */
        border: 1px solid #e6e6e6; /* Light gray border */
        border-radius: 10px;
        padding: 10px;
        margin-top: 10px;
        max-height: 400px; /* Maximum height for the container */
        overflow-y: auto; /* Scrollable container */
    }
    .user-message {
        color: #5e17eb; /* DodgerBlue color for user message */
        font-size: 18px;
        margin-top: 5px; /* Adjust margin-top as needed */
        margin-bottom: 5px;
    }
    .bot-response {
        color: #5e17eb; /* Purple color for bot response */
        font-size: 16px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display company logo
logo_url = "https://github.com/SouSingh/reccomder/blob/main/logo.png?raw=true"  # Replace with your logo's URL or file path
st.markdown(f"<img src='{logo_url}' class='logo'>", unsafe_allow_html=True)

st.markdown("<h1 class='input-text'>🤖 Ask a question about the database...</h1>", unsafe_allow_html=True)

# Model selection in sidebar
st.sidebar.markdown("<h1 class='title'>Select LLMs ⚙️</h1>", unsafe_allow_html=True)
model_name = st.sidebar.selectbox("Select Model", MODELS)

# Prompt input
prompt = st.text_input("Enter your prompt")

# Initialize session state for conversation history
if 'history' not in st.session_state:
    st.session_state.history = []

# Submit button
if st.button("Submit"):
    if prompt:
        # Prepare the request payload
        payload = {
            "prompt": prompt,
            "model_name": model_name
        }

        try:
            # Send the request to the FastAPI server
            response = requests.post(API_URL, json=payload)

            if response.status_code == 200:
                result = response.json().get("response", "No response from model")
                # Append the prompt and response to the conversation history
                st.session_state.history.append({"user": prompt, "bot": result})
            else:
                st.session_state.history.append({"user": prompt, "bot": f"Error: {response.status_code} - {response.json().get('detail', 'Unknown error')}"})
        except requests.exceptions.RequestException as e:
            st.session_state.history.append({"user": prompt, "bot": f"Error: Unable to reach the API. {e}"})
    else:
        st.error("Please enter a prompt.")

# Display the conversation history with live updates for bot response
if st.session_state.history:
    st.markdown("<h1 class='title'>Chat</h1>", unsafe_allow_html=True)
    #st.markdown("<div class='conversation-container'>", unsafe_allow_html=True)
    for entry in st.session_state.history:
        st.markdown(f"<div class='user-message'>👤User: {entry['user']}</div>", unsafe_allow_html=True)

        # For live updating bot response
        response_placeholder = st.empty()
        full_response = entry['bot']
        bot_response = ""
        for char in full_response:
            bot_response += char
            response_placeholder.markdown(f"<div class='input-text'>🤖Bot: {bot_response}</div>", unsafe_allow_html=True)
            time.sleep(0.05)  # Adjust the speed of the typing simulation

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    div.stButton > button:first-child {
        background-color: #5e17eb; /* Purple */
        color: white;
        border-radius: 10px;
        padding: 10px;
        font-size: 16px;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
