import streamlit as st
from utils.auth import require_role
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="דשבורד מנהלים", page_icon="📊", layout="wide")
apply_custom_css()

# וידוא הרשאות
user = require_role('manager')

st.title("📊 דשבורד מנהלים")
st.markdown(f"### שלום {user['full_name']}, הנה סקירת המערכת")

# סטטיסטיקות כלליות
col1, col2, col3, col4 = st.columns(4)

try:
    # ספירת פעילויות היום
    today = datetime.now().date()
    activities_today = supabase.table("activities").select("*").eq("date", str(today)).execute()
    
    # ספירת עובדים פעילים
    employees = supabase.table("users").select("*").eq("role", "employee").eq("status", "active").execute()
    
    # ספירת בתי ספר
    schools = supabase.table("schools").select("*").execute()
    
    # התראות ציוד
    equipment_alerts = supabase.table("equipment").select("*").execute()
    low_stock = [item for item in equipment_alerts.data if item.get('quantity_available', 0) <= item.get('min_threshold', 0)]
    
    with col1:
        st.metric("פעילויות היום", len(activities_today.data) if activities_today.data else 0, "")
    
    with col2:
        st.metric("עובדים פעילים", len(employees.data) if employees.data else 0, "")
    
    with col3:
        st.metric("בתי ספר פעילים", len(schools.data) if schools.data else 0, "")
    
    with col4:
        alert_count = len(low_stock)
        st.metric("התראות ציוד", alert_count, "🔴" if alert_count > 0 else "✅")

except Exception as e:
    st.error(f"שגיאה בטעינת נתונים: {str(e)}")
    with col1:
        st.metric("פעילויות היום", "0", "")
    with col2:
        st.metric("עובדים פעילים", "0", "")
    with col3:
        st.metric("בתי ספר פעילים", "0", "")
    with col4:
        st.metric("התראות ציוד", "0", "")

st.markdown("---")

# לו"ז השבוע
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📅 פעילויות השבוע הקרובה")
    try:
        # שליפת פעילויות 7 ימים קדימה
        end_date = (datetime.now() + timedelta(days=7)).date()
        activities = supabase.table("activities") \
            .select("*, schools(name), users(full_name)") \
            .gte("date", str(today)) \
            .lte("date", str(end_date)) \
            .order("date") \
            .execute()
        
        if activities.data and len(activities.data) > 0:
            df = pd.DataFrame(activities.data)
            df['school_name'] = df['schools'].apply(lambda x: x['name'] if x else 'לא ידוע')
            df['employee_name'] = df['users'].apply(lambda x: x['full_name'] if x else 'לא שובץ')
            df['status_he'] = df['status'].map({
                'planned': '🟡 מתוכנן',
                'confirmed': '🟢 מאושר',
                'completed': '✅ הושלם',
                'cancelled': '🔴 בוטל'
            })
            
            display_df = df[['date', 'school_name', 'employee_name', 'time_start', 'time_end', 'status_he']]
            display_df.columns = ['תאריך', 'בית ספר', 'עובד', 'התחלה', 'סיום', 'סטטוס']
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("אין פעילויות מתוכננות לשבוע הקרוב")
    except Exception as e:
        st.warning("טרם נוצרו פעילויות במערכת")

with col_right:
    st.subheader("🚨 התראות חשובות")
    
    # התראות ציוד
    if low_stock:
        st.warning(f"⚠️ {len(low_stock)} פריטי ציוד במלאי נמוך")
        for item in low_stock[:5]:
            st.markdown(f"- **{item.get('name')}**: {item.get('quantity_available')} יח'")
    
    # דיווחי חוסרים מעובדים
    try:
        reports = supabase.table("equipment_reports") \
            .select("*, equipment(name), users(full_name)") \
            .eq("status", "pending") \
            .execute()
        
        if reports.data and len(reports.data) > 0:
            st.error(f"📝 {len(reports.data)} דיווחי חוסרים ממתינים")
            for report in reports.data[:3]:
                st.markdown(f"- {report['equipment']['name']} - {report['users']['full_name']}")
    except:
        pass
    
    # תקציבים מתקרבים לגבול
    try:
        budgets = supabase.table("school_budgets") \
            .select("*, schools(name)") \
            .execute()
        
        if budgets.data:
            for budget in budgets.data:
                remaining = budget['budget_amount'] - budget['spent_amount']
                if remaining <= 1000:
                    st.warning(f"💰 {budget['schools']['name']}: נותרו {remaining}₪")
    except:
        pass

st.markdown("---")

# גרפים
col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    st.subheader("📈 פעילויות לפי חודש")
    try:
        # שליפת פעילויות 6 חודשים אחורה
        six_months_ago = (datetime.now() - timedelta(days=180)).date()
        activities_history = supabase.table("activities") \
            .select("date") \
            .gte("date", str(six_months_ago)) \
            .execute()
        
        if activities_history.data:
            df_history = pd.DataFrame(activities_history.data)
            df_history['date'] = pd.to_datetime(df_history['date'])
            df_history['month'] = df_history['date'].dt.to_period('M').astype(str)
            monthly_count = df_history.groupby('month').size().reset_index(name='count')
            
            fig = px.line(monthly_count, x='month', y='count', 
                         title='מספר פעילויות לפי חודש',
                         labels={'month': 'חודש', 'count': 'מספר פעילויות'})
            fig.update_traces(line_color='#FF8C00')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("אין מספיק נתונים להצגת גרף")
    except Exception as e:
        st.info("טרם נאספו נתונים היסטוריים")

with col_graph2:
    st.subheader("👥 עובדים לפי מספר פעילויות")
    try:
        activities_by_employee = supabase.table("activities") \
            .select("employee_id, users(full_name)") \
            .execute()
        
        if activities_by_employee.data:
            df_emp = pd.DataFrame(activities_by_employee.data)
            df_emp['employee_name'] = df_emp['users'].apply(lambda x: x['full_name'] if x else 'לא ידוע')
            emp_count = df_emp.groupby('employee_name').size().reset_index(name='count')
            emp_count = emp_count.sort_values('count', ascending=False)
            
            fig2 = px.bar(emp_count, x='employee_name', y='count',
                         title='מספר פעילויות לכל עובד',
                         labels={'employee_name': 'עובד', 'count': 'מספר פעילויות'})
            fig2.update_traces(marker_color='#FF8C00')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("אין מספיק נתונים להצגת גרף")
    except Exception as e:
        st.info("טרם נאספו נתונים")
