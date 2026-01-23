import streamlit as st
from utils.supabase_client import supabase
import secrets
import string

def register(email: str, password: str, full_name: str, phone: str, role: str):
    """רישום משתמש חדש"""
    try:
        # יצירת משתמש ב-Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if auth_response.user:
            # הוספת פרטים נוספים לטבלת users
            user_data = {
                "id": auth_response.user.id,
                "email": email,
                "full_name": full_name,
                "phone": phone,
                "role": role,
                "status": "active"
            }
            
            supabase.table("users").insert(user_data).execute()
            
            return {
                "success": True,
                "message": "נרשמת בהצלחה!",
                "user": user_data
            }
        else:
            return {
                "success": False,
                "message": "שגיאה ביצירת המשתמש"
            }
    except Exception as e:
        error_msg = str(e)
        if "duplicate" in error_msg.lower():
            return {"success": False, "message": "משתמש עם אימייל זה כבר קיים"}
        elif "rate" in error_msg.lower():
            return {"success": False, "message": "נסיונות רבים מדי. נסה שוב בעוד דקה"}
        return {
            "success": False,
            "message": f"שגיאה: {error_msg}"
        }


def login(email: str, password: str):
    """התחברות משתמש"""
    try:
        # התחברות דרך Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if auth_response.user:
            # שליפת פרטי המשתמש מהטבלה
            user_response = supabase.table("users").select("*").eq("id", auth_response.user.id).execute()
            
            if user_response.data and len(user_response.data) > 0:
                user_data = user_response.data[0]
                return {
                    "success": True,
                    "message": "התחברת בהצלחה!",
                    "user": user_data
                }
            else:
                return {
                    "success": False,
                    "message": "לא נמצאו פרטי משתמש"
                }
        else:
            return {
                "success": False,
                "message": "אימייל או סיסמה שגויים"
            }
    except Exception as e:
        error_msg = str(e)
        if "Invalid login" in error_msg:
            return {"success": False, "message": "אימייל או סיסמה שגויים"}
        elif "Email not confirmed" in error_msg:
            return {"success": False, "message": "יש לאשר את האימייל לפני ההתחברות"}
        return {
            "success": False,
            "message": f"שגיאה בהתחברות: {error_msg}"
        }


def logout():
    """התנתקות משתמש"""
    try:
        supabase.auth.sign_out()
    except:
        pass
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()


def check_auth():
    """בדיקת אימות - מחזיר את המשתמש או עוצר"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.warning("⚠️ נא להתחבר תחילה")
        st.stop()
    
    return st.session_state.user


def require_role(role: str):
    """בדיקת הרשאה לפי תפקיד"""
    user = check_auth()
    
    # מנהל יכול לגשת לכל דף
    if user.get('role') == 'manager':
        return user
    
    # עובד יכול לגשת רק לדפים של עובד
    if role == 'manager' and user.get('role') != 'manager':
        st.error("🔒 אין לך הרשאה לצפות בדף זה")
        st.stop()
    
    return user


def get_current_user():
    """קבלת המשתמש הנוכחי ללא עצירה"""
    if st.session_state.get('authenticated'):
        return st.session_state.get('user')
    return None


def create_employee_by_manager(email: str, full_name: str, phone: str = None, hourly_rate: float = 0.0, daily_rate: float = 0.0):
    """יצירת עובד חדש על ידי מנהל - ללא צורך בהרשמה עצמאית של העובד"""
    try:
        # יצירת סיסמה זמנית אקראית
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        # יצירת משתמש ב-Supabase Auth
        # הערה: אם Supabase מוגדר לדרוש אישור אימייל, יש להגדיר auto-confirm ב-Supabase Dashboard
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": temp_password
        })
        
        if auth_response.user:
            # הוספת פרטים נוספים לטבלת users
            user_data = {
                "id": auth_response.user.id,
                "email": email,
                "full_name": full_name,
                "phone": phone or None,
                "role": "employee",
                "status": "active",
                "hourly_rate": hourly_rate,
                "daily_rate": daily_rate
            }
            
            supabase.table("users").insert(user_data).execute()
            
            return {
                "success": True,
                "message": f"העובד '{full_name}' נוסף בהצלחה!",
                "temp_password": temp_password,
                "user": user_data
            }
        else:
            return {
                "success": False,
                "message": "שגיאה ביצירת המשתמש"
            }
    except Exception as e:
        error_msg = str(e)
        if "duplicate" in error_msg.lower() or "already registered" in error_msg.lower():
            return {"success": False, "message": "עובד עם אימייל זה כבר קיים במערכת"}
        elif "rate" in error_msg.lower():
            return {"success": False, "message": "נסיונות רבים מדי. נסה שוב בעוד דקה"}
        return {
            "success": False,
            "message": f"שגיאה: {error_msg}"
        }
