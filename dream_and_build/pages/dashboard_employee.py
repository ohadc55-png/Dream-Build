import streamlit as st
from utils.auth import require_role
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
from utils.nav import render_sidebar  # <-- התיקון
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="הדשבורד שלי", page_icon="👷", layout="wide")
apply_custom_css()
render_sidebar()  # <-- התיקון

user = require_role('employee')
st.title("👷 הדשבורד האישי שלי")

# סטטיסטיקות אישיות
col1, col2, col3 = st.columns(3)
try:
    today = datetime.now().date()
    month_start = today.replace(day=1)
    
    # שאילתות לספירה
    activities_month = supabase.table("activities").select("id").eq("employee_id", user['id']).gte("date", str(month_start)).execute()
    
    # חישוב בתי ספר ייחודיים
    all_activities = supabase.table("activities").select("school_id").eq("employee_id", user['id']).execute()
    unique_schools = len(set([a['school_id'] for a in all_activities.data])) if all_activities.data else 0
    
    with col1: st.metric("פעילויות החודש", len(activities_month.data) if activities_month.data else 0)
    with col2: st.metric("בתי ספר שעבדתי בהם", unique_schools)
    with col3: st.metric("פעילויות היום", "0") # אפשר לשפר עם שאילתה נוספת
except:
    pass

st.markdown("---")

# הלו"ז שלי + כפתור אישור ביצוע (הלוגיקה החשובה)
col_schedule, col_pending = st.columns([2, 1])

with col_schedule:
    st.subheader("📅 הלו״ז שלי")
    try:
        end_date = (datetime.now() + timedelta(days=7)).date()
        my_activities = supabase.table("activities") \
            .select("*, schools(name, address)") \
            .eq("employee_id", user['id']) \
            .gte("date", str(today)) \
            .lte("date", str(end_date)) \
            .order("date") \
            .execute()
        
        if my_activities.data:
            for activity in my_activities.data:
                school_name = activity['schools']['name'] if activity['schools'] else 'לא ידוע'
                status_emoji = {'planned': '🟡', 'confirmed': '🟢', 'completed': '✅'}.get(activity['status'], '⚪')
                
                with st.expander(f"{status_emoji} {activity['date']} - {school_name}"):
                    st.markdown(f"**שעות:** {activity['time_start']} - {activity['time_end']}")
                    if activity['schools'].get('address'):
                        st.markdown(f"**כתובת:** {activity['schools']['address']}")
                    
                    # --- כפתור אישור ביצוע (קריטי) ---
                    if activity['status'] in ['planned', 'confirmed'] and not activity.get('confirmed_by_employee'):
                        if st.button(f"✅ אשר ביצוע", key=f"confirm_{activity['id']}"):
                            supabase.table("activities").update({
                                "confirmed_by_employee": True,
                                "status": "completed"
                            }).eq("id", activity['id']).execute()
                            st.success("הפעילות אושרה!")
                            st.rerun()
                    elif activity.get('confirmed_by_employee'):
                        st.success("✅ אושר על ידך")
        else:
            st.info("אין פעילויות קרובות")
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")

with col_pending:
    st.subheader("⏳ ממתין לאישור")
    # כאן הייתה לוגיקה פשוטה להצגת פעילויות עבר שלא אושרו
    try:
        pending = supabase.table("activities").select("*").eq("employee_id", user['id']).eq("confirmed_by_employee", False).lte("date", str(today)).execute()
        if pending.data:
            st.warning(f"יש {len(pending.data)} פעילויות שלא אישרת!")
        else:
            st.success("הכל מאושר")
    except:
        pass