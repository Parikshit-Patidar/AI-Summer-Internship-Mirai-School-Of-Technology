import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# grab env vars from our .env file
load_dotenv(override=True)
api_key = os.getenv("GROQ_API_KEY")

# TODO: Add fallback error UI if the Groq key is completely missing in deployment
client = Groq(api_key=api_key)

# Basic page layout configs
st.set_page_config(page_title="The Bollywood Saga", page_icon="🎬", layout="centered")

st.title("🎬 The Bollywood Saga")
st.caption("Blazing fast chats with your favorite Bollywood icons powered by Groq.")

# System prompts mapped out for our 5 stars
PERSONAS = {
    'Shah Rukh Khan': "You are Shah Rukh Khan. Speak with immense charm, wit, and romance. Use your signature open-arms energy. Greet the user warmly and answer their questions thoughtfully, often weaving in cinematic metaphors about love and life.",
    
    'Amitabh Bachchan': "You are Amitabh Bachchan. Speak formally, with deep respect and a baritone presence (using words like 'Deviyon aur Sajjano'). You have a philosophical, poetic edge and occasionally frame things like you are hosting a high-stakes quiz show.",
    
    'Kareena Kapoor (Poo)': "You are Kareena Kapoor, specifically channeling your inner 'Poo' from K3G. You are unapologetically sassy, fiercely fashionable, and highly observant of aesthetics. You love rating people's style, outfits, and personality vibes out of 10. Start with a dramatic, confident greeting.",
    
    'Salman Khan': "You are Salman Khan, the 'Bhai' of Bollywood. You speak casually, directly, and with a big heart. You are incredibly passionate about bodybuilding, maintaining a strict weight-lifting split, and eating a massive high-calorie nutrition plan. Always relate advice back to gym discipline, lifting heavy, and staying fit.",
    
    'Ranveer Singh': "You are Ranveer Singh. You have 1000% energy, boundless enthusiasm, and a wildly quirky style. Use lots of exclamation marks, be loud, supportive, and extremely expressive. Treat the user like your best bro or closest fan."
}

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Casting Call")
    selected_char = st.selectbox("Choose your Star:", list(PERSONAS.keys()))
    
    st.divider()
    
    if st.button("Clear Conversation"):
        st.session_state.messages = []

# Persistent chat history implementation via Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_persona" not in st.session_state:
    st.session_state.current_persona = selected_char

# Auto-wipe chat window if they select a different actor from the dropdown
if st.session_state.current_persona != selected_char:
    st.session_state.messages = []
    st.session_state.current_persona = selected_char

# Render the historical conversation block
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Bottom text input bar
user_input = st.chat_input(f"Say hello to {selected_char}...")

if user_input:
    # Immediately display what the user wrote and store it
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Grab the current actor prompt configuration
    sys_instruction = PERSONAS[selected_char]

    # Execute request to the Groq API endpoint
    with st.chat_message("assistant"):
        try:
            # Using llama-3.3-70b-versatile which handles personas remarkably well
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": sys_instruction},
                    {"role": "user", "content": user_input}
                ]
            )
            
            # Extract content from Groq's payload schema
            ai_response = res.choices[0].message.content
            st.markdown(ai_response)
            
            # Save historical output
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            st.error(f"Something went sideways with the Groq API: {e}")
