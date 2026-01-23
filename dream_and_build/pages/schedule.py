import streamlit as st
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
from utils.nav import render_sidebar
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="ניהול לו״ז", page_icon="📅", layout="wide")
apply_custom_css()
render_sidebar() # חובה!

st.title("📅 ניהול לוח זמנים")

tab1, tab2 = st.tabs(["🗓️ צפייה ביומן", "➕ הוספת פעילות חדשה"])

with tab1:
    st.subheader("פעילויות קרובות")
    try:
        response = supabase.table("activities").select("*, schools(name), users(full_name)").order("date").execute()
        if response.data:
            data = []
            for item in response.data:
                data.append({
                    "תאריך": item['date'],
                    "שעות": f"{item['time_start']} - {item['time_end']}",
                    "בית ספר": item['schools']['name'] if item.get('schools') else '---',
                    "עובד": item['users']['full_name'] if item.get('users') else '--- לא שובץ ---',
                    "סטטוס": item['status']
                })
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.info("אין פעילויות")
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")

with tab2:
    st.subheader("שיבוץ פעילות חדשה")
    with st.form("add_activity_form"):
        col1, col2 = st.columns(2)
        
        # שליפת נתונים
        schools_resp = supabase.table("schools").select("id, name").eq("status", "active").execute()
        school_options = {s['name']: s['id'] for s in schools_resp.data} if schools_resp.data else {}
        
        employees_resp = supabase.table("users").select("id, full_name").eq("role", "employee").execute()
        employee_options = {e['full_name']: e['id'] for e in employees_resp.data} if employees_resp.data else {}

        with col1:
            selected_school = st.selectbox("🏫 בית ספר", list(school_options.keys()))
            date = st.date_input("📅 תאריך")
            
        with col2:
            selected_employee = st.selectbox("👷 עובד", ["--- ללא שיבוץ ---"] + list(employee_options.keys()))
            start = st.time_input("התחלה", value=datetime.strptime("08:00", "%H:%M").time())
            end = st.time_input("סיום", value=datetime.strptime("13:00", "%H:%M").time())

        if st.form_submit_button("צור פעילות"):
            try:
                emp_id = employee_options[selected_employee] if selected_employee != "--- ללא שיבוץ ---" else None
                supabase.table("activities").insert({
                    "school_id": school_options[selected_school],
                    "employee_id": emp_id,
                    "date": str(date),
                    "time_start": str(start),
                    "time_end": str(end),
                    "status": "planned"
                }).execute()
                st.success("הפעילות נוצרה!")
                st.rerun()
            except Exception as e:
                st.error(str(e))