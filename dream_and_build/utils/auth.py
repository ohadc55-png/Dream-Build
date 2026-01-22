import streamlit as st
from utils.supabase_client import supabase

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
                "role": role
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
        return {
            "success": False,
            "message": f"שגיאה: {str(e)}"
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
        return {
            "success": False,
            "message": f"שגיאה בהתחברות: {str(e)}"
        }

def logout():
    """התנתקות משתמש"""
    try:
        supabase.auth.sign_out()
        st.session_state.authenticated = False
        st.session_state.user = None
        return True
    except:
        return False

def check_auth():
    """בדיקת אימות"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.warning("⚠️ נא להתחבר תחילה")
        st.stop()
    
    return st.session_state.user

def require_role(role: str):
    """בדיקת הרשאה לפי תפקיד"""
    user = check_auth()
    if user.get('role') != role:
        st.error("❌ אין לך הרשאה לצפות בדף זה")
        st.stop()
    return user
