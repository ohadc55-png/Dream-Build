import streamlit as st
from utils.auth import logout

def render_sidebar():
    """סרגל צידי מקצועי עם ניווט חכם"""
    
    with st.sidebar:
        # === לוגו ===
        st.markdown("""
        <div style='text-align: center; padding: 1.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 1.5rem;'>
            <div style='font-size: 2.5rem; margin-bottom: 0.5rem;'>🔨</div>
            <div style='font-size: 1.4rem; font-weight: 800; color: white;'>Dream & <span style='color: #FF8C00;'>Build</span></div>
            <div style='font-size: 0.75rem; color: rgba(255,255,255,0.5); margin-top: 0.25rem;'>מערכת ניהול סדנאות</div>
        </div>
        """, unsafe_allow_html=True)
        
        # === פרטי משתמש ===
        if st.session_state.get('authenticated') and st.session_state.get('user'):
            user = st.session_state.user
            role_hebrew = '👔 מנהל' if user.get('role') == 'manager' else '👷 עובד'
            role_color = '#FF8C00' if user.get('role') == 'manager' else '#10B981'
            
            # כרטיס משתמש
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, rgba(255,140,0,0.15) 0%, rgba(255,140,0,0.05) 100%);
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 1.5rem;
                border: 1px solid rgba(255,140,0,0.2);
            '>
                <div style='display: flex; align-items: center; gap: 12px;'>
                    <div style='
                        width: 45px;
                        height: 45px;
                        background: linear-gradient(135deg, #FF8C00, #FFA500);
                        border-radius: 10px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 1.2rem;
                        font-weight: 700;
                        color: white;
                    '>
                        {user.get('full_name', 'א')[0]}
                    </div>
                    <div>
                        <div style='font-weight: 600; font-size: 0.95rem; color: white;'>{user.get('full_name', 'משתמש')}</div>
                        <div style='font-size: 0.8rem; color: {role_color};'>{role_hebrew}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # === תפריט ניווט ===
            st.markdown("""
            <div style='font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,0.4); margin-bottom: 0.75rem; padding-right: 0.5rem;'>
                תפריט ראשי
            </div>
            """, unsafe_allow_html=True)
            
            # תפריט למנהל
            if user.get('role') == 'manager':
                menu_items = [
                    ("pages/dashboard_manager.py", "📊", "דשבורד", "סקירה כללית"),
                    ("pages/schools.py", "🏫", "בתי ספר", "ניהול לקוחות"),
                    ("pages/employees.py", "👥", "עובדים", "צוות ושכר"),
                    ("pages/schedule.py", "📅", "לו״ז", "פעילויות ושיבוצים"),
                    ("pages/equipment.py", "🔧", "ציוד", "מלאי וחומרים"),
                    ("pages/finance.py", "💰", "כספים", "דוחות ותקציב"),
                ]
            else:
                # תפריט לעובד
                menu_items = [
                    ("pages/dashboard_employee.py", "👷", "הדשבורד שלי", "סקירה אישית"),
                    ("pages/schedule.py", "📅", "הלו״ז שלי", "פעילויות"),
                    ("pages/equipment.py", "🔧", "דיווח ציוד", "חוסרים"),
                ]
            
            # יצירת קישורי ניווט
            for page, icon, label, subtitle in menu_items:
                st.page_link(page, label=f"{icon}  {label}", help=subtitle)
            
            # === כפתור יציאה ===
            st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div style='font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,0.4); margin-bottom: 0.75rem; padding-right: 0.5rem;'>
                חשבון
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 יציאה מהמערכת", use_container_width=True):
                logout()
            
            # === Footer ===
            st.markdown("""
            <div style='
                position: absolute;
                bottom: 1rem;
                right: 1rem;
                left: 1rem;
                text-align: center;
                font-size: 0.7rem;
                color: rgba(255,255,255,0.3);
            '>
                © 2025 Dream & Build
            </div>
            """, unsafe_allow_html=True)


def get_current_page():
    """קבלת הדף הנוכחי"""
    return st.session_state.get('current_page', 'dashboard')
