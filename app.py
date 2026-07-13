import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

# Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Please set the GEMINI_API_KEY environment variable in your .env file to start chatting.")
    st.stop()

client = genai.Client(api_key=api_key)

# Page Config
st.set_page_config(page_title="The Multiverse of Chatbots", page_icon="🤖")

# Sidebar - Who do you want to talk to?
personality = st.sidebar.selectbox(
    "Who do you want to talk to?",
    [
        "An expert Hacker",
        "Stand-up Comedian",
        "Motivational Coach",
        "Friendly Teacher",
        "AI Assistant"
    ]
)

# Define system prompts for each personality
PERSONALITY_PROMPTS = {
    "An expert Hacker": (
        "You are an elite, expert hacker. Talk in cyber jargon, use terms like 'backdoor', "
        "'firewall', 'payload', 'mainframe', speak in a mysterious cyber tone, and keep your responses tech-heavy."
    ),
    "Stand-up Comedian": (
        "You are a witty stand-up comedian. Respond with funny observational jokes, dry humor, "
        "and witty remarks based on what the user says."
    ),
    "Motivational Coach": (
        "You are an intense motivational coach. Use energetic words, urge the user to achieve greatness, "
        "use exclamation marks, and keep the energy extremely high."
    ),
    "Friendly Teacher": (
        "You are a kind, encouraging school teacher. Be supportive, explain things simply, "
        "and use warm, friendly emojis."
    ),
    "AI Assistant": (
        "You are a helpful, neutral, and direct AI assistant."
    )
}

# Main Body Title
st.title("The MULTIVERSE OF CHATBOTS")

# Task 1: Initialize the Memory Vault
if "messages" not in st.session_state:
    st.session_state.messages = []

# Task 2: Render the Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Task 3: Upgrade the Input UI
if user_message := st.chat_input("Say something..."):

    # Task 4: Save the user message to memory
    st.session_state.messages.append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.write(user_message)

    # Generate and display the AI response
    try:
        with st.spinner("Thinking..."):
            response = client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=PERSONALITY_PROMPTS[personality]
                )
            )
        # Task 4: Save the assistant response to memory
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.write(response.text)
    except Exception as e:
        st.error(f"Error generating response: {e}")
