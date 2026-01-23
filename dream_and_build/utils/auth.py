import streamlit as st
import time

# פונקציית התחברות "פיתוח" - ללא סיסמה
def login_dev(email: str, role: str, full_name: str):
    """התחברות מהירה למטרות בדיקה"""
    
    # סימולציה של טעינה
    time.sleep(0.5)
    
    # יצירת אובייקט משתמש מדמה
    # אנחנו משתמשים באימייל גם כ-ID כדי לשמור על עקביות בבדיקות
    user_data = {
        "id": email,  # מפתח ייחודי לבדיקה
        "email": email,
        "full_name": full_name,
        "role": role,
        "status": "active"
    }
    
    return {
        "success": True,
        "message": f"ברוך הבא, {full_name}",
        "user": user_data
    }

def logout():
    """התנתקות"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()

def check_auth():
    """בדיקת אימות"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.warning("⚠️ נא להתחבר תחילה")
        st.stop()
    
    return st.session_state.user

def require_role(role: str):
    """בדיקת הרשאה"""
    user = check_auth()
    # מנהל יכול לראות הכל, עובד רק את שלו
    if role == 'manager' and user.get('role') != 'manager':
        st.error("🔒 אין לך הרשאה לצפות בדף זה")
        st.stop()
    return user