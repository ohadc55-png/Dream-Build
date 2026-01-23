import streamlit as st
from utils.auth import require_role
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="הדשבורד שלי", page_icon="👷", layout="wide")
apply_custom_css()

# וידוא הרשאות
user = require_role('employee')

st.title("👷 הדשבורד האישי שלי")
st.markdown(f"### שלום {user['full_name']}, הנה סיכום הפעילות שלך")

# סטטיסטיקות אישיות
col1, col2, col3 = st.columns(3)

try:
    # פעילויות החודש
    today = datetime.now().date()
    month_start = today.replace(day=1)
    
    activities_month = supabase.table("activities") \
        .select("*") \
        .eq("employee_id", user['id']) \
        .gte("date", str(month_start)) \
        .execute()
    
    # פעילויות השבוע
    week_start = today - timedelta(days=today.weekday())
    activities_week = supabase.table("activities") \
        .select("*") \
        .eq("employee_id", user['id']) \
        .gte("date", str(week_start)) \
        .execute()
    
    # בתי ספר ייחודיים
    all_activities = supabase.table("activities") \
        .select("school_id") \
        .eq("employee_id", user['id']) \
        .execute()
    
    unique_schools = len(set([a['school_id'] for a in all_activities.data])) if all_activities.data else 0
    
    with col1:
        st.metric("פעילויות החודש", len(activities_month.data) if activities_month.data else 0)
    
    with col2:
        st.metric("פעילויות השבוע", len(activities_week.data) if activities_week.data else 0)
    
    with col3:
        st.metric("בתי ספר שעבדתי בהם", unique_schools)

except Exception as e:
    st.error(f"שגיאה בטעינת נתונים: {str(e)}")
    with col1:
        st.metric("פעילויות החודש", "0")
    with col2:
        st.metric("פעילויות השבוע", "0")
    with col3:
        st.metric("בתי ספר שעבדתי בהם", "0")

st.markdown("---")

# הלו"ז שלי
col_schedule, col_pending = st.columns([2, 1])

