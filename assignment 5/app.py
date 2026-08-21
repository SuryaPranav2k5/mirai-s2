import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import requests
import json
import urllib.parse
from io import BytesIO
from gtts import gTTS

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Phase 1: Securely cache Gemini client
@st.cache_resource
def get_gemini_client():
    if not api_key:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        return None

client = get_gemini_client()

if not api_key:
    st.error("Please set the GEMINI_API_KEY environment variable in your .env file.")
    st.stop()

# Phase 1: Sidebar titled "Story Settings" with dropdowns for Story Genre and Art Style
st.sidebar.title("Story Settings")
genre = st.sidebar.selectbox(
    "Story Genre",
    ["Sci-Fi", "Fantasy", "Mystery", "Horror", "Romance", "Cyberpunk"]
)

art_style = st.sidebar.selectbox(
    "Art Style",
    ["Anime", "Photorealistic", "Oil Painting", "Sketch", "Digital Art", "Pixel Art"]
)

# Start / Restart Adventure button in sidebar
if st.sidebar.button("Restart Adventure", use_container_width=True):
    st.session_state.chat = None
    st.session_state.current_scene = None
    st.rerun()

# Phase 1: Initialize st.session_state to store chat history and Gemini chat object
if "chat" not in st.session_state:
    st.session_state.chat = None
if "current_scene" not in st.session_state:
    st.session_state.current_scene = None

# Helper function to parse JSON response
def parse_response(text):
    # Phase 2: Use Python's built-in json library to parse response into usable Python dictionary
    try:
        clean_text = text.strip()
        if clean_text.startswith("```"):
            lines = clean_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            clean_text = "\n".join(lines).strip()
            
        return json.loads(clean_text)
    except Exception as e:
        # Fallback dictionary if JSON is completely broken
        return {
            "story_text": f"The story shifts. (AI raw output: {text[:100]}...)",
            "image_prompt": f"A mysterious landscape, {art_style} style",
            "options": ["Step forward", "Look around"]
        }

# Helper function to download Pollinations image
def get_image(prompt):
    enhanced_prompt = f"{prompt}, {art_style.lower()} style"
    encoded = urllib.parse.quote(enhanced_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}"
    
    # Phase 5: try...except blocks to handle API failures gracefully without crashing
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        st.toast("Image server is busy, skipping visual...")
        return None

# Helper function to generate TTS audio
def get_tts(text):
    # Phase 5: try...except blocks for API calls
    try:
        # Phase 4: Use gTTS to convert the AI's story_text into an audio file
        tts = gTTS(text=text, lang="en")
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.getvalue()
    except Exception as e:
        st.toast("Audio engine is busy, skipping narration...")
        return None

# Starts the story
def start_story():
    # Phase 2: Instruct Gemini via system prompt to strictly return response as JSON object
    system_instruction = f"""You are a stateful Choose Your Own Adventure visual novel story director.
You will generate a branching story based on the choices selected by the user.
Story Genre: {genre}
Art Style: {art_style}

You MUST format your output strictly as a JSON object containing EXACTLY these three keys:
{{
  "story_text": "The narrative paragraph describing the current scene.",
  "image_prompt": "A detailed prompt for generating an image depicting the scene. It should match the art style: {art_style}.",
  "options": [
    "Short description of Choice 1",
    "Short description of Choice 2",
    "Short description of Choice 3"
  ]
}}
Ensure your response is valid JSON and strictly follows this schema."""

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        temperature=0.7,
    )
    
    st.session_state.chat = client.chats.create(
        model="gemini-flash-lite-latest",
        config=config
    )
    
    with st.spinner("Generating first scene..."):
        try:
            response = st.session_state.chat.send_message(
                f"Start a new Choose Your Own Adventure story in the {genre} genre. Introduce the setting."
            )
            scene_data = parse_response(response.text)
            
            image_bytes = get_image(scene_data.get("image_prompt", ""))
            audio_bytes = get_tts(scene_data.get("story_text", ""))
            
            st.session_state.current_scene = {
                "story_text": scene_data.get("story_text", ""),
                "image_prompt": scene_data.get("image_prompt", ""),
                "image_bytes": image_bytes,
                "audio_bytes": audio_bytes,
                "options": scene_data.get("options", [])
            }
        except Exception as e:
            st.error(f"Error starting story: {e}")

# Continues the story
def choose_option(option_text):
    with st.spinner("Generating next scene..."):
        try:
            response = st.session_state.chat.send_message(option_text)
            scene_data = parse_response(response.text)
            
            image_bytes = get_image(scene_data.get("image_prompt", ""))
            audio_bytes = get_tts(scene_data.get("story_text", ""))
            
            st.session_state.current_scene = {
                "story_text": scene_data.get("story_text", ""),
                "image_prompt": scene_data.get("image_prompt", ""),
                "image_bytes": image_bytes,
                "audio_bytes": audio_bytes,
                "options": scene_data.get("options", [])
            }
        except Exception as e:
            st.error(f"Error generating next scene: {e}")


# Main application UI
st.title("Choose Your Own Adventure Engine")

# Auto-start story if not initialized
if st.session_state.chat is None:
    start_story()
    st.rerun()

scene = st.session_state.current_scene

if scene:
    # Phase 4: Render both the story_text and the image on the screen using st.session_state
    if scene.get("image_bytes"):
        st.image(scene["image_bytes"], caption=scene.get("image_prompt"))
    else:
        st.info("(Image generation skipped)")
        
    st.info(scene["story_text"])
    
    # Phase 4: Use Streamlit's st.audio() component to play the generated narration file
    if scene.get("audio_bytes"):
        st.audio(scene["audio_bytes"], format="audio/mp3")
        
    st.write("---")
    st.subheader("What do you do next?")
    
    # Phase 3: Write a for loop that iterates over the options list and dynamically generates an st.button()
    options = scene.get("options", [])
    for idx, option in enumerate(options):
        # Click action sends option text to Gemini API
        if st.button(option, key=f"option_{idx}", use_container_width=True):
            choose_option(option)
            st.rerun()
