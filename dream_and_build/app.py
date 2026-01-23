import streamlit as st
from utils.auth import login_dev
from utils.styling import apply_custom_css
from utils.nav import render_sidebar

# הגדרות עמוד
st.set_page_config(
    page_title="Dream & Build",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()

# אתחול
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

# --- מסך כניסה (ללא סיסמה) ---
if not st.session_state.authenticated:
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.image("https://i.postimg.cc/SKL4H4GV/לוגו_D_B.png", use_container_width=True)
        st.markdown("<h3 style='text-align: center; color: #1A2840;'>כניסה למערכת</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>מצב פיתוח - כניסה מהירה</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            full_name = st.text_input("👤 שם מלא", placeholder="ישראל ישראלי")
            email = st.text_input("📧 אימייל", placeholder="user@example.com")
            
            role_display = st.radio("בחר תפקיד:", ["מנהל מערכת 🛠️", "עובד צוות 👷"], horizontal=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("🚀 כנס למערכת")
            
            if submit:
                if full_name and email:
                    role = "manager" if "מנהל" in role_display else "employee"
                    result = login_dev(email, role, full_name)
                    st.session_state.authenticated = True
                    st.session_state.user = result['user']
                    st.toast(result['message'], icon="✅")
                    st.rerun()
                else:
                    st.warning("נא למלא שם ואימייל")

# --- מסך ראשי (אחרי התחברות) ---
else:
    render_sidebar()
    user = st.session_state.user
    
    st.title("🔨 ברוכים הבאים ל-Dream & Build")
    st.info(f"שלום **{user['full_name']}**, המערכת מוכנה לעבודה.")
    st.markdown("בחר אפשרות מהתפריט בצד.")