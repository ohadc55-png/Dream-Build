import streamlit as st
from utils.auth import require_role
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
from utils.nav import render_sidebar  # <-- התיקון
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="דשבורד מנהלים", page_icon="📊", layout="wide")
apply_custom_css()
render_sidebar()  # <-- התיקון: הפעלת הסיידבר

# וידוא הרשאות
user = require_role('manager')

st.title("📊 דשבורד מנהלים")

# סטטיסטיקות כלליות
col1, col2, col3, col4 = st.columns(4)

try:
    today = datetime.now().date()
    activities_today = supabase.table("activities").select("*").eq("date", str(today)).execute()
    employees = supabase.table("users").select("*").eq("role", "employee").eq("status", "active").execute()
    schools = supabase.table("schools").select("*").execute()
    equipment_alerts = supabase.table("equipment").select("*").execute()
    low_stock = [item for item in equipment_alerts.data if item.get('quantity_available', 0) <= item.get('min_threshold', 0)]
    
    with col1:
        st.metric("פעילויות היום", len(activities_today.data) if activities_today.data else 0)
    with col2:
        st.metric("עובדים פעילים", len(employees.data) if employees.data else 0)
    with col3:
        st.metric("בתי ספר פעילים", len(schools.data) if schools.data else 0)
    with col4:
        alert_count = len(low_stock)
        st.metric("התראות ציוד", alert_count, "🔴" if alert_count > 0 else "✅")

except Exception as e:
    st.error(f"שגיאה בטעינת נתונים: {str(e)}")

st.markdown("---")

# לו"ז השבוע (הוחזר מהקוד המקורי)
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📅 פעילויות השבוע הקרובה")
    try:
        end_date = (datetime.now() + timedelta(days=7)).date()
        activities = supabase.table("activities") \
            .select("*, schools(name), users(full_name)") \
            .gte("date", str(today)) \
            .lte("date", str(end_date)) \
            .order("date") \
            .execute()
        
        if activities.data:
            df = pd.DataFrame(activities.data)
            df['school_name'] = df['schools'].apply(lambda x: x['name'] if x else 'לא ידוע')
            df['employee_name'] = df['users'].apply(lambda x: x['full_name'] if x else 'לא שובץ')
            df['status_he'] = df['status'].map({
                'planned': '🟡 מתוכנן', 'confirmed': '🟢 מאושר',
                'completed': '✅ הושלם', 'cancelled': '🔴 בוטל'
            })
            
            st.dataframe(
                df[['date', 'school_name', 'employee_name', 'time_start', 'time_end', 'status_he']], 
                use_container_width=True, hide_index=True
            )
        else:
            st.info("אין פעילויות מתוכננות לשבוע הקרוב")
    except Exception as e:
        st.warning("טרם נוצרו פעילויות במערכת")

with col_right:
    st.subheader("🚨 התראות חשובות")
    if 'low_stock' in locals() and low_stock:
        st.warning(f"⚠️ {len(low_stock)} פריטי ציוד במלאי נמוך")
        for item in low_stock[:3]:
            st.markdown(f"- **{item.get('name')}**: {item.get('quantity_available')} יח'")
    else:
        st.success("אין התראות דחופות")

st.markdown("---")

# גרפים (הוחזרו מהקוד המקורי)
col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    st.subheader("📈 פעילויות לפי חודש")
    try:
        six_months_ago = (datetime.now() - timedelta(days=180)).date()
        activities_history = supabase.table("activities").select("date").gte("date", str(six_months_ago)).execute()
        
        if activities_history.data:
            df_history = pd.DataFrame(activities_history.data)
            df_history['date'] = pd.to_datetime(df_history['date'])
            df_history['month'] = df_history['date'].dt.to_period('M').astype(str)
            monthly_count = df_history.groupby('month').size().reset_index(name='count')
            
            fig = px.line(monthly_count, x='month', y='count', labels={'month': 'חודש', 'count': 'מספר פעילויות'})
            fig.update_traces(line_color='#FF8C00')
            st.plotly_chart(fig, use_container_width=True)
    except:
        st.info("אין מספיק נתונים לגרף")

with col_graph2:
    st.subheader("👥 עובדים לפי מספר פעילויות")
    try:
        activities_by_employee = supabase.table("activities").select("employee_id, users(full_name)").execute()
        if activities_by_employee.data:
            df_emp = pd.DataFrame(activities_by_employee.data)
            df_emp['employee_name'] = df_emp['users'].apply(lambda x: x['full_name'] if x else 'לא ידוע')
            emp_count = df_emp.groupby('employee_name').size().reset_index(name='count').sort_values('count', ascending=False)
            
            fig2 = px.bar(emp_count, x='employee_name', y='count', labels={'employee_name': 'עובד', 'count': 'פעילויות'})
            fig2.update_traces(marker_color='#FF8C00')
            st.plotly_chart(fig2, use_container_width=True)
    except:
        st.info("אין מספיק נתונים לגרף")