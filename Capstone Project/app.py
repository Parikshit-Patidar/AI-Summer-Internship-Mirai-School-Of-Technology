# ColdMail - cold outreach email generator
# MirAI capstone project
#
# basic idea: fill a form -> gemini writes a tailored email -> keep track of what
# was generated so far in this session. added query params so i can share a
# pre-filled link instead of making people type everything from scratch.

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from google import genai
from google.genai import types

st.set_page_config(
    page_title="ColdMail // AI Outreach Engine",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# quick dark theme, mostly copied+tweaked css from an earlier project of mine
CUSTOM_CSS = """
<style>
.stApp {
    background-color: #0b0f14;
}
h1, h2, h3 {
    font-family: 'Courier New', monospace;
    letter-spacing: -0.5px;
}
.stMetric {
    background-color: #12181f;
    border: 1px solid #1f2933;
    border-radius: 8px;
    padding: 12px;
}
div[data-testid="stForm"] {
    background-color: #12181f;
    border: 1px solid #1f2933;
    border-radius: 10px;
    padding: 20px;
}
.stButton>button {
    background-color: #00d4a0;
    color: #0b0f14;
    font-weight: 600;
    border-radius: 6px;
    border: none;
}
.email-output {
    background-color: #0d1117;
    border: 1px solid #00d4a0;
    border-radius: 8px;
    padding: 20px;
    font-family: 'Courier New', monospace;
    white-space: pre-wrap;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# session state - without this streamlit wipes everything on every rerun,
# learned that the hard way while testing
if "history" not in st.session_state:
    st.session_state.history = []

if "last_email" not in st.session_state:
    st.session_state.last_email = None

if "gemini_configured" not in st.session_state:
    st.session_state.gemini_configured = False

# gets filled in if someone uploads a JD screenshot and hits extract
if "extracted_company" not in st.session_state:
    st.session_state.extracted_company = ""

if "extracted_role" not in st.session_state:
    st.session_state.extracted_role = ""

if "extracted_keywords" not in st.session_state:
    st.session_state.extracted_keywords = []

# pull prefilled values from the URL if someone shared a link
qp = st.query_params
default_company = qp.get("company", "")
default_role = qp.get("role", "")

with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    # check for a demo key in secrets first - if the app owner set one,
    # evaluators can test this without needing to generate their own key.
    # only touch st.secrets if a secrets.toml actually exists - accessing
    # st.secrets with none configured throws a "no secrets found" warning
    # even inside try/except, so guard on the file itself instead.
    # streamlit cloud writes its dashboard-configured secrets to this same
    # relative path at runtime, so this check works the same way deployed.
    demo_key = None
    if os.path.exists(os.path.join(".streamlit", "secrets.toml")):
        try:
            demo_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            demo_key = None

    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        help="Get one free at aistudio.google.com" + (" — or leave blank to use the demo key" if demo_key else ""),
    )

    active_key = api_key or demo_key

    if active_key:
        # new SDK doesn't have a global "configure" step - each call just
        # needs the client, so stash the key in session state and build
        # a Client() wherever it's actually used
        st.session_state.gemini_configured = True
        st.session_state.api_key = active_key
        st.success("Using your key" if api_key else "Using demo key")
    else:
        st.session_state.gemini_configured = False
        st.info("Paste your Gemini API key to enable generation")

    st.markdown("---")
    tone = st.select_slider(
        "Email tone",
        options=["Formal", "Professional", "Warm", "Bold & Confident"],
        value="Professional",
    )
    st.markdown("---")
    st.caption("Built with Streamlit + Gemini · MirAI Capstone")

st.title("✉️ ColdMail — AI Outreach Engine")
st.caption("Generates a tailored cold email instead of a generic template - Gemini actually reads the role/company context.")

tab_generate, tab_dashboard = st.tabs(["🚀 Generate", "📊 Dashboard"])

# system prompt for gemini. took a few tries to stop it from writing
# "I hope this email finds you well" every single time lol
SYSTEM_PROMPT = """You are an expert career coach and professional email copywriter.
You write cold outreach emails that are concise (under 150 words), specific, and human -
never generic templates. You always reference something concrete about the role or company.
Never use cliche phrases like "I hope this email finds you well" or "I am writing to express my interest".
Output ONLY the email body, no subject line, no extra commentary."""


def build_prompt(company, role, recruiter, background, tone, jd_keywords=None):
    # keeping this as its own function so its easy to tweak the prompt later
    # without touching the generation logic
    if recruiter:
        recruiter_line = f"addressed to {recruiter}"
    else:
        recruiter_line = "addressed generically (no named recruiter)"

    # if we pulled anything out of a JD screenshot, fold it in so the email
    # can reference actual requirements instead of speaking generically
    jd_line = ""
    if jd_keywords:
        jd_line = f"\nSpecific things mentioned in the job posting: {', '.join(jd_keywords)}. Reference at least one of these naturally.\n"

    prompt = f"""
Write a cold outreach email {recruiter_line}.

Target company: {company}
Target role: {role}
Tone: {tone}
Sender's background/pitch: {background}
{jd_line}
Requirements:
- Under 150 words
- One specific, concrete hook related to the company or role
- A clear, low-friction call to action (e.g. a 15-min call)
- No generic filler phrases
"""
    return prompt


MODEL_NAME = "gemini-3.6-flash"  # centralized here since google keeps renaming these


def generate_email(company, role, recruiter, background, tone, jd_keywords=None):
    client = genai.Client(api_key=st.session_state.api_key)
    prompt = build_prompt(company, role, recruiter, background, tone, jd_keywords)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
    )
    return response.text.strip()


def extract_jd_from_screenshot(image_bytes, mime_type):
    # separate model call, no system instruction needed here, just want
    # straight extraction. asking for raw json back so it's easy to use in
    # the rest of the app without more parsing than necessary
    client = genai.Client(api_key=st.session_state.api_key)
    vision_prompt = """This is a screenshot of a job posting. Extract:
- company: the company name
- role: the job title
- keywords: a list of 2-4 specific skills, tools, or requirements actually mentioned in the posting

Return ONLY raw JSON like {"company": "...", "role": "...", "keywords": ["...", "..."]}
No markdown formatting, no code fences, no extra text."""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            vision_prompt,
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
        ],
    )

    # gemini sometimes wraps json in ```json fences even when told not to,
    # so stripping those out just in case
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


with tab_generate:
    col_form, col_output = st.columns([1, 1.2])

    with col_form:
        # screenshot upload lives outside the form on purpose - form widgets
        # only update on submit, but i want the extracted company/role to
        # show up in the fields immediately after hitting extract
        with st.expander("📸 Got a screenshot of the job posting? Upload it here", expanded=False):
            jd_image = st.file_uploader("JD screenshot", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
            if jd_image is not None:
                if st.button("🔍 Extract details"):
                    if not st.session_state.gemini_configured:
                        st.error("Add your Gemini API key in the sidebar first.")
                    else:
                        with st.spinner("Reading the screenshot..."):
                            try:
                                data = extract_jd_from_screenshot(jd_image.getvalue(), jd_image.type)
                                st.session_state.extracted_company = data.get("company", "")
                                st.session_state.extracted_role = data.get("role", "")
                                st.session_state.extracted_keywords = data.get("keywords", [])
                                st.success(f"Found it: {data.get('company')} — {data.get('role')}")
                            except Exception as e:
                                st.error(f"Couldn't read that screenshot: {e}")

            if st.session_state.extracted_keywords:
                st.caption("Picked up from the posting: " + ", ".join(st.session_state.extracted_keywords))

        # extracted values win over the URL query params if both exist,
        # since they're more specific to what the user just uploaded
        company_default = st.session_state.extracted_company or default_company
        role_default = st.session_state.extracted_role or default_role

        with st.form("email_form"):
            company = st.text_input("Company name", value=company_default, placeholder="e.g. Notion")
            role = st.text_input("Target role", value=role_default, placeholder="e.g. Product Designer")
            recruiter = st.text_input("Recruiter name (optional)", placeholder="e.g. Priya Sharma")
            background = st.text_area(
                "Your background / pitch",
                placeholder="e.g. Final-year B.Tech student, built and shipped 3 React apps including a habit tracker on Play Store...",
                height=120,
            )
            submitted = st.form_submit_button("Generate Email →")

        # using a form here instead of raw widgets so the api only gets called
        # once on submit, not on every keystroke
        if submitted:
            if not st.session_state.gemini_configured:
                st.error("Add your Gemini API key in the sidebar first.")
            elif not company or not role or not background:
                st.warning("Company, role, and background are required.")
            else:
                with st.spinner("Drafting your email..."):
                    try:
                        email_text = generate_email(
                            company, role, recruiter, background, tone,
                            jd_keywords=st.session_state.extracted_keywords,
                        )
                        st.session_state.last_email = email_text
                        st.session_state.history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "company": company,
                            "role": role,
                            "recruiter": recruiter if recruiter else "—",
                            "tone": tone,
                            "status": "Draft",
                            "word_count": len(email_text.split()),
                        })
                    except Exception as e:
                        # not the cleanest error handling but good enough for now
                        st.error(f"Generation failed: {e}")

    with col_output:
        st.markdown("#### Generated Email")
        if st.session_state.last_email:
            st.markdown(f'<div class="email-output">{st.session_state.last_email}</div>', unsafe_allow_html=True)
            st.download_button(
                "⬇ Download as .txt",
                st.session_state.last_email,
                file_name=f"cold_email_{company if submitted else 'draft'}.txt",
            )
            if submitted:
                share_url = f"?company={company}&role={role}"
                st.text_input("🔗 Shareable pre-fill link (append to your app URL)", value=share_url)
        else:
            st.info("Your generated email will appear here.")

with tab_dashboard:
    if not st.session_state.history:
        st.info("Nothing generated yet — head to the Generate tab and create your first email.")
    else:
        df = pd.DataFrame(st.session_state.history)

        # top row of KPI cards, using deltas where it actually means something
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Emails generated", len(df))
        with k2:
            st.metric("Companies targeted", df["company"].nunique())
        with k3:
            st.metric("Avg word count", int(df["word_count"].mean()))
        with k4:
            replied = (df["status"] == "Replied").sum()
            st.metric("Replies", replied, delta=f"{replied}/{len(df)}" if len(df) else None)

        st.markdown("---")

        col_chart, col_table = st.columns([1, 1.4])

        with col_chart:
            st.markdown("#### Emails per company")
            company_counts = df["company"].value_counts()
            st.bar_chart(company_counts)

        with col_table:
            st.markdown("#### History (editable — update status as you hear back)")
            # data_editor so status can be updated inline instead of needing
            # a separate form for it. edits get written back to session_state
            # below so they stick between reruns
            edited_df = st.data_editor(
                df,
                column_config={
                    "status": st.column_config.SelectboxColumn(
                        "status",
                        options=["Draft", "Sent", "Replied", "No response"],
                        required=True,
                    ),
                },
                disabled=["timestamp", "company", "role", "recruiter", "tone", "word_count"],
                hide_index=True,
                use_container_width=True,
            )
            st.session_state.history = edited_df.to_dict("records")

        st.download_button(
            "⬇ Export history as CSV",
            df.to_csv(index=False),
            file_name="coldmail_history.csv",
        )