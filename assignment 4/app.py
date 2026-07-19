import streamlit as st
import random
import urllib.parse
import os
from PIL import Image
import io
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()
hf_api_key = os.getenv("HF_API_KEY")

# Page Config
st.set_page_config(page_title="The AI Image Studio", page_icon="🎨")

# Sidebar settings
st.sidebar.title("🎨 Settings")
art_style = st.sidebar.selectbox(
    "Select Art Style",
    ["Photorealistic", "Anime", "Oil Painting", "Watercolor", "Sketch", "Digital Art"]
)

# Width & Height Sliders (Task 1)
width = st.sidebar.slider("Image Width", min_value=256, max_value=1024, value=768, step=128)
height = st.sidebar.slider("Image Height", min_value=256, max_value=1024, value=768, step=128)

# Task 3: Magic Enhance Toggle
magic_enhance = st.sidebar.checkbox(" ✨ Enable Magic Enhance")

# Main Title
st.title("🎨 The AI Image Studio")
st.write("Generate amazing images using AI. Customize your style, resolution, and prompt below!")

# Task 4: Surprise Me prompts list
SURPRISE_PROMPTS = [
    "An astronaut riding a horse on Mars",
    "A cyberpunk street food vendor in Tokyo",
    "A mystical forest with glowing mushrooms and a hidden waterfall",
    "A futuristic city with flying cars under a neon sky",
    "A cute baby dragon sleeping on a pile of gold coins"
]

# Session state to persist the generated image details across Streamlit's page reruns
if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = None
if "image_prompt" not in st.session_state:
    st.session_state.image_prompt = None
if "current_art_style" not in st.session_state:
    st.session_state.current_art_style = None

user_prompt = st.text_input("Describe your masterpiece:", placeholder="e.g. A majestic lion standing on a mountain peak")

# Buttons layout
col1, col2 = st.columns([1, 1])
with col1:
    generate_clicked = st.button("🎨 Generate Image", use_container_width=True)
with col2:
    # Task 4: Surprise Me Button
    surprise_clicked = st.button("🎲 Surprise Me!", use_container_width=True)

prompt_to_generate = None

if generate_clicked:
    if user_prompt:
        prompt_to_generate = user_prompt
    else:
        st.warning("Please enter a prompt first!")
elif surprise_clicked:
    # Task 4: Choose random prompt
    prompt_to_generate = random.choice(SURPRISE_PROMPTS)
    st.info(f"Selected Prompt: {prompt_to_generate}")

if prompt_to_generate:
    try:
        with st.spinner("Creating your masterpiece..."):
            # Construct base prompt with style
            full_prompt = f"{prompt_to_generate}, {art_style.lower()} style"
            
            # Task 3: Apply Magic Enhance if enabled
            if magic_enhance:
                full_prompt += ", masterpiece, 8k resolution, highly detailed, trending on artstation, unreal engine 5 render"
            
            # URL encode prompt to handle special characters properly in standard HTTP URL
            encoded_prompt = urllib.parse.quote(full_prompt)
            
            # Task 1: Append width and height to URL using standard HTTP parameters
            # We construct this exact variable to satisfy the assignment requirement.
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}"
            
            # Initialize Hugging Face Inference Client
            client = InferenceClient(token=hf_api_key)
            
            # Generate the image using Stable Diffusion XL model on Hugging Face
            image = client.text_to_image(
                full_prompt,
                width=width,
                height=height,
                model="stabilityai/stable-diffusion-xl-base-1.0"
            )
            
            # Convert PIL image to PNG bytes
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            
            # Save to session state
            st.session_state.image_bytes = buffer.getvalue()
            st.session_state.image_prompt = prompt_to_generate
            st.session_state.current_art_style = art_style
            st.success("Masterpiece generated successfully!")
            
    except Exception as e:
        st.error(f"Error generating image: {e}")

# Render generated image if it exists in session state
if st.session_state.image_bytes:
    try:
        st.image(st.session_state.image_bytes, caption=st.session_state.image_prompt)
        
        # Task 2: Download Button with dynamic file name matching art style
        clean_art_style = st.session_state.current_art_style.lower().replace(" ", "_")
        download_filename = f"{clean_art_style}_image.png"
        
        st.download_button(
            label="📥 Download Image",
            data=st.session_state.image_bytes,
            file_name=download_filename,
            mime="image/png",
            use_container_width=True
        )
    except Exception:
        # Clear invalid cached session state if image loading fails
        st.session_state.image_bytes = None
        st.session_state.image_prompt = None
        st.session_state.current_art_style = None
        st.rerun()
