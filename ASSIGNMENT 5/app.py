import streamlit as st
from google import genai
from google.genai import types
import json
import requests
import urllib.parse
from gtts import gTTS
import time
import hashlib
from io import BytesIO
from google.genai.errors import ServerError

# --- UI Setup & Config ---
st.set_page_config(page_title="AI Visual Novel Engine", layout="wide")

st.sidebar.title("🎬 Story Settings")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
genre = st.sidebar.selectbox("Story Genre", ["Cyberpunk", "Dark Fantasy", "Sci-Fi", "Mystery"])
art_style = st.sidebar.selectbox("Art Style", ["Anime", "Cinematic", "Watercolor", "Pixel Art"])

# --- State Management ---
if "chat" not in st.session_state:
    st.session_state.chat = None
if "current_scene" not in st.session_state:
    st.session_state.current_scene = None
if "chat_config" not in st.session_state:
    st.session_state.chat_config = None

# --- Core Logic ---
def generate_next_scene(user_choice):
    """Sends user choice to Gemini, parses the JSON, and fetches media."""
    try:
        with st.spinner("The AI Director is writing the next scene..."):
            # 1. Get AI Response
            for attempt in range(3):
                try:
                    response = st.session_state.chat.send_message(user_choice)
                    break
                except ServerError as e:
                    if e.code != 503 or attempt == 2:
                        raise
                    time.sleep(2 ** attempt)
            if not response.text:
                raise ValueError("Gemini returned an empty response.")
            raw_text = response.text.strip()
            
            # Clean text in case of markdown blocks
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()
                
            # 2. Parse JSON
            scene_data = json.loads(raw_text)
            story_text = scene_data.get("story_text")
            base_prompt = scene_data.get("image_prompt")
            options = scene_data.get("options")
            if not isinstance(story_text, str) or not story_text.strip():
                raise ValueError("Gemini's response is missing story text.")
            if not isinstance(base_prompt, str):
                raise ValueError("Gemini's response has an invalid image prompt.")
            if not isinstance(options, list) or not options or not all(
                isinstance(option, str) and option.strip() for option in options
            ):
                raise ValueError("Gemini's response has invalid story choices.")
            
            image_prompt = f"{base_prompt}, {art_style} style, masterpiece"
            
            # 3. Fetch image bytes so the image server is not requested twice.
            image = None
            try:
                encoded_prompt = urllib.parse.quote(image_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                res = requests.get(image_url, timeout=20)
                res.raise_for_status()
                if res.headers.get("Content-Type", "").startswith("image/"):
                    image = res.content
                else:
                    st.toast("Image service returned an invalid response.", icon="⚠️")
            except requests.RequestException as e:
                st.toast(f"Image generation failed: {e}", icon="⚠️")

            # 4. Generate audio in memory to avoid shared-file collisions.
            audio = None
            try:
                tts = gTTS(text=story_text, lang='en', slow=False)
                audio_buffer = BytesIO()
                tts.write_to_fp(audio_buffer)
                audio = audio_buffer.getvalue()
            except Exception as e:
                st.toast(f"Voiceover generation failed: {e}", icon="⚠️")

            # 5. Update Session State
            st.session_state.current_scene = {
                "text": story_text,
                "image": image,
                "audio": audio,
                "options": options
            }
            return True # Flag that the generation was successful

    except Exception as e:
        # The error will now stay on screen because we return False instead of rerunning
        st.error(f"Error generating scene: {e}")
        return False

# --- Render App ---
if not api_key:
    st.info("👈 Enter your Gemini API Key in the sidebar to begin.")
else:
    # Recreate the chat if the API key or story genre changes.
    chat_config = (hashlib.sha256(api_key.encode()).hexdigest(), genre)
    if st.session_state.chat_config != chat_config:
        st.session_state.chat = None
        st.session_state.current_scene = None

    # 1. Initialize the chat session using Native JSON Mode
    if st.session_state.chat is None:
        system_instruction = f"""
        You are a visual novel engine running a {genre} story. 
        Return valid JSON only, with exactly these fields:
        {{
            "story_text": "The narrative paragraph.",
            "image_prompt": "A detailed image prompt that does not contain text.",
            "options": ["Choice 1", "Choice 2", "Choice 3"]
        }}
        """
        try:
            client = genai.Client(api_key=api_key)
            chat = client.chats.create(
                model="gemini-3.8-flash",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                ),
            )
            st.session_state.chat = chat
            st.session_state.chat_config = chat_config
        except Exception as e:
            st.error(f"Could not connect to Gemini: {e}")
        
    # 2. Display Start Button if no scene exists
    if st.session_state.chat is not None and st.session_state.current_scene is None:
        if st.button("🚀 Start Adventure"):
            # Only rerun if the scene generation was successful
            success = generate_next_scene("Begin the story.")
            if success:
                st.rerun()

    # 3. Display the current scene
    else:
        scene = st.session_state.current_scene
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if scene["image"]:
                st.image(scene["image"], use_container_width=True)
            
            st.markdown(f"### {scene['text']}")
            
            if scene["audio"]:
                st.audio(scene["audio"], format="audio/mp3")
                
        with col2:
            st.markdown("### Choose your path:")
            
            for idx, choice in enumerate(scene["options"]):
                if st.button(choice, key=f"btn_{idx}", use_container_width=True):
                    # Only rerun if the scene generation was successful
                    success = generate_next_scene(f"I choose to: {choice}")
                    if success:
                        st.rerun()