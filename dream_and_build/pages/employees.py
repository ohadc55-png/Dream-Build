import streamlit as st
from utils.auth import require_role
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ניהול עובדים", page_icon="👥", layout="wide")
apply_custom_css()

# וידוא הרשאות מנהל
user = require_role('manager')

st.title("👥 ניהול עובדים")

# טאבים
tab1, tab2, tab3 = st.tabs(["📋 רשימת עובדים", "➕ הוספת עובד", "📊 ביצועים"])

# טאב 1: רשימת עובדים
with tab1:
    st.subheader("רשימת העובדים")
    
    # פילטרים
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        status_filter = st.selectbox("סטטוס", ["הכל", "פעיל", "לא פעיל"])
    with col_filter2:
        search = st.text_input("🔍 חיפוש עובד", placeholder="הקלד שם...")
    
    try:
        # שליפת עובדים
        query = supabase.table("users").select("*").eq("role", "employee").order("full_name")
        
        if status_filter == "פעיל":
            query = query.eq("status", "active")
        elif status_filter == "לא פעיל":
            query = query.eq("status", "inactive")
        
        employees = query.execute()
        
        if employees.data and len(employees.data) > 0:
            df = pd.DataFrame(employees.data)
            
            # פילטר חיפוש
            if search:
                df = df[df['full_name'].str.contains(search, case=False, na=False)]
            
            if len(df) > 0:
                df_display = df[['full_name', 'email', 'phone', 'status', 'hire_date']].copy()
                df_display.columns = ['שם מלא', 'אימייל', 'טלפון', 'סטטוס', 'תאריך העסקה']
                df_display['סטטוס'] = df_display['סטטוס'].map({'active': '✅ פעיל', 'inactive': '❌ לא פעיל'})
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                # עריכת עובד
                st.subheader("✏️ עריכת עובד")
                employee_names = df['full_name'].tolist()
                selected_name = st.selectbox("בחר עובד לעריכה", employee_names)
                
                if selected_name:
                    selected_emp = df[df['full_name'] == selected_name].iloc[0]
                    
                    with st.form("edit_employee_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_name = st.text_input("שם מלא", value=selected_emp['full_name'])
                            edit_phone = st.text_input("טלפון", value=selected_emp.get('phone', '') or '')
                            edit_hourly = st.number_input("שכר לשעה (₪)", value=float(selected_emp.get('hourly_rate') or 0), min_value=0.0)
                        
                        with col2:
                            edit_email = st.text_input("אימייל", value=selected_emp['email'], disabled=True)
                            edit_status = st.selectbox("סטטוס", ['active', 'inactive'], 
                                                      index=0 if selected_emp['status'] == 'active' else 1,
                                                      format_func=lambda x: 'פעיל' if x == 'active' else 'לא פעיל')
                            edit_daily = st.number_input("שכר ליום (₪)", value=float(selected_emp.get('daily_rate') or 0), min_value=0.0)
                        
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            update_btn = st.form_submit_button("💾 שמור שינויים", use_container_width=True)
                        
                        if update_btn:
                            try:
                                update_data = {
                                    "full_name": edit_name,
                                    "phone": edit_phone if edit_phone else None,
                                    "status": edit_status,
                                    "hourly_rate": edit_hourly if edit_hourly > 0 else None,
                                    "daily_rate": edit_daily if edit_daily > 0 else None
                                }
                                
                                supabase.table("users").update(update_data).eq("id", selected_emp['id']).execute()
                                st.success("✅ העובד עודכן בהצלחה!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ שגיאה בעדכון: {str(e)}")
            else:
                st.info("לא נמצאו עובדים התואמים לחיפוש")
        else:
            st.info("אין עובדים במערכת")
    
    except Exception as e:
        st.error(f"שגיאה בטעינת עובדים: {str(e)}")

# טאב 2: הוספת עובד (למעשה זו הרשמה)
with tab2:
    st.subheader("➕ הוספת עובד חדש")
    st.info("💡 עובדים חדשים יכולים להירשם דרך מסך ההרשמה הראשי, או שתוכל להוסיף אותם כאן")
    
    with st.form("add_employee_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("שם מלא *")
            new_email = st.text_input("אימייל *")
            new_password = st.text_input("סיסמה *", type="password", help="לפחות 6 תווים")
        
        with col2:
            new_phone = st.text_input("טלפון")
            new_hourly = st.number_input("שכר לשעה (₪)", min_value=0.0, value=0.0)
            new_daily = st.number_input("שכר ליום (₪)", min_value=0.0, value=0.0)
        
        submit = st.form_submit_button("➕ הוסף עובד", use_container_width=True)
        
        if submit:
            if not all([new_name, new_email, new_password]):
                st.error("❌ נא למלא את שדות החובה")
            elif len(new_password) < 6:
                st.error("❌ הסיסמה חייבת להכיל לפחות 6 תווים")
            else:
                try:
                    # יצירת משתמש ב-Auth
                    auth_response = supabase.auth.sign_up({
                        "email": new_email,
                        "password": new_password
                    })
                    
                    if auth_response.user:
                        user_data = {
                            "id": auth_response.user.id,
                            "email": new_email,
                            "full_name": new_name,
                            "phone": new_phone if new_phone else None,
                            "role": "employee",
                            "status": "active",
                            "hourly_rate": new_hourly if new_hourly > 0 else None,
                            "daily_rate": new_daily if new_daily > 0 else None
                        }
                        
                        supabase.table("users").insert(user_data).execute()
                        st.success(f"✅ העובד '{new_name}' נוסף בהצלחה!")
                        st.rerun()
                    else:
                        st.error("❌ שגיאה ביצירת המשתמש")
                except Exception as e:
                    st.error(f"❌ שגיאה: {str(e)}")

# טאב 3: ביצועים
with tab3:
    st.subheader("📊 ביצועי עובדים")
    
    try:
        # שליפת כל הפעילויות עם פרטי עובדים
        activities = supabase.table("activities") \
            .select("*, users(full_name)") \
            .execute()
        
        if activities.data and len(activities.data) > 0:
            df = pd.DataFrame(activities.data)
            df['employee_name'] = df['users'].apply(lambda x: x['full_name'] if x else 'לא ידוע')
            
            # סטטיסטיקות לכל עובד
            stats = df.groupby('employee_name').agg({
                'id': 'count',
                'status': lambda x: (x == 'completed').sum()
            }).reset_index()
            stats.columns = ['עובד', 'סה"כ פעילויות', 'הושלמו']
            stats['אחוז השלמה'] = (stats['הושלמו'] / stats['סה"כ פעילויות'] * 100).round(1).astype(str) + '%'
            
            st.dataframe(stats, use_container_width=True, hide_index=True)
            
            # גרף
            import plotly.express as px
            fig = px.bar(stats, x='עובד', y='סה"כ פעילויות', 
                        title='מספר פעילויות לכל עובד',
                        color='הושלמו',
                        color_continuous_scale='Oranges')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("אין מספיק נתונים להצגת ביצועים")
    
    except Exception as e:
        st.info("טרם נאספו נתונים")
