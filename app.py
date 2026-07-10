import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

# Load API Key from environment or .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Page Config
st.set_page_config(page_title="AI Multiverse", page_icon="🤖")

st.title("🌍 AI Multiverse")
st.write("Talk with different AI Personalities!")

# Sidebar Configuration
st.sidebar.title("Configuration")

# Fallback: Let user enter API key in sidebar if not in environment
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password", help="Enter your Gemini API key from Google AI Studio.")
    if not api_key:
        st.warning("Please set the GEMINI_API_KEY environment variable (e.g. in a .env file) or enter it in the sidebar to start chatting.")
        st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

# Personality Selectbox
personality = st.sidebar.selectbox(
    "Select Personality",
    [
        "AI Assistant",
        "Pirate Captain",
        "Shakespearean Poet",
        "Tech Support Specialist",
        "Zen Meditation Master"
    ]
)

# Clear Chat Session
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.session_state.chat_session = None

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_personality" not in st.session_state:
    st.session_state.current_personality = personality

# Reset chat session and history if personality changes
if st.session_state.current_personality != personality:
    st.session_state.messages = []
    st.session_state.chat_session = None
    st.session_state.current_personality = personality

# Map personalities to detailed system instructions
PERSONALITY_PROMPTS = {
    "AI Assistant": (
        "You are a helpful, polite, and direct AI assistant. "
        "Keep your responses helpful, clear, and concise."
    ),
    "Pirate Captain": (
        "You are a salty, adventurous pirate captain. "
        "Talk in pirate slang (use terms like 'Ahoy', 'matey', 'ye', 'scurvy dog', 'shiver me timbers'), "
        "tell stories of the sea, and maintain a rowdy but friendly demeanor."
    ),
    "Shakespearean Poet": (
        "You are a dramatic, poetic playwright from the Elizabethan era. "
        "Speak in Shakespearean English, using 'thou', 'thee', 'thine', 'hath', and 'doth', "
        "and try to structure your thoughts poetically, occasionally rhyming."
    ),
    "Tech Support Specialist": (
        "You are a slightly cynical, pragmatic IT support specialist. "
        "Frequently ask if the user has tried restarting their device, use tech jargon, "
        "and express mild frustration with user errors in a humorous way."
    ),
    "Zen Meditation Master": (
        "You are a calm, peaceful Zen meditation master. "
        "Respond with gentle wisdom, advise breathing deeply, finding inner peace, "
        "and keep your tone relaxed, short, and mindful."
    )
}

# Initialize Gemini Chat Session if not already present
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

# Display historical messages in chat view
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Capture new user input
if user_input := st.chat_input("Say something..."):
    # Render user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Generate response from Gemini chat session
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.chat_session.send_message(user_input)
                assistant_response = response.text
                message_placeholder.markdown(assistant_response)
                # Store response in history
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            except Exception as e:
                st.error(f"Error generating response: {e}")
