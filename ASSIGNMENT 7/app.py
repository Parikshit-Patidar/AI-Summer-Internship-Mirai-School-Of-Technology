import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime, timedelta
from google import genai
import urllib.parse

# -----------------------------------------
# PHASE 1: THE DATA PIPELINE
# -----------------------------------------
def generate_synthetic_data():
    """Generates 14 days of realistic screen time data if the CSV doesn't exist."""
    if not os.path.exists("screentime.csv"):
        apps = {
            "TikTok": "Social Media", "Instagram": "Social Media", 
            "VS Code": "Coding", "GitHub": "Coding",
            "YouTube": "Entertainment", "Netflix": "Entertainment",
            "Duolingo": "Education", "Kindle": "Education"
        }
        
        data = []
        base_date = datetime.now() - timedelta(days=14)
        
        for i in range(14):
            current_date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
            for app, category in apps.items():
                # Randomize minutes to make the data look realistic
                minutes = random.randint(0, 120) if category != "Coding" else random.randint(30, 240)
                if minutes > 0:
                    data.append([current_date, app, category, minutes])
                    
        df = pd.DataFrame(data, columns=["Date", "App_Name", "Category", "Minutes_Used"])
        df.to_csv("screentime.csv", index=False)

generate_synthetic_data()

@st.cache_data
def load_data():
    return pd.read_csv("screentime.csv")

df = load_data()

# -----------------------------------------
# PHASE 2: THE COMMAND CENTER UI
# -----------------------------------------
st.set_page_config(page_title="Life-OS Dashboard", page_icon="⚡", layout="wide")
st.title("⚡ Life-OS: Wellbeing & Productivity Dashboard")

# Sidebar Controls
st.sidebar.header("Command Center")
dates = sorted(df['Date'].unique(), reverse=True)
selected_date = st.sidebar.selectbox("Filter by Day", dates)
daily_goal = st.sidebar.slider("Daily Screen Time Goal (Minutes)", min_value=60, max_value=600, value=240, step=30)

# Filter Data
day_data = df[df['Date'] == selected_date]
total_mins = day_data['Minutes_Used'].sum()

if not day_data.empty:
    most_used_app = day_data.loc[day_data['Minutes_Used'].idxmax()]['App_Name']
else:
    most_used_app = "None"

# KPI Row
st.subheader("Daily High-Level Stats")
col1, col2, col3 = st.columns(3)

# If total_mins > daily_goal, delta is negative (bad). Streamlit handles delta_color normally (green for positive, red for negative).
# We want remaining minutes.
remaining = daily_goal - total_mins
col1.metric("Total Screen Time", f"{total_mins} mins", delta=f"{int(remaining)} mins remaining", delta_color="normal")
col2.metric("Most Used App", most_used_app)
col3.metric("Daily Goal", f"{daily_goal} mins")

st.divider()

# Visualizations
st.subheader("14-Day Trend")
trend_data = df.groupby('Date')['Minutes_Used'].sum().reset_index()
st.bar_chart(trend_data.set_index('Date'))

# -----------------------------------------
# PHASE 3: THE AI INTEGRATION
# -----------------------------------------
st.subheader("🤖 AI Life Coach Analysis")

api_key = os.environ.get("GEMINI_API_KEY")

if api_key:
    # Data Bridge: Aggregate and convert to string
    summary_df = day_data.groupby('Category')['Minutes_Used'].sum().reset_index()
    data_str = summary_df.to_string(index=False)
    
    # System Prompt Construction
    prompt = f"""
    You are a brutal-but-fair productivity and lifestyle coach.
    Here is my screen time summary for today by category:
    
    {data_str}
    
    My daily goal is {daily_goal} minutes, and I spent a total of {total_mins} minutes today.
    Analyze my categories. DO NOT just say "use your phone less." 
    Instead, look at where I spent the most time and suggest specific physical, real-world replacements. 
    For example, if I overused Entertainment, suggest an active alternative.
    Be direct, hold me accountable, but keep it constructive. Keep your response under 100 words.
    """
    
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        # Render Output conditionally based on goal achievement
        if total_mins > daily_goal:
            st.warning(response.text)
        else:
            st.success(response.text)
            
    except Exception as e:
        st.error(f"Failed to connect to Gemini API: {e}")
else:
    st.info("⚠️ Please set your GEMINI_API_KEY in your environment variables to unlock AI coaching.")

# -----------------------------------------
# PHASE 4: THE INNOVATION DELIVERABLE
# -----------------------------------------
st.subheader("🎭 The Guilt-Trip Avatar")
st.write("A dynamic reflection of your daily habits.")

# Determine the visual prompt based on user performance
if total_mins > daily_goal:
    image_prompt = "A lazy zombie slouched on a couch in a dark room, staring mindlessly at a glowing smartphone, cinematic lighting, highly detailed digital art"
    caption = "Missed the goal: Zombie Mode"
else:
    image_prompt = "A focused cyber-warrior meditating on a sunlit mountaintop, vibrant colors, highly detailed digital art"
    caption = "Crushed the goal: Warrior Mode"

# Call Pollinations Image Generation API (No auth required)
encoded_prompt = urllib.parse.quote(image_prompt)
image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=400&nologo=true"

st.image(image_url, caption=caption, use_container_width=True)