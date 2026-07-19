# The AI Image Studio 🎨 (Assignment 4)

An upgraded AI Image Studio application built using **Streamlit** and powered by **Hugging Face's Stable Diffusion XL (SDXL)** model. It includes advanced custom features such as resolution selectors, dynamic downloading, magic prompts, and surprise idea generation.

---

## 🚀 Implemented Features

### 🛠️ Task 1: Custom Dimensions (Width & Height)
* Added sliders to the sidebar allowing the user to select widths and heights between `256px` and `1024px` (in steps of `128px`).
* Appended width and height parameters directly as URL parameters in the constructed API endpoint URL (matching `?width=...&height=...`).

### 💾 Task 2: Dynamic Downloading
* Updated the `st.download_button` so that generated images are saved with a clean, dynamic filename matching the selected art style (e.g., `photorealistic_image.png`, `anime_image.png`, `sketch_image.png`).
* Automatically configured download files to use the `.png` format.

### 🪄 Task 3: Magic Enhance Toggle
* Created a sidebar checkbox for `✨ Enable Magic Enhance`.
* When enabled, the application secretly appends powerful quality-booster words to the prompt (e.g. `masterpiece`, `8k resolution`, `highly detailed`, `unreal engine 5 render`) to enhance output beauty.

### 🎲 Task 4: Surprise Me! Feature
* Added a `🎲 Surprise Me!` button alongside the main generation button.
* Clicking this button randomly picks a creative prompt from a curated list of 5 ideas, displays the selection to the user via a UI notice, and immediately generates the image.

### 🔒 Reliability & Fallback Implementation
* Built a fallback system using the **Hugging Face Inference API** running **Stable Diffusion XL (SDXL)**, resolving the `500 Internal Server Error` and `402 Payment Required` issues that occur on keyless Pollinations AI servers when using custom dimensions.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
Make sure you have python installed (version `3.10` or newer is recommended).

### 2. Configure API Key
Create a `.env` file in the project's root directory and add your Hugging Face Access Token:
```env
HF_API_KEY=your_hugging_face_token_here
```
*(You can generate a free token in 30 seconds at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens))*

### 3. Install Dependencies
Run the following command to install the required libraries:
```bash
pip install streamlit pillow python-dotenv requests huggingface_hub
```

### 4. Run the Application
Start the Streamlit development server:
```bash
streamlit run "assignment 4/app.py"
```

Once running, the application will automatically launch in your browser at `http://localhost:8501`.

Recording link - https://drive.google.com/file/d/1X4bxfEkfIPmrXKyziOWAH8au-dGJqF1Z/view?usp=sharing