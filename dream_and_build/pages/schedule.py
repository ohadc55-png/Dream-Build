import streamlit as st
from utils.auth import check_auth
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="ניהול לו״ז", page_icon="📅", layout="wide")
apply_custom_css()

# בדיקת אימות
user = check_auth()
is_manager = user.get('role') == 'manager'

st.title("📅 ניהול לו״ז" if is_manager else "📅 הלו״ז שלי")

# טאבים - למנהל יש יותר אפשרויות
if is_manager:
    tab1, tab2, tab3 = st.tabs(["📋 לוח שנה", "➕ הוספת פעילות", "📊 סיכום"])
else:
    tab1, tab2 = st.tabs(["📋 הלו״ז שלי", "📊 סיכום"])

# טאב 1: לוח שנה / רשימת פעילויות
with tab1:
    # פילטרים
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        date_range = st.selectbox("טווח זמן", ["השבוע", "החודש", "כל הזמנים"])
    
    with col_f2:
        status_filter = st.selectbox("סטטוס", ["הכל", "מתוכנן", "מאושר", "הושלם", "בוטל"])
    
    if is_manager:
        with col_f3:
            # שליפת עובדים לפילטר
            try:
                employees_list = supabase.table("users").select("id, full_name").eq("role", "employee").execute()
                emp_options = {"הכל": None}
                if employees_list.data:
                    emp_options.update({e['full_name']: e['id'] for e in employees_list.data})
                emp_filter = st.selectbox("עובד", list(emp_options.keys()))
            except:
                emp_filter = "הכל"
                emp_options = {"הכל": None}
    
    # חישוב טווח תאריכים
    today = datetime.now().date()
    if date_range == "השבוע":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif date_range == "החודש":
        start_date = today.replace(day=1)
        next_month = today.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
    else:
        start_date = today - timedelta(days=365)
        end_date = today + timedelta(days=365)
    
    # מיפוי סטטוסים
    status_map = {
        "הכל": None,
        "מתוכנן": "planned",
        "מאושר": "confirmed",
        "הושלם": "completed",
        "בוטל": "cancelled"
    }
    
    try:
        # בניית שאילתה
        query = supabase.table("activities") \
            .select("*, schools(name), users(full_name)") \
            .gte("date", str(start_date)) \
            .lte("date", str(end_date)) \
            .order("date")
        
        # פילטר עובד (למנהל או לעובד)
        if not is_manager:
            query = query.eq("employee_id", user['id'])
        elif is_manager and emp_filter != "הכל":
            query = query.eq("employee_id", emp_options[emp_filter])
        
        # פילטר סטטוס
        if status_map[status_filter]:
            query = query.eq("status", status_map[status_filter])
        
        activities = query.execute()
        
        if activities.data and len(activities.data) > 0:
            df = pd.DataFrame(activities.data)
            df['school_name'] = df['schools'].apply(lambda x: x['name'] if x else 'לא ידוע')
            df['employee_name'] = df['users'].apply(lambda x: x['full_name'] if x else 'לא שובץ')
            
            status_emoji = {
                'planned': '🟡 מתוכנן',
                'confirmed': '🟢 מאושר',
                'completed': '✅ הושלם',
                'cancelled': '🔴 בוטל'
            }
            df['status_he'] = df['status'].map(status_emoji)
            
            # הצגה בטבלה
            display_cols = ['date', 'school_name', 'time_start', 'time_end', 'status_he']
            col_names = ['תאריך', 'בית ספר', 'התחלה', 'סיום', 'סטטוס']
            
            if is_manager:
                display_cols.insert(2, 'employee_name')
                col_names.insert(2, 'עובד')
            
            df_display = df[display_cols].copy()
            df_display.columns = col_names
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # עריכה (למנהל בלבד)
            if is_manager:
                st.markdown("---")
                st.subheader("✏️ עריכת פעילות")
                
                activity_options = [f"{a['date']} - {a['school_name']}" for _, a in df.iterrows()]
                selected_activity = st.selectbox("בחר פעילות לעריכה", activity_options)
                
                if selected_activity:
                    idx = activity_options.index(selected_activity)
                    activity = df.iloc[idx]
                    
                    with st.form("edit_activity_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_date = st.date_input("תאריך", value=pd.to_datetime(activity['date']))
                            edit_time_start = st.time_input("שעת התחלה", value=datetime.strptime(activity['time_start'], '%H:%M:%S').time() if activity['time_start'] else datetime.now().time())
                        
                        with col2:
                            edit_status = st.selectbox("סטטוס", ['planned', 'confirmed', 'completed', 'cancelled'],
                                                      index=['planned', 'confirmed', 'completed', 'cancelled'].index(activity['status']),
                                                      format_func=lambda x: {'planned': 'מתוכנן', 'confirmed': 'מאושר', 'completed': 'הושלם', 'cancelled': 'בוטל'}[x])
                            edit_time_end = st.time_input("שעת סיום", value=datetime.strptime(activity['time_end'], '%H:%M:%S').time() if activity['time_end'] else datetime.now().time())
                        
                        edit_notes = st.text_area("הערות", value=activity.get('notes', '') or '')
                        
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            update_btn = st.form_submit_button("💾 שמור", use_container_width=True)
                        with col_btn2:
                            delete_btn = st.form_submit_button("🗑️ מחק", use_container_width=True, type="secondary")
                        
                        if update_btn:
                            try:
                                update_data = {
                                    "date": str(edit_date),
                                    "time_start": str(edit_time_start),
                                    "time_end": str(edit_time_end),
                                    "status": edit_status,
                                    "notes": edit_notes if edit_notes else None
                                }
                                supabase.table("activities").update(update_data).eq("id", activity['id']).execute()
                                st.success("✅ הפעילות עודכנה!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ שגיאה: {str(e)}")
                        
                        if delete_btn:
                            try:
                                supabase.table("activities").delete().eq("id", activity['id']).execute()
                                st.success("✅ הפעילות נמחקה!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ שגיאה: {str(e)}")
        else:
            st.info("אין פעילויות בטווח הזמן שנבחר")
    
    except Exception as e:
        st.error(f"שגיאה בטעינת פעילויות: {str(e)}")

# טאב 2: הוספת פעילות (למנהל) / סיכום (לעובד)
if is_manager:
    with tab2:
        st.subheader("➕ הוספת פעילות חדשה")
        
        with st.form("add_activity_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # שליפת בתי ספר
                try:
                    schools = supabase.table("schools").select("id, name").eq("status", "active").execute()
                    school_options = {s['name']: s['id'] for s in schools.data} if schools.data else {}
                except:
                    school_options = {}
                
                new_school = st.selectbox("בית ספר *", list(school_options.keys()) if school_options else ["אין בתי ספר"])
                new_date = st.date_input("תאריך *", value=datetime.now().date())
                new_time_start = st.time_input("שעת התחלה *", value=datetime.strptime("08:00", "%H:%M").time())
            
            with col2:
                # שליפת עובדים
                try:
                    employees = supabase.table("users").select("id, full_name").eq("role", "employee").eq("status", "active").execute()
                    employee_options = {e['full_name']: e['id'] for e in employees.data} if employees.data else {}
                except:
                    employee_options = {}
                
                new_employee = st.selectbox("עובד *", list(employee_options.keys()) if employee_options else ["אין עובדים"])
                new_status = st.selectbox("סטטוס", ['planned', 'confirmed'], format_func=lambda x: 'מתוכנן' if x == 'planned' else 'מאושר')
                new_time_end = st.time_input("שעת סיום *", value=datetime.strptime("14:00", "%H:%M").time())
            
            new_notes = st.text_area("הערות")
            
            submit = st.form_submit_button("➕ הוסף פעילות", use_container_width=True)
            
            if submit:
                if not school_options or not employee_options:
                    st.error("❌ יש להוסיף בתי ספר ועובדים לפני יצירת פעילות")
                else:
                    try:
                        activity_data = {
                            "school_id": school_options[new_school],
                            "employee_id": employee_options[new_employee],
                            "date": str(new_date),
                            "time_start": str(new_time_start),
                            "time_end": str(new_time_end),
                            "status": new_status,
                            "notes": new_notes if new_notes else None
                        }
                        
                        supabase.table("activities").insert(activity_data).execute()
                        st.success("✅ הפעילות נוספה בהצלחה!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ שגיאה: {str(e)}")

# טאב סיכום (משותף)
summary_tab = tab3 if is_manager else tab2
with summary_tab:
    st.subheader("📊 סיכום פעילויות")
    
    try:
        # שליפת פעילויות לסיכום
        if is_manager:
            activities_summary = supabase.table("activities").select("status, date").execute()
        else:
            activities_summary = supabase.table("activities").select("status, date").eq("employee_id", user['id']).execute()
        
        if activities_summary.data and len(activities_summary.data) > 0:
            df_summary = pd.DataFrame(activities_summary.data)
            
            # סטטיסטיקות
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("סה״כ פעילויות", len(df_summary))
            with col2:
                completed = len(df_summary[df_summary['status'] == 'completed'])
                st.metric("הושלמו", completed)
            with col3:
                planned = len(df_summary[df_summary['status'].isin(['planned', 'confirmed'])])
                st.metric("מתוכננות", planned)
            with col4:
                cancelled = len(df_summary[df_summary['status'] == 'cancelled'])
                st.metric("בוטלו", cancelled)
            
            # גרף לפי סטטוס
            import plotly.express as px
            status_counts = df_summary['status'].value_counts().reset_index()
            status_counts.columns = ['סטטוס', 'כמות']
            status_counts['סטטוס'] = status_counts['סטטוס'].map({
                'planned': 'מתוכנן',
                'confirmed': 'מאושר',
                'completed': 'הושלם',
                'cancelled': 'בוטל'
            })
            
            fig = px.pie(status_counts, values='כמות', names='סטטוס', 
                        title='התפלגות פעילויות לפי סטטוס',
                        color_discrete_sequence=['#FFD700', '#32CD32', '#FF8C00', '#FF6347'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("אין נתונים לסיכום")
    
    except Exception as e:
        st.info("טרם נאספו נתונים")
