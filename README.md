# AI Summer Internship | Mirai School of Technology

This repository contains the practical work completed during an eight-week AI
Summer Internship at Mirai School of Technology. The projects progress from
basic Streamlit interactions to AI-powered chat, image, voice, data-analysis,
and multimodal applications.

## Contents

- [Capstone: ColdMail](#capstone-coldmail)
- [Assignments](#assignments)
- [Run any Streamlit app](#run-any-streamlit-app)
- [Deploy on Streamlit Community Cloud](#deploy-on-streamlit-community-cloud)
- [Repository structure](#repository-structure)

## Capstone: ColdMail

**ColdMail** is the final project: a tailored AI cold-outreach email
generator. It combines structured form input with Gemini text generation and
can use Gemini Vision to extract a company, role, and keywords from a job
description screenshot.

### Highlights

- Generates personalized outreach emails with selectable tones.
- Extracts job details from uploaded screenshots.
- Tracks generated emails in a session-based dashboard.
- Provides KPI cards, an editable history table, company charts, CSV export,
	and downloadable emails.
- Creates shareable, pre-filled links with Streamlit query parameters.

**Live demo:** [Open ColdMail on Streamlit Community Cloud](https://ai-summer-internship-mirai-school-of-technology-uvcvmy8rh4ku8c.streamlit.app/)

The capstone is documented in [capstone-project/Readme.md](capstone-project/Readme.md)
and [capstone-project/Design.md](capstone-project/Design.md).

## Assignments

| Assignment | Project | What it demonstrates | Main dependencies |
| --- | --- | --- | --- |
| [1](ASSIGNMENT%201/app.py) | Echo Chamber 9000 | Streamlit inputs, validation, formatted output, and an approximate token estimator | Streamlit |
| [2](ASSIGNMENT%202/app.py) | The Bollywood Saga | Persona-based conversational UI and Groq chat completions | Streamlit, Groq, python-dotenv |
| [3](ASSIGNMENT%203/app.py) | The Bollywood Saga | A refined version of the persona chatbot with persistent session history | Streamlit, Groq, python-dotenv |
| [4](ASSIGNMENT%204/app.py) | AI Image Studio | Prompt-based image generation, styles, dimensions, enhancement, and PNG download | Streamlit, Requests |
| [5](ASSIGNMENT%205/app.py) | AI Visual Novel | Branching scenes using Gemini, generated artwork, and gTTS voiceover | Streamlit, Gemini, Requests, gTTS |
| [6](ASSIGNMENT%206/README.md) | Developer Profile | Profile presentation and live GitHub statistics | Markdown |
| [7](ASSIGNMENT%207/app.py) | Life-OS Dashboard | Screen-time analytics, goals, charts, and AI wellbeing coaching | Streamlit, Pandas, Gemini |

Assignment 4 uses Pollinations AI for image generation. Assignments 5 and 7
use Gemini and Pollinations AI, and may require internet access while running.

## Run any Streamlit app

### 1. Clone the repository

```bash
git clone https://github.com/Parikshit-Patidar/AI-Summer-Internship-Mirai-School-Of-Technology.git
cd AI-Summer-Internship-Mirai-School-Of-Technology
```

### 2. Create and activate a virtual environment

Python 3.11 is recommended, especially for the capstone.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install the app's dependencies

Run the command from the repository root. Assignments without a
`requirements.txt` file use the package list shown below.

```bash
# Assignment 1
python -m pip install streamlit

# Assignments 2 and 3
python -m pip install streamlit python-dotenv groq

# Assignment 4
python -m pip install -r "ASSIGNMENT 4/requirements.txt"

# Assignment 5
python -m pip install streamlit google-generativeai requests gTTS

# Assignment 7
python -m pip install -r "ASSIGNMENT 7/requirements.txt"

# Capstone
python -m pip install -r capstone-project/requirements.txt
```

### 4. Start the selected app

Streamlit must be given the path to the selected `app.py`:

```bash
streamlit run "ASSIGNMENT 1/app.py"
streamlit run "ASSIGNMENT 2/app.py"
streamlit run "ASSIGNMENT 3/app.py"
streamlit run "ASSIGNMENT 4/app.py"
streamlit run "ASSIGNMENT 5/app.py"
streamlit run "ASSIGNMENT 7/app.py"
streamlit run capstone-project/app.py
```

After starting, open the local URL printed by Streamlit, normally
`http://localhost:8501`.

### API keys and secrets

Never commit API keys to Git. Configure only the key required by the selected
project:

- Assignments 2 and 3: set `GROQ_API_KEY` in a local `.env` file or shell
	environment.
- Assignment 5: enter the Gemini API key in the app sidebar.
- Assignment 7: set `GEMINI_API_KEY` in the shell environment.
- Capstone: enter a Gemini key in the sidebar, or create
	`capstone-project/.streamlit/secrets.toml` with:

	```toml
	GEMINI_API_KEY = "your-gemini-api-key"
	```

The capstone uses the `google-genai` SDK and Python 3.11. Assignment 7 uses
the pinned dependencies in its `requirements.txt`.

## Deploy on Streamlit Community Cloud

The capstone is already deployed, but any Streamlit app can be deployed with
the following process:

1. Push the repository to GitHub.
2. Open [share.streamlit.io](https://share.streamlit.io/) and select the
	 repository and branch.
3. Set the app file path, for example `capstone-project/app.py`.
4. Add the required API keys under **Advanced settings > Secrets**, using the
	 same names described above.
5. Deploy the app.

For apps with a folder-specific `requirements.txt`, Streamlit Community Cloud
should be configured with that app directory as the working directory when
available. The capstone includes [runtime.txt](capstone-project/runtime.txt)
with Python `3.11` and [requirements.txt](capstone-project/requirements.txt)
for reproducible deployment.

## Repository structure

```text
.
├── ASSIGNMENT 1/app.py       # Streamlit fundamentals
├── ASSIGNMENT 2/app.py       # Groq persona chatbot
├── ASSIGNMENT 3/app.py       # Refined Groq persona chatbot
├── ASSIGNMENT 4/app.py       # AI image generation studio
├── ASSIGNMENT 5/app.py       # AI visual novel
├── ASSIGNMENT 6/README.md    # Developer profile and GitHub statistics
├── ASSIGNMENT 7/app.py       # Screen-time wellbeing dashboard
└── capstone-project/         # ColdMail final project
		├── app.py
		├── Design.md
		├── Readme.md
		├── requirements.txt
		└── runtime.txt
```

## Learning areas

The internship work covers artificial intelligence, machine learning, data
science, natural language processing, computer vision, generative AI,
multimodal APIs, and interactive application development with Streamlit.


