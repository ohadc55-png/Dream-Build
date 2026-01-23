import streamlit as st
from utils.auth import require_role
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
from utils.nav import render_sidebar
import pandas as pd

st.set_page_config(page_title="ניהול עובדים", page_icon="👥", layout="wide")
apply_custom_css()
render_sidebar()

# וידוא הרשאות מנהל
user = require_role('manager')

st.title("👥 ניהול צוות עובדים")

tab1, tab2 = st.tabs(["📋 רשימת עובדים", "➕ הוספת עובד חדש"])

# --- טאב 1: רשימת עובדים ---
with tab1:
    st.subheader("מצבת כוח אדם")
    
    # פילטרים
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        search = st.text_input("🔍 חיפוש עובד", placeholder="שם או אימייל...")
    
    try:
        # שליפת נתונים
        query = supabase.table("users").select("*").eq("role", "employee").order("full_name")
        if search:
            query = query.ilike("full_name", f"%{search}%")
            
        employees = query.execute()
        
        if employees.data:
            df = pd.DataFrame(employees.data)
            
            # עיצוב הטבלה
            display_df = df[['full_name', 'email', 'phone', 'status']].copy()
            display_df.columns = ['שם מלא', 'אימייל', 'טלפון', 'סטטוס']
            
            # הצגת טבלה אינטראקטיבית
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "סטטוס": st.column_config.SelectboxColumn(
                        "סטטוס",
                        options=["active", "inactive"],
                        required=True
                    )
                }
            )
            
            # סטטיסטיקה מהירה
            st.caption(f"סה״כ עובדים רשומים: {len(df)}")
            
        else:
            st.info("לא נמצאו עובדים במערכת.")
            
    except Exception as e:
        st.error(f"שגיאה בטעינת נתונים: {str(e)}")

# --- טאב 2: הוספת עובד ---
with tab2:
    st.subheader("רישום עובד חדש למערכת")
    
    with st.form("add_employee_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("שם מלא *")
            new_phone = st.text_input("טלפון")
        with col2:
            new_email = st.text_input("אימייל *")
            new_password = st.text_input("סיסמה ראשונית *", type="password")
            
        st.info("ℹ️ העובד יוכל לשנות את הסיסמה בכניסה הראשונה (בפיתוח)")
        
        submit = st.form_submit_button("➕ הוסף עובד", use_container_width=True)
        
        if submit:
            if new_name and new_email and new_password:
                try:
                    # יצירת משתמש (בסימולציה אנחנו מכניסים ישר לטבלה)
                    user_data = {
                        "email": new_email,
                        "full_name": new_name,
                        "phone": new_phone,
                        "role": "employee",
                        "status": "active"
                        # הערה: במערכת אמיתית יוצרים קודם ב-Auth
                    }
                    
                    supabase.table("users").insert(user_data).execute()
                    st.success(f"העובד {new_name} נוסף בהצלחה!")
                    st.rerun()
                except Exception as e:
                    st.error(f"שגיאה בהוספה: {str(e)}")
            else:
                st.warning("נא למלא שדות חובה (שם, אימייל, סיסמה)")