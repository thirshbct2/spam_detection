# Get folder statistics
stats = get_folder_stats(CURRENT_DIR)

# Email selection at the top
st.markdown("### 📧 Select Email to Analyze")
selected_email = st.selectbox("Choose email", email_files, label_visibility="collapsed", index=None, placeholder="Select an email...")

# Only show everything if an email is selected
if selected_email:
    # Stats row - only show after selection
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
