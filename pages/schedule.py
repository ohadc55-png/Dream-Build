import streamlit as st
from utils.auth import check_auth
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
from utils.nav import render_sidebar
import pandas as pd
from datetime import datetime, timedelta
import hashlib

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

# === פונקציה ליצירת צבע קבוע לכל מדריך ===
def get_employee_color(employee_id: str) -> str:
    """יצירת צבע ייחודי וקבוע לכל מדריך"""
    colors = [
        "#3B82F6",  # כחול
        "#10B981",  # ירוק
        "#F59E0B",  # כתום
        "#EF4444",  # אדום
        "#8B5CF6",  # סגול
        "#EC4899",  # ורוד
        "#06B6D4",  # טורקיז
        "#84CC16",  # ירוק בהיר
        "#F97316",  # כתום כהה
        "#6366F1",  # אינדיגו
    ]
    if not employee_id:
        return "#6B7280"  # אפור לללא מדריך
    # יצירת אינדקס קבוע מה-ID
    hash_val = int(hashlib.md5(str(employee_id).encode()).hexdigest(), 16)
    return colors[hash_val % len(colors)]

# === שליפת נתונים בסיסיים ===
try:
    employees_data = supabase.table("users").select("id, full_name").eq("role", "employee").eq("status", "active").execute()
    emp_options = {e['full_name']: e['id'] for e in employees_data.data} if employees_data.data else {}
    emp_colors = {e['id']: get_employee_color(e['id']) for e in employees_data.data} if employees_data.data else {}
    emp_names_by_id = {e['id']: e['full_name'] for e in employees_data.data} if employees_data.data else {}
    
    schools_data = supabase.table("schools").select("id, name, price_per_day").eq("status", "active").execute()
    school_options = {s['name']: s['id'] for s in schools_data.data} if schools_data.data else {}
    school_prices = {s['id']: s['price_per_day'] for s in schools_data.data} if schools_data.data else {}
except:
    emp_options = {}
    emp_colors = {}
    emp_names_by_id = {}
    school_options = {}
    school_prices = {}

# === טאבים ===
if is_manager:
    tab1, tab2, tab3, tab4 = st.tabs(["📋 לוח פעילויות", "➕ פעילות בודדת", "🔄 תוכנית תהליכית", "📊 סיכום"])
else:
    tab1, tab2 = st.tabs(["📋 הפעילויות שלי", "✅ אישור ביצוע"])