with col_schedule:
    st.subheader("📅 הלו״ז שלי השבוע")
    
    try:
        # שליפת פעילויות 7 ימים קדימה
        end_date = (datetime.now() + timedelta(days=7)).date()
        my_activities = supabase.table("activities") \
            .select("*, schools(name, address)") \
            .eq("employee_id", user['id']) \
            .gte("date", str(today)) \
            .lte("date", str(end_date)) \
            .order("date") \
            .execute()
        
        if my_activities.data and len(my_activities.data) > 0:
            for activity in my_activities.data:
                school_name = activity['schools']['name'] if activity['schools'] else 'לא ידוע'
                school_address = activity['schools']['address'] if activity['schools'] else ''
                
                status_emoji = {
                    'planned': '🟡',
                    'confirmed': '🟢',
                    'completed': '✅',
                    'cancelled': '🔴'
                }.get(activity['status'], '⚪')
                
                with st.expander(f"{status_emoji} {activity['date']} - {school_name}"):
                    st.markdown(f"**שעות:** {activity['time_start']} - {activity['time_end']}")
                    if school_address:
                        st.markdown(f"**כתובת:** {school_address}")
                    if activity.get('notes'):
                        st.markdown(f"**הערות:** {activity['notes']}")
                    
                    # אישור פעילות
                    if activity['status'] in ['planned', 'confirmed'] and not activity.get('confirmed_by_employee'):
                        if st.button(f"✅ אשר ביצוע פעילות", key=f"confirm_{activity['id']}"):
                            try:
                                supabase.table("activities") \
                                    .update({
                                        "confirmed_by_employee": True,
                                        "confirmation_time": datetime.now().isoformat(),
                                        "status": "completed"
                                    }) \
                                    .eq("id", activity['id']) \
                                    .execute()
                                st.success("✅ הפעילות אושרה בהצלחה!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"שגיאה באישור: {str(e)}")
                    elif activity.get('confirmed_by_employee'):
                        st.success("✅ אישרת את ביצוע הפעילות")
        else:
            st.info("אין פעילויות מתוכננות לשבוע הקרוב")
    
    except Exception as e:
        st.warning("טרם שובצת לפעילויות")

with col_pending:
    st.subheader("⏳ ממתין לאישור")
    
    try:
        pending_activities = supabase.table("activities") \
            .select("*, schools(name)") \
            .eq("employee_id", user['id']) \
            .eq("confirmed_by_employee", False) \
            .lte("date", str(today)) \
            .execute()
        
        if pending_activities.data and len(pending_activities.data) > 0:
            st.warning(f"יש לך {len(pending_activities.data)} פעילויות שטרם אישרת!")
            
            for activity in pending_activities.data[:5]:
                school_name = activity['schools']['name'] if activity['schools'] else 'לא ידוע'
                st.markdown(f"- **{activity['date']}** - {school_name}")
        else:
            st.success("✅ אין פעילויות ממתינות לאישור")
    
    except Exception as e:
        st.info("אין פעילויות ממתינות")

st.markdown("---")

# ניתוח ביצועים אישי
st.subheader("📊 הביצועים שלי")

col_stats1, col_stats2 = st.columns(2)

with col_stats1:
    st.markdown("#### 📈 פעילויות לפי חודש")
    try:
        three_months_ago = (datetime.now() - timedelta(days=90)).date()
        activities_history = supabase.table("activities") \
            .select("date") \
            .eq("employee_id", user['id']) \
            .gte("date", str(three_months_ago)) \
            .execute()
        
        if activities_history.data and len(activities_history.data) > 0:
            df_history = pd.DataFrame(activities_history.data)
            df_history['date'] = pd.to_datetime(df_history['date'])
            df_history['month'] = df_history['date'].dt.to_period('M').astype(str)
            monthly_count = df_history.groupby('month').size().reset_index(name='count')
            
            for _, row in monthly_count.iterrows():
                st.metric(row['month'], f"{row['count']} פעילויות")
        else:
            st.info("טרם ביצעת פעילויות")
    except Exception as e:
        st.info("אין מספיק נתונים")

with col_stats2:
    st.markdown("#### 🏫 בתי הספר שלי")
    try:
        activities_by_school = supabase.table("activities") \
            .select("school_id, schools(name)") \
            .eq("employee_id", user['id']) \
            .execute()
        
        if activities_by_school.data:
            df_schools = pd.DataFrame(activities_by_school.data)
            df_schools['school_name'] = df_schools['schools'].apply(lambda x: x['name'] if x else 'לא ידוע')
            school_count = df_schools.groupby('school_name').size().reset_index(name='count')
            school_count = school_count.sort_values('count', ascending=False)
            
            for _, row in school_count.head(5).iterrows():
                st.markdown(f"- **{row['school_name']}**: {row['count']} פעילויות")
        else:
            st.info("טרם עבדת בבתי ספר")
    except Exception as e:
        st.info("אין מספיק נתונים")

st.markdown("---")

# דיווח מהיר על ציוד
st.subheader("🔧 דיווח חוסר ציוד")

with st.form("quick_equipment_report"):
    col_eq1, col_eq2 = st.columns(2)
    
    with col_eq1:
        # שליפת רשימת ציוד
        try:
            equipment_list = supabase.table("equipment").select("id, name").execute()
            equipment_options = {item['name']: item['id'] for item in equipment_list.data} if equipment_list.data else {}
            
            selected_equipment = st.selectbox("בחר פריט ציוד", list(equipment_options.keys()) if equipment_options else ["אין ציוד במערכת"])
        except:
            equipment_options = {}
            selected_equipment = st.text_input("שם הציוד החסר")
    
    with col_eq2:
        quantity_needed = st.number_input("כמות נדרשת", min_value=1, value=1)
    
    urgency = st.selectbox("רמת דחיפות", ["low", "medium", "high"], 
                          format_func=lambda x: {"low": "נמוכה", "medium": "בינונית", "high": "גבוהה"}[x])
    
    notes = st.text_area("הערות נוספות (אופציונלי)")
    
    submit_report = st.form_submit_button("📝 שלח דיווח", use_container_width=True)
    
    if submit_report:
        try:
            if equipment_options and selected_equipment in equipment_options:
                report_data = {
                    "equipment_id": equipment_options[selected_equipment],
                    "employee_id": user['id'],
                    "quantity_needed": quantity_needed,
                    "urgency": urgency,
                    "status": "pending",
                    "notes": notes if notes else None
                }
                
                supabase.table("equipment_reports").insert(report_data).execute()
                st.success("✅ הדיווח נשלח בהצלחה!")
                st.rerun()
            else:
                st.error("אנא בחר ציוד מהרשימה")
        except Exception as e:
            st.error(f"שגיאה בשליחת הדיווח: {str(e)}")
