import streamlit as st
from utils.auth import logout

def render_sidebar():
    """פונקציה שמציירת את הסרגל הצידי - יש לקרוא לה מכל דף"""
    
    with st.sidebar:
        st.image("https://i.postimg.cc/SKL4H4GV/לוגו_D_B.png", use_container_width=True)
        
        # וידוא שיש משתמש מחובר לפני שמציגים פרטים
        if st.session_state.get('authenticated') and st.session_state.get('user'):
            user = st.session_state.user
            role_hebrew = 'מנהל' if user.get('role') == 'manager' else 'עובד'
            
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                <div style='font-size: 0.9rem; color: #aaa;'>שלום,</div>
                <div style='font-size: 1.2rem; font-weight: bold; color: white;'>{user.get('full_name', 'אורח')}</div>
                <div style='font-size: 0.9rem; color: #FF8C00;'>{role_hebrew}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📌 תפריט ראשי")
            
            # --- הקישורים בעברית ---
            # שים לב: אלו השמות שיוצגו למשתמש, והם מפנים לקבצים באנגלית
            if user.get('role') == 'manager':
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