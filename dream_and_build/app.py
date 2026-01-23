import streamlit as st
from utils.auth import login, register, logout
from utils.styling import apply_custom_css

# === הגדרות עמוד ===
st.set_page_config(
    page_title="Dream & Build",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === אתחול Session State ===
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

# === CSS מותאם למסך כניסה ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800;900&display=swap');

* { font-family: 'Heebo', sans-serif !important; }

[data-testid="stSidebar"] { display: none; }
#MainMenu, footer, header { visibility: hidden; }

.login-container {
    max-width: 420px;
    margin: 0 auto;
    padding: 2rem;
}

.login-header {
    text-align: center;
    margin-bottom: 2rem;
}

.login-logo {
    font-size: 4rem;
    margin-bottom: 1rem;
}

.login-title {
    font-size: 2rem;
    font-weight: 800;
    color: #1A2840;
    margin-bottom: 0.5rem;
}

.login-title span {
    color: #FF8C00;
}

.login-subtitle {
    color: #6B7280;
    font-size: 1rem;
}

.stApp {
    background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
}

.stTabs [data-baseweb="tab-list"] {
    justify-content: center;
    gap: 0;
    background: white;
    border-radius: 12px;
    padding: 4px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.stTabs [data-baseweb="tab"] {
    flex: 1;
    justify-content: center;
    border-radius: 10px;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #FF8C00, #FFA500) !important;
    color: white !important;
}

div[data-testid="stForm"] {
    background: white;
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border: 1px solid #E5E7EB;
}

.stButton > button {
    background: linear-gradient(135deg, #FF8C00 0%, #FFA500 100%);
    color: white !important;
    border: none;
    border-radius: 10px;
    padding: 0.75rem 2rem;
    font-weight: 600;
    font-size: 1rem;
    box-shadow: 0 4px 15px rgba(255, 140, 0, 0.3);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255, 140, 0, 0.4);
}

.feature-box {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    border: 1px solid #E5E7EB;
}

.feature-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.feature-title {
    font-weight: 600;
    color: #1A2840;
    margin-bottom: 0.25rem;
}

.feature-desc {
    font-size: 0.85rem;
    color: #6B7280;
}
</style>
""", unsafe_allow_html=True)


# === אם מחובר - הפניה לדשבורד ===
if st.session_state.authenticated:
    user = st.session_state.user
    
    # הפניה לדף המתאים
    if user.get('role') == 'manager':
        st.switch_page("pages/dashboard_manager.py")
    else:
        st.switch_page("pages/dashboard_employee.py")


# === מסך כניסה ===
else:
    # Header
    st.markdown("""
    <div class="login-header">
        <div class="login-logo">🔨</div>
        <h1 class="login-title">Dream & <span>Build</span></h1>
        <p class="login-subtitle">מערכת ניהול סדנאות נגרות</p>
    </div>
    """, unsafe_allow_html=True)
    
    # טאבים
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 התחברות", "📝 הרשמה"])
        
        # === טאב התחברות ===
        with tab1:
            with st.form("login_form", clear_on_submit=False):
                st.markdown("#### 👋 ברוכים השבים!")
                
                email = st.text_input(
                    "אימייל",
                    placeholder="your@email.com",
                    key="login_email"
                )
                password = st.text_input(
                    "סיסמה",
                    type="password",
                    placeholder="••••••••",
                    key="login_password"
                )
                
                submit = st.form_submit_button("התחבר", use_container_width=True)
                
                if submit:
                    if not email or not password:
                        st.error("⚠️ נא למלא את כל השדות")
                    else:
                        with st.spinner("מתחבר..."):
                            result = login(email, password)
                        
                        if result['success']:
                            st.session_state.authenticated = True
                            st.session_state.user = result['user']
                            st.success("✅ התחברת בהצלחה!")
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")
        
        # === טאב הרשמה ===
        with tab2:
            with st.form("register_form", clear_on_submit=False):
                st.markdown("#### 🆕 יצירת חשבון חדש")
                
                full_name = st.text_input(
                    "שם מלא",
                    placeholder="ישראל ישראלי",
                    key="reg_name"
                )
                email_reg = st.text_input(
                    "אימייל",
                    placeholder="your@email.com",
                    key="reg_email"
                )
                phone = st.text_input(
                    "טלפון",
                    placeholder="050-0000000",
                    key="reg_phone"
                )
                
                col_pass1, col_pass2 = st.columns(2)
                with col_pass1:
                    password_reg = st.text_input(
                        "סיסמה",
                        type="password",
                        placeholder="לפחות 6 תווים",
                        key="reg_password"
                    )
                with col_pass2:
                    password_confirm = st.text_input(
                        "אימות סיסמה",
                        type="password",
                        placeholder="שוב...",
                        key="reg_password_confirm"
                    )
                
                role = st.selectbox(
                    "תפקיד",
                    ["employee", "manager"],
                    format_func=lambda x: "👷 עובד" if x == "employee" else "👔 מנהל",
                    key="reg_role"
                )
                
                submit_reg = st.form_submit_button("הרשמה", use_container_width=True)
                
                if submit_reg:
                    if not all([full_name, email_reg, phone, password_reg, password_confirm]):
                        st.error("⚠️ נא למלא את כל השדות")
                    elif password_reg != password_confirm:
                        st.error("❌ הסיסמאות לא תואמות")
                    elif len(password_reg) < 6:
                        st.error("❌ הסיסמה חייבת להכיל לפחות 6 תווים")
                    else:
                        with st.spinner("נרשם..."):
                            result = register(email_reg, password_reg, full_name, phone, role)
                        
                        if result['success']:
                            st.success("✅ נרשמת בהצלחה! אפשר להתחבר")
                            st.balloons()
                        else:
                            st.error(f"❌ {result['message']}")
    
    # === Features Section ===
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    features = [
        ("📊", "דשבורד חכם", "מעקב בזמן אמת"),
        ("🏫", "ניהול לקוחות", "בתי ספר ותקציבים"),
        ("👥", "ניהול צוות", "עובדים ושכר"),
        ("💰", "דוחות כספיים", "הכנסות והוצאות"),
    ]
    
    for col, (icon, title, desc) in zip([col1, col2, col3, col4], features):
        with col:
            st.markdown(f"""
            <div class="feature-box">
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">{title}</div>
                <div class="feature-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
