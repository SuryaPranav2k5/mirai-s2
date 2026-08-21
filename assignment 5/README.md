# FableForge AI: Multi-Modal Visual Novel Engine 🎭 (Assignment 5)

An immersive "Choose Your Own Adventure" Visual Novel Engine built with **Streamlit** and powered by **Google Gemini 2.5 Flash** (Stateful text generation) and **Pollinations AI** (Visual asset generation).

This project demonstrates advanced orchestration of generative text, image generation, text-to-speech (TTS) audio synthesis, and dynamic UI elements in a stateful Streamlit environment.

---

## 🚀 Advanced Features & Engineering Concepts

### 1. Structured JSON Engine & Safe Parsing 🧠
* **Gemini Structured Output:** Configured the Gemini client using `response_mime_type="application/json"` to ensure response consistency.
* **System Prompt Constraints:** Instructed Gemini to return responses adhering strictly to a JSON schema containing exactly three keys: `story_text`, `image_prompt`, and `options`.
* **JSON Parser Fallback:** Researched and integrated Python's built-in `json` library (`json.loads()`). Built a resilient fallback mechanism that cleans markdown code blocks, validates key presence, and falls back to pre-defined stories and choices if the parser encounters malformed strings, guaranteeing a crash-free experience.

### 2. Dynamic UI & Choice Generation 🎛️
* **Interactive Story Branches:** Bypassed the traditional `st.chat_input()` to build an authentic visual novel choice screen.
* **Dynamic Button Loops:** Leveraged Python `for` loops to iterate over the AI-generated `options` list and construct native `st.button()` elements on-the-fly.
* **Stateful Callbacks:** Developed a state mechanism where clicking a button triggers a callback to send the choice as a message to the Gemini chat session, fetch new visual and audio assets, update the session state, and invoke `st.rerun()` to refresh the dashboard instantly.

### 3. Speech Synthesis & Audio Integration 🔊
* **gTTS Integration:** Researched the `gTTS` (Google Text-to-Speech) library to synthesize high-quality audio files from the story segment's `story_text`.
* **TLD Accent Settings:** Added a dropdown allowing users to change narration accents (US, UK, Indian, Australian, Canadian) by dynamically swapping gTTS's Top-Level Domain (TLD) parameter.
* **BytesIO Memory Buffer:** Instead of saving audio files to local disks—which causes permission locks and I/O overhead on Windows—audio is streamed directly in-memory using `io.BytesIO`. The bytes are fed directly into Streamlit's `st.audio()` player.

### 4. Robust Connection States & Graceful Failures 🛡️
* **API Resiliency:** Wrapped all HTTP queries to the Pollinations API and gTTS audio generator in `try...except` blocks.
* **Toast Notifications:** If the Pollinations server is busy or gTTS times out, the app flashes a neat warning toast (e.g. `st.toast("Image server is busy, skipping visual...")`) and continues the adventure with fallback UI blocks and audio placeholders without disrupting the user or triggering red Traceback error pages.

---

## 🛠️ Installation & Setup

### 1. Configure Gemini API Key
Make sure your root `.env` file contains your Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Install Dependencies
Run the command below in your terminal to install the necessary libraries:
```bash
pip install -r requirements.txt
```

### 3. Run the Application
Start the Streamlit local server:
```bash
streamlit run "assignment 5/app.py"
```

---

## 🔗 Professional LinkedIn Post Draft

```text
🚀 Exciting News! I just completed my Capstone Project for the "AI Builder" Track at MirAI School of Technology! 

I built FableForge AI, a stateful "Choose Your Own Adventure" Visual Novel Engine that blends generative text, visual assets, and synthesized speech into an immersive gaming dashboard.

To build this, I researched and implemented three critical engineering concepts:
1️⃣ Structured JSON Outputs: Forcing Gemini 2.5 Flash to return valid JSON strings and implementing robust fallback parsers.
2️⃣ Dynamic UI Generation: Dynamically generating Streamlit button controls from parsed lists of AI-generated choices to drive branching storylines.
3️⃣ Speech Synthesis: Integrating gTTS (Google Text-to-Speech) with multi-accent support and utilizing in-memory BytesIO buffers to stream audio narration without disk-write locks.
4️⃣ Graceful Failures: Building API try-except blocks to rescue visual/audio servers timeouts, keeping the UI crash-free.

Check out the gameplay and sound in the screen capture! 🎬

Huge thanks to MirAI School of Technology for the incredible support. On to the next challenge! 🌟

#GenerativeAI #Streamlit #Gemini #TextToSpeech #Python #WebDevelopment #AIBuilder
```
