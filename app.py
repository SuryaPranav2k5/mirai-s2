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

# Input Form (matching the screenshot layout)
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Say something:")
    submit_button = st.form_submit_button(label="SEND")

# Process submit and generate response (without keeping conversation history)
if submit_button and user_input:
    try:
        with st.spinner("Thinking..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_input,
                config=types.GenerateContentConfig(
                    system_instruction=PERSONALITY_PROMPTS[personality]
                )
            )
            # Render the response
            st.write(f"### Response from {personality}:")
            st.write(response.text)
    except Exception as e:
        st.error(f"Error generating response: {e}")
