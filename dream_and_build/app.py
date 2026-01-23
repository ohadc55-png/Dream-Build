import streamlit as st
from utils.auth import login_dev, logout
from utils.styling import apply_custom_css

# --- הגדרות עמוד (חייב להיות ראשון) ---
st.set_page_config(
    page_title="Dream & Build",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- החלת העיצוב ---
apply_custom_css()

# --- אתחול Session State ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

# --- מסך כניסה (אם לא מחובר) ---
if not st.session_state.authenticated:
    
    # עמודות למרכוז הלוגו והטופס
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        # הצגת לוגו
        st.image("https://i.postimg.cc/SKL4H4GV/לוגו_D_B.png", use_container_width=True)
        
        st.markdown("<h3 style='text-align: center;'>כניסה למערכת</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>מצב בדיקה - ללא סיסמה</p>", unsafe_allow_html=True)
        
        # טופס כניסה מעוצב
        with st.form("login_form"):
            full_name = st.text_input("👤 שם מלא", placeholder="לדוגמה: ישראל ישראלי")
            email = st.text_input("📧 אימייל", placeholder="your@email.com")
            
            # בחירת תפקיד בסטייל
            role_display = st.radio("בחר תפקיד לכניסה:", 
                                  ["מנהל מערכת 🛠️", "עובד צוות 👷"], 
                                  horizontal=True)
            
            # המרת התצוגה לקוד
            role = "manager" if "מנהל" in role_display else "employee"
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("🚀 כניסה למערכת")
            
            if submit:
                if email and full_name:
                    result = login_dev(email, role, full_name)
                    st.session_state.authenticated = True
                    st.session_state.user = result['user']
                    st.toast(result['message'], icon="✅")
                    st.rerun()
                else:
                    st.warning("נא למלא שם ואימייל")

# --- האפליקציה עצמה (אחרי התחברות) ---
else:
    # --- Sidebar ---
    with st.sidebar:
        st.image("https://i.postimg.cc/SKL4H4GV/לוגו_D_B.png", use_container_width=True)
        
        user = st.session_state.user
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 10px 0;'>
            <div style='font-size: 0.9rem; color: #aaa;'>שלום,</div>
            <div style='font-size: 1.2rem; font-weight: bold; color: white;'>{user['full_name']}</div>
            <div style='font-size: 0.9rem; color: #FF8C00;'>{role_display if 'role_display' in locals() else ('מנהל' if user['role']=='manager' else 'עובד')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📌 תפריט ראשי")
        
        # תפריט מותאם אישית לפי תפקיד
        if user['role'] == 'manager':
            st.page_link("pages/dashboard_manager.py", label="דשבורד מנהלים", icon="📊")
            st.page_link("pages/schools.py", label="ניהול בתי ספר", icon="🏫")
            st.page_link("pages/employees.py", label="ניהול עובדים", icon="👥")
            st.page_link("pages/schedule.py", label="ניהול לו״ז", icon="📅")
            st.page_link("pages/equipment.py", label="ניהול ציוד", icon="🔧")
            st.page_link("pages/finance.py", label="דוחות כספיים", icon="💰")
        else:
            st.page_link("pages/dashboard_employee.py", label="הדשבורד שלי", icon="👷")
            st.page_link("pages/schedule.py", label="הלו״ז שלי", icon="📅")
            st.page_link("pages/equipment.py", label="דיווח ציוד", icon="🔧")
            
        st.markdown("---")
        if st.button("יציאה מהמערכת 🚪"):
            logout()

    # --- תוכן ראשי ---
    st.title("ברוכים הבאים ל-Dream & Build")
    st.markdown("בחר בתפריט בצד כדי להתחיל לעבוד.")
    
    # הצגה ויזואלית יפה לדף הבית הריק
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"אתה מחובר כעת כ**{user['full_name']}** ({'מנהל' if user['role']=='manager' else 'עובד'}).")
    
    with col2:
        st.markdown("### 🚀 מה חדש?")
        st.caption("המערכת בגרסת בדיקה. כל הנתונים נשמרים, אך הכניסה ללא סיסמה.")