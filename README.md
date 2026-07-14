# The Multiverse of Chatbots 🤖

A stateful, multi-personality Streamlit chatbot powered by Google Gemini. 

## Features
- **Memory Vault (`st.session_state`)**: Retains conversation history across user interactions and sidebar adjustments.
- **Dynamic Personalities**: Switch between multiple AI roles (Hacker, Comedian, Motivational Coach, Friendly Teacher, AI Assistant) via the sidebar.
- **Streamlit Native Chat UI**: Utilizes modern `st.chat_input` and `st.chat_message` elements.

## Getting Started

### 1. Installation
Clone the repository, set up a virtual environment, and install the dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file based on `.env.example` and add your Google Gemini API key:
```env
GEMINI_API_KEY=your_api_key_here
```

### 3. Run the App
Start the Streamlit application:
```bash
streamlit run app.py
```
