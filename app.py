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

# Clear Chat History Button in Sidebar
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.session_state.chat_session = None

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_personality" not in st.session_state:
    st.session_state.current_personality = personality

# Reset session state on personality switch
if st.session_state.current_personality != personality:
    st.session_state.messages = []
    st.session_state.chat_session = None
    st.session_state.current_personality = personality

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

# Initialize Gemini Chat Session
if "chat_session" not in st.session_state or st.session_state.chat_session is None:
    system_instruction = PERSONALITY_PROMPTS[personality]
    try:
        st.session_state.chat_session = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
    except Exception as e:
        st.error(f"Failed to initialize Gemini Chat session: {e}")
        st.stop()

# Main Body Title
st.title("The MULTIVERSE OF CHATBOTS")

# Input Form (matching the screenshot layout)
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Say something:")
    submit_button = st.form_submit_button(label="SEND")

# Process submit
if submit_button and user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get response
    try:
        response = st.session_state.chat_session.send_message(user_input)
        assistant_response = response.text
        # Append model response
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    except Exception as e:
        st.error(f"Error generating response: {e}")

# Render chat history below the form
if st.session_state.messages:
    st.write("### Conversation History")
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"👤 **You:** {msg['content']}")
        else:
            st.markdown(f"🤖 **{personality}:** {msg['content']}")
        st.write("---")
