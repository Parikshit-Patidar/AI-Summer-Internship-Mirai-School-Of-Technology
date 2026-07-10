import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# grab env vars 
load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")

# TODO: add proper error handling here later if API key is missing
client = genai.Client(api_key=api_key)

st.set_page_config(page_title="The Bollywood Saga", page_icon="🎬", layout="centered")

st.title("🎬 The Bollywood Saga")
st.caption("Chat with your favorite Bollywood icons.")

# system prompts for the different stars
# kept it to 5 as requested
PROMPTS = {
    'Shah Rukh Khan': "You are Shah Rukh Khan. Speak with immense charm, wit, and romance. Use your signature open-arms energy. Greet the user warmly and answer their questions thoughtfully, often weaving in cinematic metaphors about love and life.",
    
    'Amitabh Bachchan': "You are Amitabh Bachchan. Speak formally, with deep respect and a baritone presence (using words like 'Deviyon aur Sajjano'). You have a philosophical, poetic edge and occasionally frame things like you are hosting a high-stakes quiz show.",
    
    'Kareena Kapoor (Poo)': "You are Kareena Kapoor, specifically channeling your inner 'Poo' from K3G. You are unapologetically sassy, fiercely fashionable, and highly observant of aesthetics. You love rating people's style, outfits, and personality vibes out of 10. Start with a dramatic, confident greeting.",
    
    'Salman Khan': "You are Salman Khan, the 'Bhai' of Bollywood. You speak casually, directly, and with a big heart. You are incredibly passionate about bodybuilding, maintaining a strict weight-lifting split, and eating a massive high-calorie nutrition plan. Always relate advice back to gym discipline, lifting heavy, and staying fit.",
    
    'Ranveer Singh': "You are Ranveer Singh. You have 1000% energy, boundless enthusiasm, and a wildly quirky style. Use lots of exclamation marks, be loud, supportive, and extremely expressive. Treat the user like your best bro or closest fan."
}

# Sidebar stuff
with st.sidebar:
    st.header("⚙️ Casting Call")
    # list(PROMPTS.keys()) just grabs the names for the dropdown
    selected_char = st.selectbox("Choose your Star:", list(PROMPTS.keys()))
    
    st.divider()
    
    if st.button("Clear Chat"):
        st.session_state.messages = []

# setup session state so the chat doesn't wipe on every refresh
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# track the current star so we know if the user changes it in the dropdown
if "current_persona" not in st.session_state:
    st.session_state.current_persona = selected_char

# reset chat if they switch characters mid-conversation
if st.session_state.current_persona != selected_char:
    # print(f"Switching from {st.session_state.current_persona} to {selected_char}") # debug
    st.session_state.messages = []
    st.session_state.current_persona = selected_char

# render the chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# main chat input
user_input = st.chat_input(f"Say hello to {selected_char}...")

if user_input:
    # show user message on screen & save to state
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # grab the right persona prompt
    sys_instruction = PROMPTS[selected_char]

    # hit the gemini API
    # TODO: refactor this if we actually win the hackathon, otherwise it stays as is lol
    with st.chat_message("assistant"):
        try:
            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_input,
                config=types.GenerateContentConfig(system_instruction=sys_instruction)
            )
            st.markdown(res.text)
            
            # save AI response to history
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            
        except Exception as e:
            st.error(f"Oof, something broke: {e}")