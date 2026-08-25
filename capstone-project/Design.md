# Technical Design Document — ColdMail

## 1. Problem & scope

Cold outreach emails usually fall into two bad categories: generic templates
that mention nothing specific, or a slow manual process of researching each
company individually. ColdMail's goal is to make the *tailored* version fast,
without sacrificing specificity — by giving Gemini structured context to
write from instead of a bare "write me an email" prompt.

## 2. Data flow

```
[form input] ----\
                   >--> Prompt Builder --> Gemini (text) --> email output
[JD screenshot] --/         ^
      |                     |
      v                     |
Gemini (vision) -----> extracted company/role/keywords
      |
      v
st.session_state.history <-- appended after each generation
      |
      v
Dashboard (KPIs + editable table)
```

Two independent Gemini calls exist in this app, and they're kept separate
on purpose:

1. **Vision extraction** (`extract_jd_from_screenshot`) — takes raw image
   bytes + a prompt asking for structured JSON back. No system instruction
   needed here since the task is narrow (extraction, not writing).
2. **Text generation** (`generate_email`) — takes the (possibly
   screenshot-derived) form fields, builds a prompt via `build_prompt()`,
   and calls Gemini with a system instruction that constrains tone, length,
   and forbids cliché phrasing.

Keeping these as separate functions means the vision step can fail or be
skipped entirely (no screenshot uploaded) without touching the generation
path at all — the form still works standalone.

## 3. API integration strategy

- **SDK**: uses `google-genai` (the current, actively maintained SDK), not
  the older `google-generativeai` package — that one was deprecated by
  Google in late 2025 and is now in unmaintained legacy mode, which turned
  out to be the source of some odd instability during development (see
  note below).
- **Model**: `gemini-3.6-flash`, centralized as a single `MODEL_NAME`
  constant rather than repeated as a magic string, since Gemini's model
  lineup has moved fast this year (2.0 → 2.5 → 3.x, with older versions
  retired for new API keys) — bumping it later is a one-line change.
- **Key handling**: the API key is never hardcoded. It's read either from
  a sidebar text input (session-only, never persisted) or from
  `st.secrets["GEMINI_API_KEY"]` as a fallback, which lets a deployed demo
  work without requiring the visitor to have their own key. Real secrets
  are excluded from git via `.gitignore`.
- **Structured output from vision**: the vision prompt explicitly asks for
  raw JSON with no markdown fences, and the parsing code strips fences
  defensively anyway (Gemini doesn't always obey formatting instructions
  perfectly) before `json.loads()`.

**Development note**: an earlier version of this app used the legacy
`google-generativeai` package and hit a segfault crash during Gemini calls
in more than one environment. Migrating to `google-genai` (Google's current
SDK) resolved it — a good example of why depending on a deprecated library
is worth avoiding even mid-project.

## 4. Logic modules

| Module | Responsibility |
|---|---|
| `build_prompt()` | Assembles the text-generation prompt from form fields + optional JD keywords. Isolated so prompt wording can be iterated without touching API call logic. |
| `generate_email()` | Owns the Gemini text-generation call and model config. |
| `extract_jd_from_screenshot()` | Owns the Gemini vision call, image encoding, and JSON parsing/cleanup. |
| Session state block | Initializes `history`, `last_email`, `gemini_configured`, `extracted_*` — all state that must survive Streamlit's rerun-on-every-interaction model. |
| Generate tab | Form UI, screenshot uploader, wiring extracted values into form defaults. |
| Dashboard tab | Derives a Pandas DataFrame from `history`, renders KPI metrics, bar chart, and the editable table; writes edits back into session state. |

## 5. Known limitations

- History is session-only — refreshing the browser tab or restarting the
  server clears it. Acceptable for a capstone demo; a production version
  would persist to a database.
- Vision extraction assumes a reasonably legible screenshot; very low-res
  or heavily cropped images may return incomplete JSON, which is caught
  and surfaced as an error rather than silently failing.