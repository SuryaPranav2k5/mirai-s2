import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import io
from PIL import Image

# Load API Key
load_dotenv()

# Page config
st.set_page_config(page_title="The AI Image Studio", page_icon="🎨")

# Sidebar - Generation Settings
st.sidebar.title("Generation Settings")

# Art Style selectbox
art_style = st.sidebar.selectbox(
    "Select Art Style",
    [
        "Photorealistic",
        "Anime",
        "Oil Painting",
        "Watercolor",
        "Sketch",
        "Digital Art",
        "Cyberpunk",
        "Fantasy",
        "3D Render"
    ]
)

# Dimensions sliders
width = st.sidebar.slider("Image Width", min_value=256, max_value=1024, value=768, step=128)
height = st.sidebar.slider("Image Height", min_value=256, max_value=1024, value=768, step=128)

# Optional API Key Input in Sidebar
user_api_key = st.sidebar.text_input("API Key (Optional)", type="password", help="Leave empty to use default GEMINI_API_KEY from environment variables.")

# Determine which API Key to use
api_key = user_api_key if user_api_key else os.getenv("GEMINI_API_KEY")

# Main Content
st.title("The AI Image Studio")

# Input prompt
user_prompt = st.text_input("Describe your masterpiece:")

# Map selected dimensions to standard Imagen 3 aspect ratios
def get_aspect_ratio(w, h):
    ratio = w / h
    standards = [0.5625, 0.75, 1.0, 1.3333, 1.7777]
    ratios = ["9:16", "3:4", "1:1", "4:3", "16:9"]
    closest_idx = min(range(len(standards)), key=lambda i: abs(standards[i] - ratio))
    return ratios[closest_idx]

# Trigger image generation
if user_prompt:
    if not api_key:
        st.error("Please enter a Gemini API Key in the sidebar or set it in your .env file to generate images.")
    else:
        try:
            with st.spinner("Generating your masterpiece..."):
                client = genai.Client(api_key=api_key)
                
                # Incorporate art style into prompt
                final_prompt = f"{user_prompt}, {art_style.lower()} style"
                aspect_ratio = get_aspect_ratio(width, height)
                
                # Call Google GenAI SDK Imagen 3
                result = client.models.generate_images(
                    model='imagen-3.0-generate-002',
                    prompt=final_prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        aspect_ratio=aspect_ratio,
                        output_mime_type="image/jpeg",
                    )
                )
                
                # Render the generated image
                if result.generated_images:
                    for gen_img in result.generated_images:
                        image = Image.open(io.BytesIO(gen_img.image_bytes))
                        st.image(image, caption=f"Generated masterpiece: {user_prompt}", use_container_width=True)
                else:
                    st.warning("No images were generated. Please try a different prompt.")
        except Exception as e:
            st.error(f"Error generating image: {e}")
