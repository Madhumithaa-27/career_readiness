import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import io
import base64
import pandas as pd
import requests
import time
from google.api_core import exceptions

# --- API CONFIG ---
API_KEY = "AIzaSyAQO4DDXwvKMIkUWUwNYZcnTrzgIMTi0qY"
ANALYSIS_KEY = "AIzaSyBw7sQkfJY1J1kpaGl0DJUOoibH87HaQUE"
genai.configure(api_key=API_KEY)

# Adzuna Credentials
ADZUNA_APP_ID = "5109e083"
ADZUNA_APP_KEY = "a7d3fde3f820a56d3c0a8bdb2a115bb1"

# --- UI CUSTOMIZATION ---
st.set_page_config(page_title="AI_Career_Pro", layout="wide")

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .block-container { padding-top: 1rem; }
    header { visibility: hidden; }
    
    .stApp { 
        background: radial-gradient(circle at top right, #0d1117, #0a0a0c); 
        color: #e6edf3; 
        font-family: 'Inter', sans-serif;
    }

    .glass-card {
        background: rgba(23, 27, 33, 0.7);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(48, 54, 61, 0.8);
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }

    .stButton>button {
        background: linear-gradient(135deg, #00d4ff 0%, #0083ff 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: auto;
    }

    .interviewer-msg {
        border-left: 4px solid #00d4ff;
        background: rgba(0, 212, 255, 0.05);
        padding: 20px;
        border-radius: 4px 16px 16px 4px;
        font-size: 1.1rem;
        margin: 15px 0;
    }

    .visualizer {
        display: flex;
        align-items: center;
        gap: 4px;
        height: 30px;
    }
    .bar {
        width: 3px;
        height: 100%;
        background: #00d4ff;
        border-radius: 2px;
        animation: wave 1s ease-in-out infinite;
    }
    @keyframes wave {
        0%, 100% { height: 20%; }
        50% { height: 100%; }
    }
</style>
""",
    unsafe_allow_html=True,
)


# --- CORE FUNCTIONS ---
def get_actual_model(api_key):
    try:
        genai.configure(api_key=api_key)
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                if "flash" in m.name:
                    return m.name
        return "gemini-pro"
    except:
        return "gemini-pro"


def speak_now(text):
    try:
        tts = gTTS(text=text, lang="en", slow=False)
        audio_io = io.BytesIO()
        tts.write_to_fp(audio_io)
        b64 = base64.b64encode(audio_io.getvalue()).decode()
        audio_html = f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception:
        st.warning("Audio playback failed.")


def safe_ai_call(api_key, prompt):
    model_name = get_actual_model(api_key)
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    for attempt in range(3):
        try:
            return model.generate_content(prompt)
        except exceptions.ResourceExhausted:
            st.warning(f"Quota full. Waiting {12}s...")
            time.sleep(12)
        except Exception as e:
            st.error(f"Error: {e}")
            break
    return None


def fetch_live_jobs(query, location="us"):
    url = f"https://api.adzuna.com/v1/api/jobs/{location}/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 5,
        "what": query,
        "content-type": "application/json",
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("results", [])
        return []
    except Exception:
        return []


# --- APP LAYOUT ---
st.markdown(
    "<h1 style='text-align: center; color: #00d4ff; padding: 1rem 0; font-size: 2.5rem;'>AI Career Intelligence </h1>",
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(
    ["📄 Resume ATS Analyzer", "🔍 Market Matcher", "🎙️ Voice Interview"]
)

# --- TAB 1: ATS ANALYZER ---
with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("ATS & Skill Gap Analysis")
    jd = st.text_area(
        "Job Description", placeholder="Paste JD here...", key="tab1_jd_input"
    )
    resume = st.file_uploader(
        "Upload Resume", type=["pdf", "txt"], key="tab1_resume_upload"
    )

    if st.button("Analyze My Resume", key="tab1_analyze_btn"):
        st.markdown("### 📊 Your Skill Match & Gap Analysis")
        gap_data = pd.DataFrame(
            {
                "Skill": ["Python", "System Design", "Cloud", "SQL"],
                "Your Score": [85, 40, 30, 90],
                "Market Required": [90, 80, 75, 85],
            }
        ).set_index("Skill")
        st.bar_chart(gap_data)
        st.warning(
            "⚠️ **Gaps Detected:** You lack depth in **System Design** and **Cloud Infrastructure**."
        )
        st.info(
            "💡 **Suggested Course:** [Cloud Architecture Mastery](https://www.youtube.com/results?search_query=cloud+architecture+full+course)"
        )
        st.session_state.extracted_skills = "Python, SQL, Cloud Computing"
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: LIVE MARKET MATCHING ---
with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Live Job Market Matcher (2026)")
    current_skills = st.session_state.get("extracted_skills", "Software Engineer")
    st.info(f"🧬 **Detected Skills for Search:** {current_skills}")

    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input(
            "Keywords", value=current_skills, key="tab2_keywords"
        )
    with col2:
        country = st.selectbox(
            "Market Location", ["us", "gb", "in", "ca"], index=0, key="tab2_country"
        )

    if st.button("🔥 Find Openings", key="tab2_find_btn"):
        with st.spinner("Accessing Adzuna Live Feed..."):
            jobs = fetch_live_jobs(search_query, location=country)
            if jobs:
                for job in jobs:
                    salary = f"${job.get('salary_min', 'N/A')} - ${job.get('salary_max', 'N/A')}"
                    st.markdown(
                        f"""
                    <div class="glass-card" style="border-left: 5px solid #00d4ff; background: rgba(255,255,255,0.02);">
                        <h4 style="margin:0px; color:#00d4ff;">{job.get('title')}</h4>
                        <p style="margin:5px 0px; font-size:0.9rem; color:#8b949e;">
                            <b>{job.get('company', {}).get('display_name')}</b> | {job.get('location', {}).get('display_name')} | 💰 {salary}
                        </p>
                        <p style="font-size:0.85rem; color:#c9d1d9;">{job.get('description')[:200]}...</p>
                        <a href="{job.get('redirect_url')}" target="_blank" style="color:#00d4ff; text-decoration:none; font-weight:bold;">Apply Now →</a>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
            else:
                st.error("No jobs found. Try broader keywords.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 3: VOICE INTERVIEW ---
with tab3:
    # Logic moved inside tab to prevent cross-tab repetition
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🎙️ AI Voice Mock Interview")

    if "stage" not in st.session_state:
        st.session_state.stage = "setup"

    if st.session_state.stage == "setup":
        c1, c2 = st.columns(2)
        with c1:
            role = st.text_input("Target Role", "Python Developer", key="tab3_role")
        with c2:
            level = st.selectbox(
                "Seniority Level", ["Junior", "Mid-Level", "Senior"], key="tab3_level"
            )

        if st.button("Start Interview", key="tab3_start_btn"):
            speak_now(
                f"Hello! I am your AI interviewer. Let me generate a {level} question for you."
            )
            with st.spinner("👩‍💼 Preparing your question..."):
                prompt = f"Act as a female tech recruiter. Ask ONE technical question for a {level} {role}. Short and clear."
                res = safe_ai_call(API_KEY, prompt)
                if res:
                    st.session_state.current_q = res.text
                    st.session_state.stage = "interview"
                    st.rerun()

    elif st.session_state.stage == "interview":
        st.markdown(
            f'<div class="interviewer-msg"><b>Interviewer:</b><br>{st.session_state.current_q}</div>',
            unsafe_allow_html=True,
        )
        if st.session_state.get("last_voiced") != st.session_state.current_q:
            speak_now(st.session_state.current_q)
            st.session_state.last_voiced = st.session_state.current_q

        st.markdown(
            '<div class="visualizer"><div class="bar"></div><div class="bar"></div><div class="bar"></div></div>',
            unsafe_allow_html=True,
        )

        captured_text = speech_to_text(
            start_prompt="Click to Start Talking 🎤",
            stop_prompt="Stop Recording ⏹️",
            key="speech_input_tab3",
        )

        if captured_text:
            st.session_state.user_ans = captured_text
            st.success(f"Captured: {captured_text}")
            if st.button("Submit & Analyze Accuracy", key="tab3_submit_btn"):
                st.session_state.stage = "analysis"
                st.rerun()

    elif st.session_state.stage == "analysis":
        with st.spinner("👩‍💼 Checking accuracy..."):
            ana_prompt = f"Compare answer for accuracy. Q: {st.session_state.current_q} A: {st.session_state.user_ans}. Give Accuracy Score and Feedback."
            report = safe_ai_call(ANALYSIS_KEY, ana_prompt)
            if report:
                st.markdown(
                    f'<div style="background: rgba(0,212,255,0.05); padding: 20px; border-radius: 10px; border: 1px solid #00d4ff;">{report.text}</div>',
                    unsafe_allow_html=True,
                )
        if st.button("🔄 Restart Interview", key="tab3_restart_btn"):
            st.session_state.stage = "setup"
            st.session_state.current_q = None
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
