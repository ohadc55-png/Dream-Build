import streamlit as st
from utils.auth import login_dev
from utils.styling import apply_custom_css
from utils.nav import render_sidebar  # <-- הייבוא החדש

# הגדרות עמוד
st.set_page_config(
    page_title="Dream & Build",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()

# אתחול Session
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

# --- מסך כניסה ---
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.image("https://i.postimg.cc/SKL4H4GV/לוגו_D_B.png", use_container_width=True)
        st.markdown("<h3 style='text-align: center;'>כניסה למערכת</h3>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            full_name = st.text_input("👤 שם מלא")
            email = st.text_input("📧 אימייל")
            role_display = st.radio("תפקיד:", ["מנהל מערכת 🛠️", "עובד צוות 👷"], horizontal=True)
            
            submit = st.form_submit_button("🚀 כניסה")
            
            if submit and email and full_name:
                role = "manager" if "מנהל" in role_display else "employee"
                result = login_dev(email, role, full_name)
                st.session_state.authenticated = True
                st.session_state.user = result['user']
                st.rerun()

# --- מסך ראשי (אחרי התחברות) ---
else:
    # כאן אנחנו קוראים לתפריט שיצרנו ב-nav.py
    render_sidebar()
    
    user = st.session_state.user
    st.title("ברוכים הבאים ל-Dream & Build")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"שלום **{user['full_name']}**, בחר בתפריט בצד כדי להתחיל.")
    with col2:
        st.image("https://i.postimg.cc/TY5ZZGd5/סדנא.jpg", use_container_width=True)