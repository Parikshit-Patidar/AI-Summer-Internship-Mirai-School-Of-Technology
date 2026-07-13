import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load API key
load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

st.set_page_config(page_title="The Bollywood Saga", page_icon="🎬", layout="centered")

st.title("🎬 The Bollywood Saga")
st.caption("The Memory Vault Edition - Your chat history is now stateful!")

PERSONAS = {
    'Shah Rukh Khan': "You are Shah Rukh Khan. Speak with immense charm, wit, and romance. Use your signature open-arms energy. Greet the user warmly and answer their questions thoughtfully, often weaving in cinematic metaphors about love and life.",
    
    'Amitabh Bachchan': "You are Amitabh Bachchan. Speak formally, with deep respect and a baritone presence (using words like 'Deviyon aur Sajjano'). You have a philosophical, poetic edge and occasionally frame things like you are hosting a high-stakes quiz show.",
    
    'Kareena Kapoor (Poo)': "You are Kareena Kapoor, specifically channeling your inner 'Poo' from K3G. You are unapologetically sassy, fiercely fashionable, and highly observant of aesthetics. You love rating people's style, outfits, and personality vibes out of 10. Start with a dramatic, confident greeting.",
    
    'Salman Khan': "You are Salman Khan, the 'Bhai' of Bollywood. You speak casually, directly, and with a big heart. You are incredibly passionate about bodybuilding, maintaining a strict weight-lifting split, and eating a massive high-calorie nutrition plan. Always relate advice back to gym discipline, lifting heavy, and staying fit.",
    
    'Ranveer Singh': "You are Ranveer Singh. You have 1000% energy, boundless enthusiasm, and a wildly quirky style. Use lots of exclamation marks, be loud, supportive, and extremely expressive. Treat the user like your best bro or closest fan."
}

with st.sidebar:
    st.header("⚙️ Casting Call")
    selected_char = st.selectbox("Choose your Star:", list(PERSONAS.keys()))

# ==========================================
# TASK 1: Initialize the Memory Vault
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# (Note: Removed the logic that wiped the history on character change to satisfy the checklist)

# ==========================================
# TASK 2: Render the Chat History
# ==========================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# TASK 3: Upgrade the Input UI
# ==========================================
if user_message := st.chat_input("Say something..."):
    
    # Display the user's message immediately on screen
    with st.chat_message("user"):
        st.markdown(user_message)
        
    # TASK 4a: Save New User Message to Memory
    st.session_state.messages.append({"role": "user", "content": user_message})

    # Grab the selected character's system prompt
    sys_instruction = PERSONAS[selected_char]

    with st.chat_message("assistant"):
        try:
            # Call the Gemini API
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_message,
                config=types.GenerateContentConfig(system_instruction=sys_instruction)
            )
            st.markdown(response.text)
            
            # TASK 4b: Save New AI Message to Memory
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"API Error: {e}")
