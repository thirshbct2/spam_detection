import os
import streamlit as st
from email_parser import parse_eml
from spam_detector import detect_spam
from file_mover import copy_email_with_reason, get_folder_stats
from database import init_db, log_analysis, get_analysis_history, get_stats

# Configure page
st.set_page_config(
    page_title="AI Spam Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - No space anywhere, unique design
st.markdown("""
<style>
    /* Remove all padding and margins */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Full width container */
    .stApp {
        margin: 0;
        padding: 0;
    }
    
    /* Unique gradient header */
    .cyber-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px 40px;
        color: white;
        margin: 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .cyber-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Spam alert - dramatic red */
    .spam-box {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        margin: 20px 0;
        box-shadow: 0 8px 16px rgba(255,107,107,0.3);
        border: none;
    }
    
    .spam-box h3 {
        margin: 0 0 15px 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    /* Safe alert - vibrant green */
    .safe-box {
        background: linear-gradient(135deg, #51cf66 0%, #37b24d 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        margin: 20px 0;
        box-shadow: 0 8px 16px rgba(81,207,102,0.3);
        border: none;
    }
    
    .safe-box h3 {
        margin: 0 0 15px 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    /* Info boxes */
    .info-box {
        background: #e7f5ff;
        border-left: 4px solid #1971c2;
        padding: 15px;
        margin: 15px 0;
        border-radius: 4px;
    }
    
    /* Stats boxes */
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 10px 0;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Warning boxes */
    .warning-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
        font-weight: 500;
    }
    
    .error-box {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
init_db()

# Header
st.markdown("""
<div class="cyber-header">
    <h1>🛡️ AI SPAM DETECTOR</h1>
</div>
""", unsafe_allow_html=True)

# Get current directory and mails folder
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MAILS_FOLDER = os.path.join(CURRENT_DIR, "mails")

# Get list of .eml files from mails folder
email_files = []
if os.path.exists(MAILS_FOLDER):
    email_files = [f for f in os.listdir(MAILS_FOLDER) if f.endswith(".eml")]

if not email_files:
    st.warning("⚠️ No emails found in 'mails' folder!")
    st.info("Please add .eml files to the mails folder to analyze them.")
    st.stop()

# Email selection at the top - with placeholder, no default selection
st.markdown("### 📧 Select Email to Analyze")
selected_email = st.selectbox(
    "Choose email", 
    email_files, 
    label_visibility="collapsed",
    index=None,
    placeholder="Click here to select an email..."
)

# Initialize session state for tracking current session stats
if 'session_stats' not in st.session_state:
    st.session_state.session_stats = {'spam_count': 0, 'real_count': 0, 'total_classified': 0}
if 'analyzed_emails' not in st.session_state:
    st.session_state.analyzed_emails = set()

# Only show stats and email details if email is selected
if selected_email:
    # Stats row - only visible after email selection
    stats = st.session_state.session_stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">🚨 {stats['spam_count']}</div>
            <div class="stat-label">Spam Detected</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">✅ {stats['real_count']}</div>
            <div class="stat-label">Legitimate Emails</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">📊 {stats['total_classified']}</div>
            <div class="stat-label">Total Analyzed</div>
        </div>
        """, unsafe_allow_html=True)
    
    email_path = os.path.join(MAILS_FOLDER, selected_email)
    parsed = parse_eml(email_path)
    
    # Two column layout
    col1, col2 = st.columns([1, 1], gap="small")
    
    with col1:
        st.markdown("### 📩 Email Details")
        st.markdown(f"""
        <div class="info-box">
            <strong>From:</strong> {parsed['from']}<br>
            <strong>To:</strong> {parsed['to']}<br>
            <strong>Subject:</strong> {parsed['subject']}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📄 Content")
        st.text_area("Email body", parsed["body"], height=400, label_visibility="collapsed")
    
    with col2:
        st.markdown("### 🔍 AI Analysis")
        
        # Detect spam
        with st.spinner("🤖 Analyzing..."):
            spam_result = detect_spam(parsed)
        
        # Update session stats only if this email hasn't been analyzed yet
        if selected_email not in st.session_state.analyzed_emails:
            st.session_state.analyzed_emails.add(selected_email)
            if spam_result["is_spam"]:
                st.session_state.session_stats['spam_count'] += 1
            else:
                st.session_state.session_stats['real_count'] += 1
            st.session_state.session_stats['total_classified'] += 1
            # Force rerun to update stats display
            st.rerun()
        
        # Display result
        if spam_result["is_spam"]:
            st.markdown(f"""
            <div class="spam-box">
                <h3>⚠️ {spam_result['classification']} ({spam_result['confidence']}% confidence)</h3>
                <p style="margin: 0; font-size: 1.1rem; line-height: 1.6;">{spam_result['reason']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="error-box">🚫 <strong>DO NOT RESPOND</strong> to this email!</div>
            <div class="warning-box">⚠️ <strong>DO NOT CLICK</strong> any links!</div>
            <div class="warning-box">⚠️ <strong>DO NOT SHARE</strong> personal information!</div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown(f"""
            <div class="safe-box">
                <h3>✅ {spam_result['classification']} ({spam_result['confidence']}% confidence)</h3>
                <p style="margin: 0; font-size: 1.1rem; line-height: 1.6;">{spam_result['reason']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="info-box">✅ <strong>SAFE TO RESPOND</strong> - This email appears genuine!</div>
            <div class="info-box">👍 <strong>VERIFY SENDER</strong> - Double check the email address if unsure!</div>
            <div class="info-box">🔒 <strong>STAY CAUTIOUS</strong> - Still avoid sharing sensitive data unless necessary!</div>
            """, unsafe_allow_html=True)
        
        # Automatically copy to appropriate folder (silently)
        copy_result = copy_email_with_reason(
            email_filename=selected_email,
            is_spam=spam_result["is_spam"],
            reason=spam_result["reason"],
            source_dir=MAILS_FOLDER
        )
        
        # Log to database
        log_analysis(selected_email, parsed, spam_result, copy_result)

# Analysis History Section
st.markdown("---")
st.markdown("### 📊 Analysis History (Debug Log)")

with st.expander("View Recent Analysis History", expanded=False):
    history = get_analysis_history(limit=50)
    
    if history:
        for record in history:
            status_icon = "🚨" if record["is_spam"] else "✅"
            timestamp = record["timestamp"].split("T")[0] + " " + record["timestamp"].split("T")[1][:8]
            
            st.markdown(f"""
            <div class="info-box">
                <strong>{status_icon} {record['classification']}</strong> - {record['email_filename']} <strong>({record['confidence']}% confidence)</strong><br>
                <small>📅 {timestamp} | From: {record['sender']}</small><br>
                <small>📁 Copied to: {record['copied_to_folder']}/</small><br>
                <small>💬 {record['reason']}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No analysis history yet. Analyze an email to see logs here.")