# ========================================
# טאב 1: לוח פעילויות
# ========================================
with tab1:
    # פילטרים
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        date_filter = st.selectbox("טווח זמן", ["השבוע", "החודש", "הכל"])
    
    with col_f2:
        status_filter = st.selectbox("סטטוס", ["הכל", "מתוכנן", "מאושר", "הושלם", "בוטל"])
    
    if is_manager:
        with col_f3:
            filter_emp_options = ["כל המדריכים"] + list(emp_options.keys())
            emp_filter = st.selectbox("🎨 מדריך", filter_emp_options)
        
        with col_f4:
            filter_school_options = ["כל בתי הספר"] + list(school_options.keys())
            school_filter = st.selectbox("בית ספר", filter_school_options)
    
    # מקרא צבעים למדריכים
    if is_manager and emp_options:
        st.markdown("#### 🎨 מקרא מדריכים:")
        legend_html = "<div style='display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 1rem;'>"
        for emp_name, emp_id in emp_options.items():
            color = emp_colors.get(emp_id, "#6B7280")
            legend_html += f"<span style='background: {color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem;'>{emp_name}</span>"
        legend_html += "<span style='background: #6B7280; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem;'>❌ לא שובץ</span>"
        legend_html += "</div>"
        st.markdown(legend_html, unsafe_allow_html=True)
    
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
        elif is_manager and emp_filter != "כל המדריכים":
            query = query.eq("employee_id", emp_options.get(emp_filter))
        
        # פילטר בית ספר
        if is_manager and school_filter != "כל בתי הספר":
            query = query.eq("school_id", school_options.get(school_filter))
        
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
                    st.metric("⚠️ ללא מדריך", no_employee)
                else:
                    pct = f"{completed/total*100:.0f}%" if total > 0 else "0%"
                    st.metric("השלמה", pct)
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            # בניית טבלה צבעונית
            days_hebrew = ['שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת', 'ראשון']
            
            # הצגת לוח צבעוני
            st.markdown("#### 📅 לוח פעילויות:")
            
            for act in activities.data:
                emp_id = act.get('employee_id')
                color = emp_colors.get(emp_id, "#6B7280") if emp_id else "#6B7280"
                status_icon = {'planned': '🟡', 'confirmed': '🟢', 'completed': '✅', 'cancelled': '🔴'}.get(act['status'], '⚪')
                weekday = datetime.strptime(act['date'], '%Y-%m-%d').weekday()
                day_name = days_hebrew[weekday]
                
                emp_name = act['users']['full_name'] if act.get('users') else '❌ לא שובץ'
                school_name = act['schools']['name'] if act.get('schools') else '-'
                
                st.markdown(f"""
                <div style='background: white; padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem; border-right: 5px solid {color}; display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <div style='font-weight: 600; font-size: 1rem;'>{status_icon} {act['date']} ({day_name})</div>
                        <div style='color: #6B7280; font-size: 0.9rem;'>🏫 {school_name} | 👷 <span style='color: {color}; font-weight: 600;'>{emp_name}</span> | 🕐 {act['time_start'][:5]} - {act['time_end'][:5]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # === עריכה/מחיקת פעילות (מנהל) ===
            if is_manager:
                st.markdown("---")
                st.markdown("### ⚙️ עריכה/מחיקת פעילות")
                
                activity_labels = [f"{a['date']} | {a['schools']['name'] if a.get('schools') else '-'} | {a['users']['full_name'] if a.get('users') else 'לא שובץ'}" for a in activities.data]
                selected_idx = st.selectbox("בחר פעילות", range(len(activity_labels)), format_func=lambda x: activity_labels[x])
                
                selected_act = activities.data[selected_idx]
                
                col_edit, col_delete = st.columns([3, 1])
                
                with col_edit:
                    with st.form("edit_activity"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_date = st.date_input("📅 תאריך", value=datetime.strptime(selected_act['date'], '%Y-%m-%d'))
                            
                            emp_names = list(emp_options.keys())
                            current_emp = selected_act['users']['full_name'] if selected_act.get('users') else None
                            emp_idx = emp_names.index(current_emp) if current_emp in emp_names else 0
                            edit_employee = st.selectbox("👷 מדריך *", emp_names, index=emp_idx if emp_names else 0)
                        
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
                        
                        if st.form_submit_button("💾 שמור שינויים", use_container_width=True):
                            supabase.table("activities").update({
                                "date": str(edit_date),
                                "employee_id": emp_options.get(edit_employee),
                                "status": edit_status,
                                "time_start": str(edit_start),
                                "time_end": str(edit_end)
                            }).eq("id", selected_act['id']).execute()
                            st.success("✅ נשמר!")
                            st.rerun()
                
                with col_delete:
                    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
                    if st.button("🗑️ מחק פעילות", use_container_width=True, type="secondary"):
                        supabase.table("activities").delete().eq("id", selected_act['id']).execute()
                        st.success("🗑️ נמחק!")
                        st.rerun()
        else:
            st.info("אין פעילויות בטווח הנבחר")
            
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")

# ========================================
# טאב 2: פעילות בודדת (מנהל) / אישור ביצוע (עובד)
# ========================================
if is_manager:
    with tab2:
        st.markdown("### ➕ שיבוץ פעילות בודדת")
        
        with st.form("add_activity"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_school = st.selectbox("🏫 בית ספר *", list(school_options.keys()) if school_options else ["אין בתי ספר"])
                new_date = st.date_input("📅 תאריך *", value=datetime.now().date())
                new_employee = st.selectbox("👷 מדריך *", list(emp_options.keys()) if emp_options else ["אין מדריכים"])
            
            with col2:
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    new_start = st.time_input("🕐 התחלה", value=datetime.strptime("08:00", "%H:%M").time())
                with col_t2:
                    new_end = st.time_input("🕐 סיום", value=datetime.strptime("14:00", "%H:%M").time())
                
                new_status = st.selectbox("סטטוס", ['planned', 'confirmed'], format_func=lambda x: 'מתוכנן' if x == 'planned' else 'מאושר')
            
            new_notes = st.text_area("הערות")
            
            if new_school and school_options:
                price = school_prices.get(school_options.get(new_school), 0)
                st.info(f"💰 עלות פעילות: ₪{price:,}")
            
            if st.form_submit_button("➕ צור פעילות", use_container_width=True):
                if not new_school or not new_employee:
                    st.error("❌ חובה לבחור בית ספר ומדריך!")
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
                        st.success("✅ הפעילות נוצרה!")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ שגיאה: {str(e)}")
    
    # ========================================
    # טאב 3: תוכנית תהליכית
    # ========================================
    with tab3:
        st.markdown("### 🔄 יצירת תוכנית תהליכית")
        st.info("💡 צור סדרת פעילויות שחוזרות על עצמן - לדוגמה: 5 מפגשים בימי ראשון")
        
        with st.form("create_series"):
            col1, col2 = st.columns(2)
            
            with col1:
                series_school = st.selectbox("🏫 בית ספר *", list(school_options.keys()) if school_options else ["אין בתי ספר"], key="series_school")
                series_employee = st.selectbox("👷 מדריך *", list(emp_options.keys()) if emp_options else ["אין מדריכים"], key="series_emp")
                series_start_date = st.date_input("📅 תאריך התחלה *", value=datetime.now().date(), key="series_start")
            
            with col2:
                series_count = st.number_input("🔢 מספר מפגשים", min_value=1, max_value=52, value=5)
                series_day = st.selectbox("📆 יום בשבוע", 
                    options=[6, 0, 1, 2, 3, 4, 5],
                    format_func=lambda x: ['שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת', 'ראשון'][x]
                )
                
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    series_start_time = st.time_input("🕐 שעת התחלה", value=datetime.strptime("08:00", "%H:%M").time(), key="series_time_start")
                with col_t2:
                    series_end_time = st.time_input("🕐 שעת סיום", value=datetime.strptime("14:00", "%H:%M").time(), key="series_time_end")
            
            # תצוגה מקדימה
            st.markdown("#### 📋 תצוגה מקדימה:")
            
            # חישוב התאריכים
            preview_dates = []
            current_date = series_start_date
            
            days_until_target = (series_day - current_date.weekday()) % 7
            if days_until_target == 0 and current_date.weekday() != series_day:
                days_until_target = 7
            first_date = current_date + timedelta(days=days_until_target)
            
            for i in range(series_count):
                date = first_date + timedelta(weeks=i)
                preview_dates.append(date)
            
            days_hebrew = ['שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת', 'ראשון']
            preview_text = ", ".join([f"{d.strftime('%d/%m/%Y')} ({days_hebrew[d.weekday()]})" for d in preview_dates[:5]])
            if len(preview_dates) > 5:
                preview_text += f" ועוד {len(preview_dates) - 5}..."
            
            st.markdown(f"""
            <div style='background: #DBEAFE; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
                <div style='font-weight: 600; color: #1E40AF; margin-bottom: 0.5rem;'>📅 תאריכים שייווצרו:</div>
                <div style='color: #1E3A8A; font-size: 0.9rem;'>{preview_text}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if series_school and school_options:
                price_per_day = school_prices.get(school_options.get(series_school), 0)
                total_price = price_per_day * series_count
                st.markdown(f"""
                <div style='background: #D1FAE5; padding: 1rem; border-radius: 10px;'>
                    <div style='font-weight: 600; color: #065F46;'>💰 סה״כ עלות: ₪{total_price:,} ({series_count} × ₪{price_per_day:,})</div>
                </div>
                """, unsafe_allow_html=True)
            
            if st.form_submit_button("🚀 צור את כל הפעילויות", use_container_width=True):
                if not series_school or not series_employee:
                    st.error("❌ חובה לבחור בית ספר ומדריך!")
                else:
                    try:
                        activities_to_create = []
                        for date in preview_dates:
                            activities_to_create.append({
                                "school_id": school_options[series_school],
                                "employee_id": emp_options[series_employee],
                                "date": str(date),
                                "time_start": str(series_start_time),
                                "time_end": str(series_end_time),
                                "status": "planned",
                                "notes": f"תוכנית תהליכית - {series_count} מפגשים"
                            })
                        
                        supabase.table("activities").insert(activities_to_create).execute()
                        
                        st.success(f"✅ נוצרו {series_count} פעילויות בהצלחה!")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ שגיאה: {str(e)}")
    
    # ========================================
    # טאב 4: סיכום לפי מדריך
    # ========================================
    with tab4:
        st.markdown("### 📊 סיכום פעילויות לפי מדריך")
        
        try:
            month_start = datetime.now().replace(day=1).date()
            month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            
            all_activities = supabase.table("activities") \
                .select("employee_id, status") \
                .gte("date", str(month_start)) \
                .lte("date", str(month_end)) \
                .execute()
            
            if all_activities.data and emp_options:
                for emp_name, emp_id in emp_options.items():
                    emp_acts = [a for a in all_activities.data if a['employee_id'] == emp_id]
                    total = len(emp_acts)
                    completed = len([a for a in emp_acts if a['status'] == 'completed'])
                    planned = len([a for a in emp_acts if a['status'] in ['planned', 'confirmed']])
                    
                    color = emp_colors.get(emp_id, "#6B7280")
                    
                    st.markdown(f"""
                    <div style='background: white; padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem; border-right: 5px solid {color};'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <span style='font-weight: 600; color: {color};'>{emp_name}</span>
                            <span>סה״כ: {total} | ✅ {completed} | 🟡 {planned}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("אין נתונים לחודש זה")
                
        except Exception as e:
            st.error(f"שגיאה: {str(e)}")

else:
    # טאב אישור ביצוע לעובד
    with tab2:
        st.markdown("### ✅ אישור ביצוע פעילויות")
        
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
                            st.rerun()
            else:
                st.success("✅ כל הפעילויות אושרו!")
                
        except Exception as e:
            st.error(f"שגיאה: {str(e)}")
