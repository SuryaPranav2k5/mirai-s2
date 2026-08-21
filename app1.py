import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

# Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Please set the GEMINI_API_KEY environment variable in your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)

# Page configuration
st.set_page_config(page_title="The AI Image Studio", page_icon="🎨")

# Sidebar
st.sidebar.title("Generation Settings")
art_style = st.sidebar.selectbox(
    "Select Art Style",
    ["Photorealistic", "Anime", "Oil Painting", "Watercolor", "Sketch", "Digital Art"]
)

# Width & Height Sliders
width = st.sidebar.slider("Image Width", min_value=256, max_value=1024, value=768, step=128)
height = st.sidebar.slider("Image Height", min_value=256, max_value=1024, value=768, step=128)

# Main Page
st.title("The AI Image Studio")
user_prompt = st.text_input("Describe your masterpiece:")

if user_prompt:
    try:
        with st.spinner("Generating..."):
            final_prompt = f"{user_prompt}, {art_style.lower()} style"
            
            result = client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=final_prompt
            )
            
            # Display image directly using bytes and the selected width
            for generated_image in result.generated_images:
                st.image(generated_image.image_bytes, caption=user_prompt, width=width)
                
    except Exception as e:
        st.error(f"Error generating image: {e}")
