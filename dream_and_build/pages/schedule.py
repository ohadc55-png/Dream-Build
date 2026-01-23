import streamlit as st
from utils.auth import check_auth
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
from utils.nav import render_sidebar
import pandas as pd
from datetime import datetime, timedelta

# === הגדרות עמוד ===
st.set_page_config(page_title="ניהול לו״ז | Dream & Build", page_icon="📅", layout="wide")
apply_custom_css()
render_sidebar()

# === וידוא הרשאות ===
user = check_auth()
is_manager = user.get('role') == 'manager'

# === כותרת ===
st.markdown(f"""
<h1 style='margin-bottom: 0;'>📅 {'ניהול לו״ז' if is_manager else 'הלו״ז שלי'}</h1>
<p style='color: #6B7280; margin-top: 0.25rem;'>{'תכנון ושיבוץ פעילויות' if is_manager else 'צפייה ואישור פעילויות'}</p>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# === שליפת נתונים בסיסיים ===
try:
    employees_data = supabase.table("users").select("id, full_name").eq("role", "employee").eq("status", "active").execute()
    emp_options = {e['full_name']: e['id'] for e in employees_data.data} if employees_data.data else {}
    
    schools_data = supabase.table("schools").select("id, name, price_per_day").eq("status", "active").execute()
    school_options = {s['name']: s['id'] for s in schools_data.data} if schools_data.data else {}
    school_prices = {s['id']: s['price_per_day'] for s in schools_data.data} if schools_data.data else {}
except:
    emp_options = {}
    school_options = {}
    school_prices = {}

# === טאבים ===
if is_manager:
    tab1, tab2, tab3 = st.tabs(["📋 לוח פעילויות", "➕ שיבוץ פעילות חדשה", "📊 סיכום"])
else:
    tab1, tab2 = st.tabs(["📋 הפעילויות שלי", "✅ אישור ביצוע"])

# ========================================
# טאב 1: לוח פעילויות
# ========================================
with tab1:
    # פילטרים
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        date_filter = st.selectbox("טווח זמן", ["השבוע", "החודש", "הכל"])
    
    with col_f2:
        status_filter = st.selectbox("סטטוס", ["הכל", "מתוכנן", "מאושר", "הושלם", "בוטל"])
    
    if is_manager:
        with col_f3:
            filter_emp_options = ["הכל"] + list(emp_options.keys())
            emp_filter = st.selectbox("עובד", filter_emp_options)
    
    # חישוב טווח תאריכים
    today = datetime.now().date()
    if date_filter == "השבוע":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif date_filter == "החודש":
        start_date = today.replace(day=1)
        end_date = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    else:
        start_date = today - timedelta(days=90)
        end_date = today + timedelta(days=90)
    
    status_map = {"הכל": None, "מתוכנן": "planned", "מאושר": "confirmed", "הושלם": "completed", "בוטל": "cancelled"}
    
    try:
        # בניית שאילתה
        query = supabase.table("activities") \
            .select("*, schools(name, price_per_day), users(full_name)") \
            .gte("date", str(start_date)) \
            .lte("date", str(end_date)) \
            .order("date")
        
        # פילטר עובד
        if not is_manager:
            query = query.eq("employee_id", user['id'])
        elif is_manager and emp_filter != "הכל":
            query = query.eq("employee_id", emp_options.get(emp_filter))
        
        # פילטר סטטוס
        if status_map.get(status_filter):
            query = query.eq("status", status_map[status_filter])
        
        activities = query.execute()
        
        if activities.data:
            # סטטיסטיקות
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            total = len(activities.data)
            completed = len([a for a in activities.data if a['status'] == 'completed'])
            planned = len([a for a in activities.data if a['status'] in ['planned', 'confirmed']])
            no_employee = len([a for a in activities.data if not a.get('employee_id')])
            
            with col_s1:
                st.metric("סה״כ", total)
            with col_s2:
                st.metric("הושלמו", completed)
            with col_s3:
                st.metric("מתוכננות", planned)
            with col_s4:
                if is_manager and no_employee > 0:
                    st.metric("⚠️ ללא עובד", no_employee)
                else:
                    pct = f"{completed/total*100:.0f}%" if total > 0 else "0%"
                    st.metric("השלמה", pct)
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            # בניית טבלה
            days_hebrew = ['שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת', 'ראשון']
            rows = []
            for act in activities.data:
                status_badge = {
                    'planned': '🟡 מתוכנן',
                    'confirmed': '🟢 מאושר', 
                    'completed': '✅ הושלם',
                    'cancelled': '🔴 בוטל'
                }.get(act['status'], act['status'])
                
                weekday = datetime.strptime(act['date'], '%Y-%m-%d').weekday()
                
                rows.append({
                    'id': act['id'],
                    'תאריך': act['date'],
                    'יום': days_hebrew[weekday],
                    'בית ספר': act['schools']['name'] if act.get('schools') else '-',
                    'עובד': act['users']['full_name'] if act.get('users') else '❌ לא שובץ',
                    'שעות': f"{act['time_start'][:5]} - {act['time_end'][:5]}",
                    'סטטוס': status_badge,
                    'status_raw': act['status'],
                    'employee_id': act.get('employee_id'),
                    'confirmed_by_employee': act.get('confirmed_by_employee', False)
                })
            
            df = pd.DataFrame(rows)
            st.dataframe(df[['תאריך', 'יום', 'בית ספר', 'עובד', 'שעות', 'סטטוס']], use_container_width=True, hide_index=True)
            
            # === עריכת פעילות (מנהל) ===
            if is_manager:
                st.markdown("---")
                st.markdown("### ⚙️ עריכת פעילות")
                
                activity_labels = [f"{r['תאריך']} | {r['בית ספר']} | {r['עובד']}" for _, r in df.iterrows()]
                selected_idx = st.selectbox("בחר פעילות לעריכה", range(len(activity_labels)), format_func=lambda x: activity_labels[x])
                
                selected_act = activities.data[selected_idx]
                
                with st.form("edit_activity"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edit_date = st.date_input("תאריך", value=datetime.strptime(selected_act['date'], '%Y-%m-%d'))
                        
                        # בחירת עובד - חובה!
                        emp_names = list(emp_options.keys())
                        current_emp = selected_act['users']['full_name'] if selected_act.get('users') else None
                        emp_idx = emp_names.index(current_emp) if current_emp in emp_names else 0
                        
                        edit_employee = st.selectbox("👷 עובד אחראי *", emp_names, index=emp_idx if emp_names else 0)
                        st.caption("⚠️ חובה לשבץ עובד אחראי לכל פעילות")
                    
                    with col2:
                        statuses = ['planned', 'confirmed', 'completed', 'cancelled']
                        status_labels = {'planned': 'מתוכנן', 'confirmed': 'מאושר', 'completed': 'הושלם', 'cancelled': 'בוטל'}
                        current_status_idx = statuses.index(selected_act['status']) if selected_act['status'] in statuses else 0
                        edit_status = st.selectbox("סטטוס", statuses, index=current_status_idx, format_func=lambda x: status_labels[x])
                        
                        col_t1, col_t2 = st.columns(2)
                        with col_t1:
                            edit_start = st.time_input("התחלה", value=datetime.strptime(selected_act['time_start'][:5], '%H:%M').time())
                        with col_t2:
                            edit_end = st.time_input("סיום", value=datetime.strptime(selected_act['time_end'][:5], '%H:%M').time())
                    
                    edit_notes = st.text_area("הערות", value=selected_act.get('notes', '') or '')
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.form_submit_button("💾 שמור שינויים", use_container_width=True):
                            if not edit_employee:
                                st.error("❌ חובה לבחור עובד אחראי!")
                            else:
                                supabase.table("activities").update({
                                    "date": str(edit_date),
                                    "employee_id": emp_options.get(edit_employee),
                                    "status": edit_status,
                                    "time_start": str(edit_start),
                                    "time_end": str(edit_end),
                                    "notes": edit_notes
                                }).eq("id", selected_act['id']).execute()
                                st.success("✅ נשמר!")
                                st.rerun()
                    
                    with col_btn2:
                        if st.form_submit_button("🗑️ מחק פעילות", use_container_width=True):
                            supabase.table("activities").delete().eq("id", selected_act['id']).execute()
                            st.success("🗑️ נמחק!")
                            st.rerun()
        else:
            st.info("אין פעילויות בטווח הנבחר")
            
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")

# ========================================
# טאב 2: שיבוץ פעילות חדשה (מנהל) / אישור ביצוע (עובד)
# ========================================
if is_manager:
    with tab2:
        st.markdown("### ➕ שיבוץ פעילות חדשה")
        
        with st.form("add_activity"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_school = st.selectbox("🏫 בית ספר *", list(school_options.keys()) if school_options else ["אין בתי ספר"])
                new_date = st.date_input("📅 תאריך *", value=datetime.now().date())
                new_employee = st.selectbox("👷 עובד אחראי *", list(emp_options.keys()) if emp_options else ["אין עובדים"])
                st.caption("⚠️ חובה לשבץ עובד אחראי")
            
            with col2:
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    new_start = st.time_input("🕐 התחלה", value=datetime.strptime("08:00", "%H:%M").time())
                with col_t2:
                    new_end = st.time_input("🕐 סיום", value=datetime.strptime("14:00", "%H:%M").time())
                
                new_status = st.selectbox("סטטוס", ['planned', 'confirmed'], format_func=lambda x: 'מתוכנן' if x == 'planned' else 'מאושר')
            
            new_notes = st.text_area("הערות")
            
            # הצגת מחיר
            if new_school and school_options:
                price = school_prices.get(school_options.get(new_school), 0)
                st.info(f"💰 עלות פעילות: ₪{price:,}")
            
            if st.form_submit_button("➕ צור פעילות", use_container_width=True):
                if not new_school or not new_employee:
                    st.error("❌ חובה לבחור בית ספר ועובד אחראי!")
                elif not school_options or not emp_options:
                    st.error("❌ אין בתי ספר או עובדים במערכת")
                else:
                    try:
                        supabase.table("activities").insert({
                            "school_id": school_options[new_school],
                            "employee_id": emp_options[new_employee],
                            "date": str(new_date),
                            "time_start": str(new_start),
                            "time_end": str(new_end),
                            "status": new_status,
                            "notes": new_notes or None
                        }).execute()
                        st.success("✅ הפעילות נוצרה בהצלחה!")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ שגיאה: {str(e)}")

else:
    # טאב אישור ביצוע לעובד
    with tab2:
        st.markdown("### ✅ אישור ביצוע פעילויות")
        st.info("כאן תוכל לאשר פעילויות שביצעת")
        
        try:
            today = datetime.now().date()
            pending = supabase.table("activities") \
                .select("*, schools(name)") \
                .eq("employee_id", user['id']) \
                .eq("confirmed_by_employee", False) \
                .lte("date", str(today)) \
                .in_("status", ["planned", "confirmed"]) \
                .execute()
            
            if pending.data:
                st.warning(f"⚠️ יש לך {len(pending.data)} פעילויות שממתינות לאישור")
                
                for act in pending.data:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"""
                            <div style='background: #FEF3C7; padding: 1rem; border-radius: 10px; border-right: 4px solid #F59E0B;'>
                                <div style='font-weight: 600;'>{act['date']} - {act['schools']['name'] if act.get('schools') else '-'}</div>
                                <div style='font-size: 0.9rem; color: #6B7280;'>{act['time_start'][:5]} - {act['time_end'][:5]}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            if st.button("✅ אשר", key=f"confirm_{act['id']}"):
                                supabase.table("activities").update({
                                    "confirmed_by_employee": True,
                                    "status": "completed"
                                }).eq("id", act['id']).execute()
                                st.success("אושר!")
                                st.rerun()
                        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            else:
                st.success("✅ כל הפעילויות אושרו!")
                
        except Exception as e:
            st.error(f"שגיאה: {str(e)}")

# ========================================
# טאב 3: סיכום
# ========================================
tab_summary = tab3 if is_manager else tab2
# הסיכום כבר מופיע בטאב הראשון
