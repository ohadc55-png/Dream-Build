import streamlit as st
from utils.auth import login, register, logout, check_auth
from utils.styling import apply_custom_css
import base64

# הגדרות עמוד
st.set_page_config(
    page_title="Dream & Build - ניהול סדנאות נגרות",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# החלת עיצוב מותאם
apply_custom_css()

# טעינת תמונות
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

# בדיקת אימות
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

# עמוד כניסה/הרשמה
if not st.session_state.authenticated:
    
    # לוגו
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("assets/logo.png", width=300)
        except:
            st.title("🔨 Dream & Build")
    
    st.markdown("<h2 style='text-align: center; color: #FF8C00;'>מערכת ניהול סדנאות נגרות</h2>", unsafe_allow_html=True)
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    # טאבים להתחברות והרשמה
    tab1, tab2 = st.tabs(["🔐 התחברות", "📝 הרשמה"])
    
    with tab1:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("📧 אימייל", placeholder="example@email.com")
            password = st.text_input("🔒 סיסמה", type="password", placeholder="הכנס סיסמה")
            submit = st.form_submit_button("כניסה", use_container_width=True)
            
            if submit:
                if email and password:
                    result = login(email, password)
                    if result['success']:
                        st.session_state.authenticated = True
                        st.session_state.user = result['user']
                        st.success("✅ התחברת בהצלחה!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['message']}")
                else:
                    st.warning("⚠️ נא למלא את כל השדות")
    
    with tab2:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        with st.form("register_form"):
            full_name = st.text_input("👤 שם מלא", placeholder="הכנס שם מלא")
            email_reg = st.text_input("📧 אימייל", placeholder="example@email.com")
            phone = st.text_input("📱 טלפון", placeholder="050-1234567")
            password_reg = st.text_input("🔒 סיסמה", type="password", placeholder="בחר סיסמה חזקה")
            password_confirm = st.text_input("🔒 אימות סיסמה", type="password", placeholder="הכנס סיסמה שוב")
            role = st.selectbox("תפקיד", ["employee", "manager"], 
                               format_func=lambda x: "עובד" if x == "employee" else "מנהל")
            
            submit_reg = st.form_submit_button("הרשמה", use_container_width=True)
            
            if submit_reg:
                if not all([full_name, email_reg, phone, password_reg, password_confirm]):
                    st.warning("⚠️ נא למלא את כל השדות")
                elif password_reg != password_confirm:
                    st.error("❌ הסיסמאות לא תואמות")
                elif len(password_reg) < 6:
                    st.error("❌ הסיסמה חייבת להכיל לפחות 6 תווים")
                else:
                    result = register(email_reg, password_reg, full_name, phone, role)
                    if result['success']:
                        st.success("✅ נרשמת בהצלחה! אפשר להתחבר עכשיו")
                    else:
                        st.error(f"❌ {result['message']}")

# עמוד ראשי לאחר התחברות
else:
    # Sidebar
    with st.sidebar:
        try:
            st.image("assets/logo.png", width=200)
        except:
            st.title("🔨 D&B")
        
        st.markdown(f"### שלום, {st.session_state.user.get('full_name', 'משתמש')}! 👋")
        st.markdown(f"**תפקיד:** {'מנהל' if st.session_state.user.get('role') == 'manager' else 'עובד'}")
        st.markdown("---")
        
        # תפריט ניווט
        if st.session_state.user.get('role') == 'manager':
            st.page_link("pages/1_📊_dashboard_manager.py", label="📊 דשבורד מנהלים")
            st.page_link("pages/3_🏫_schools.py", label="🏫 ניהול בתי ספר")
            st.page_link("pages/4_👥_employees.py", label="👥 ניהול עובדים")
            st.page_link("pages/5_📅_schedule.py", label="📅 ניהול לו״ז")
            st.page_link("pages/6_🔧_equipment.py", label="🔧 ניהול ציוד")
            st.page_link("pages/7_💰_finance.py", label="💰 דוחות כספיים")
        else:
            st.page_link("pages/2_👷_dashboard_employee.py", label="👷 הדשבורד שלי")
            st.page_link("pages/5_📅_schedule.py", label="📅 הלו״ז שלי")
            st.page_link("pages/6_🔧_equipment.py", label="🔧 דיווח ציוד")
        
        st.markdown("---")
        if st.button("🚪 התנתקות", use_container_width=True):
            logout()
            st.rerun()
    
    # תוכן ראשי
    st.title("🔨 ברוכים הבאים ל-Dream & Build")
    
    if st.session_state.user.get('role') == 'manager':
        st.markdown("### 📊 מערכת ניהול סדנאות נגרות למנהלים")
        st.info("👈 בחר דף מהתפריט בצד כדי להתחיל")
        
        # סטטיסטיקות מהירות
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("פעילויות היום", "0", "")
        with col2:
            st.metric("עובדים פעילים", "0", "")
        with col3:
            st.metric("בתי ספר", "0", "")
        with col4:
            st.metric("התראות ציוד", "0", "🔴")
    else:
        st.markdown("### 👷 הדשבורד האישי שלך")
        st.info("👈 בחר דף מהתפריט בצד")
        
        # סטטיסטיקות עובד
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("פעילויות החודש", "0", "")
        with col2:
            st.metric("פעילויות השבוע", "0", "")
        with col3:
            st.metric("בתי ספר", "0", "")
