import streamlit as st
import requests
import os
import json

st.set_page_config(
    page_title="JobCopilot AI - Resume Analyzer",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Theme Injected CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling overrides */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Layout Aesthetics */
    .main-title {
        background: linear-gradient(90deg, #FF7B00 0%, #FFAE00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #8C8C8C;
        margin-bottom: 2rem;
    }
    
    /* Card Aesthetics */
    .metric-card {
        background: #1E1E1E;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #333333;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #FF7B00;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #8C8C8C;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.1em;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin-top: 0.5rem;
        background: linear-gradient(135deg, #FFFFFF 0%, #D9D9D9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-value.excellent {
        background: linear-gradient(135deg, #00FF87 0%, #60EFFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-value.good {
        background: linear-gradient(135deg, #FFFB00 0%, #FFB200 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-value.warning {
        background: linear-gradient(135deg, #FF4B4B 0%, #FF7474 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .priority-fix-card {
        background: #2D1A12;
        border-left: 5px solid #FF7B00;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    
    .priority-fix-text {
        font-size: 1rem;
        font-weight: 500;
        color: #FFE6D5;
    }
    
    .info-card {
        background: #141414;
        border: 1px solid #262626;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    
    .list-item {
        margin-bottom: 0.5rem;
        color: #CCCCCC;
    }
    
    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #F5F5F5;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
        border-bottom: 1px solid #333;
        padding-bottom: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## ⚙️ Configuration")
api_base_url = st.sidebar.text_input("FastAPI Base URL", value="http://localhost:8000")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📤 Upload & Parameters")

uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
target_role = st.sidebar.text_input("Target Role / Position", placeholder="e.g. Senior Frontend Engineer")
job_description = st.sidebar.text_area("Target Job Description (Optional)", placeholder="Paste the job description details here to match keywords and requirements...", height=200)

analyze_button = st.sidebar.button("🚀 Analyze Resume", use_container_width=True)

# Helper function to assign score color classes
def get_score_class(score):
    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "good"
    else:
        return "warning"

# Header
st.markdown('<div class="main-title">JobCopilot AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Multi-Agent Intelligent Resume Analyzer & Enhancer</div>', unsafe_allow_html=True)

if not analyze_button:
    st.info("👈 Fill out the configurations and upload your resume in the sidebar to start analyzing.")
    
    # Showcase Features / Landing Layout
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">ATS Compatibility</div>
            <div class="metric-value" style="font-size:1.8rem; margin-top: 1rem;">Structure Audit</div>
            <p style="color:#8C8C8C; font-size:0.85rem; margin-top:0.5rem;">Scans margins, contact details, fonts, structure, tables, and standard headers matching common corporate ATS software.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Recruiter Screening</div>
            <div class="metric-value" style="font-size:1.8rem; margin-top: 1rem;">Candidate Fit</div>
            <p style="color:#8C8C8C; font-size:0.85rem; margin-top:0.5rem;">Simulates a real human recruiter's first impression, calculating the shortlist probability and evaluating key strengths.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Keyword Match</div>
            <div class="metric-value" style="font-size:1.8rem; margin-top: 1rem;">Skill Gap Analysis</div>
            <p style="color:#8C8C8C; font-size:0.85rem; margin-top:0.5rem;">Compares your resume text against the target role and job description to identify missing tools, technologies, and buzzwords.</p>
        </div>
        """, unsafe_allow_html=True)

else:
    # Validation
    if not uploaded_file:
        st.error("Please upload a resume file (.pdf or .docx).")
    elif not target_role.strip():
        st.error("Please enter a Target Role / Position.")
    else:
        # Perform API call
        with st.spinner("Analyzing resume... This executes 6 AI agents in parallel (usually takes ~5-7 seconds)"):
            try:
                # Prepare payload
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {
                    "target_role": target_role,
                    "job_description": job_description or ""
                }
                
                # Make POST request to FastAPI endpoint with a longer timeout for local model execution
                url = f"{api_base_url.rstrip('/')}/api/v1/analyze"
                response = requests.post(url, files=files, data=data, timeout=6000)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract variables
                    ats_res = result.get("ats_result", {})
                    rec_res = result.get("recruiter_result", {})
                    gram_res = result.get("grammar_result", {})
                    proj_res = result.get("project_result", {})
                    key_res = result.get("keyword_result", {})
                    quest_res = result.get("question_result", {})
                    agg_res = result.get("aggregated_result", {})
                    
                    overall_score = agg_res.get("overall_score", 0)
                    priority_fixes = agg_res.get("priority_fixes", [])
                    dashboard_data = agg_res.get("dashboard_data", {})
                    
                    st.success("Analysis complete!")
                    
                    # Metrics Grid Row
                    st.markdown('<div class="section-title">📊 Executive Dashboard Summary</div>', unsafe_allow_html=True)
                    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
                    
                    with m_col1:
                        score_cls = get_score_class(overall_score)
                        st.markdown(f"""
                        <div class="metric-card" style="border: 2px solid #FF7B00;">
                            <div class="metric-label" style="color: #FF7B00; font-weight:700;">Overall Fit</div>
                            <div class="metric-value {score_cls}">{overall_score}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with m_col2:
                        ats_score = ats_res.get("score", 0)
                        score_cls = get_score_class(ats_score)
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">ATS Score</div>
                            <div class="metric-value {score_cls}">{ats_score}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with m_col3:
                        rec_prob = rec_res.get("shortlist_probability", 0)
                        score_cls = get_score_class(rec_prob)
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Shortlist Prob</div>
                            <div class="metric-value {score_cls}">{rec_prob}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with m_col4:
                        key_score = key_res.get("match_score", 0)
                        score_cls = get_score_class(key_score)
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Keyword Match</div>
                            <div class="metric-value {score_cls}">{key_score}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with m_col5:
                        gram_score = gram_res.get("score", 0)
                        score_cls = get_score_class(gram_score)
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Grammar Score</div>
                            <div class="metric-value {score_cls}">{gram_score}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Layout splitting Priority Fixes and Detailed Analysis Tabs
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    c_left, c_right = st.columns([1, 2])
                    
                    with c_left:
                        st.markdown('<div class="section-title">⚠️ Priority Action Items</div>', unsafe_allow_html=True)
                        if not priority_fixes:
                            st.success("Great job! No high-priority fixes identified.")
                        else:
                            for idx, fix in enumerate(priority_fixes, 1):
                                st.markdown(f"""
                                <div class="priority-fix-card">
                                    <div class="priority-fix-text">🛠️ {fix}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                    with c_right:
                        st.markdown('<div class="section-title">🔍 Comprehensive Analysis Reports</div>', unsafe_allow_html=True)
                        
                        tab1, tab2, tab3, tab4 = st.tabs([
                            "📄 ATS & Formatting",
                            "💼 Recruiter & Projects",
                            "🎯 Keywords & Skills",
                            "❓ Interview Prep"
                        ])
                        
                        with tab1:
                            st.subheader("ATS Formatting Assessment")
                            st.write(f"**Score:** `{ats_score}/100`")
                            
                            col_a1, col_a2 = st.columns(2)
                            with col_a1:
                                st.markdown("**Formatting & Layout Issues:**")
                                issues = ats_res.get("issues", [])
                                if issues:
                                    for issue in issues:
                                        st.markdown(f"- 🔴 {issue}")
                                else:
                                    st.success("No layout issues detected.")
                            with col_a2:
                                st.markdown("**Optimization Suggestions:**")
                                suggestions = ats_res.get("suggestions", [])
                                if suggestions:
                                    for sugg in suggestions:
                                        st.markdown(f"- 💡 {sugg}")
                                else:
                                    st.success("No formatting suggestions.")
                                    
                            st.markdown("---")
                            st.subheader("Grammar, Readability & Style")
                            st.write(f"**Score:** `{gram_score}/100`")
                            
                            col_g1, col_g2 = st.columns(2)
                            with col_g1:
                                st.markdown("**Grammar & Sentence Style Issues:**")
                                errors = gram_res.get("errors", [])
                                if errors:
                                    for err in errors:
                                        st.markdown(f"- ⚠️ {err}")
                                else:
                                    st.success("No grammar errors detected!")
                            with col_g2:
                                st.markdown("**Writing Suggestions:**")
                                suggestions = gram_res.get("suggestions", [])
                                if suggestions:
                                    for sugg in suggestions:
                                        st.markdown(f"- 💡 {sugg}")
                                else:
                                    st.success("No writing style suggestions.")
                                    
                        with tab2:
                            st.subheader("Recruiter First Impression")
                            st.write(f"**Shortlist Probability:** `{rec_prob}%`")
                            
                            feedback = rec_res.get("feedback", [])
                            if feedback:
                                for fb in feedback:
                                    st.markdown(f"- 👤 {fb}")
                            else:
                                st.info("No recruiter feedback compiled.")
                                
                            st.markdown("---")
                            st.subheader("Project Technical Depth Analysis")
                            if proj_res:
                                st.write(f"**Technical Complexity Score:** `{proj_res.get('score', 0)}/100`")
                                col_p1, col_p2 = st.columns(2)
                                with col_p1:
                                    st.markdown("**Observations on Complexity & Scale:**")
                                    depth = proj_res.get("depth_analysis", [])
                                    if depth:
                                        for d in depth:
                                            st.markdown(f"- ⚙️ {d}")
                                    else:
                                        st.info("No projects detected or analyzed.")
                                with col_p2:
                                    st.markdown("**Architectural Recommendations:**")
                                    suggs = proj_res.get("suggestions", [])
                                    if suggs:
                                        for s in suggs:
                                            st.markdown(f"- 💡 {s}")
                                    else:
                                        st.success("No specific project enhancement suggestions.")
                            else:
                                st.info("Project depth analysis was not run.")
                                
                        with tab3:
                            st.subheader("Keyword & Skills Alignment")
                            st.write(f"**Alignment Score:** `{key_score}/100`")
                            
                            col_k1, col_k2 = st.columns(2)
                            with col_k1:
                                st.markdown("**Missing Required Skills:**")
                                missing_skills = key_res.get("missing_skills", [])
                                if missing_skills:
                                    for skill in missing_skills:
                                        st.markdown(f"- ❌ `{skill}`")
                                else:
                                    st.success("All required skills match!")
                                    
                                st.markdown("**Missing Keywords/Buzzwords:**")
                                missing_keywords = key_res.get("missing_keywords", [])
                                if missing_keywords:
                                    for keyword in missing_keywords:
                                        st.markdown(f"- 🔍 `{keyword}`")
                                else:
                                    st.success("All recommended keywords are present!")
                                    
                            with col_k2:
                                st.markdown("**Skill Gap Assessment Summary:**")
                                gaps = key_res.get("skill_gaps", [])
                                if gaps:
                                    for gap in gaps:
                                        st.markdown(f"- 📌 {gap}")
                                else:
                                    st.success("No notable skill gaps identified.")
                                    
                        with tab4:
                            st.subheader("Intelligent Follow-Up Prep Questions")
                            st.info("These questions are dynamically generated based on vague metrics or unspecified technologies in your resume. Be ready to answer these in an interview.")
                            
                            questions = quest_res.get("questions", [])
                            if questions:
                                for idx, q in enumerate(questions, 1):
                                    st.markdown(f"**{idx}.** {q}")
                            else:
                                st.success("No specific clarifying questions generated. Resume content is detailed and clear!")
                                
                else:
                    st.error(f"Backend Server Error ({response.status_code}): {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend server. Please verify the FastAPI backend is running and the port is correct.")
                st.info("To start the backend, run: \n`python main.py` or `uvicorn main:app --reload`")
            except Exception as e:
                st.error(f"An unexpected error occurred during request: {str(e)}")
