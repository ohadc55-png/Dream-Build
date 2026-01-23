import streamlit as st
from utils.auth import require_role
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
from utils.nav import render_sidebar
import pandas as pd
from datetime import datetime, timedelta

# === הגדרות עמוד ===
st.set_page_config(page_title="הדשבורד שלי | Dream & Build", page_icon="👷", layout="wide")
apply_custom_css()
render_sidebar()

# === וידוא הרשאות ===
user = require_role('employee')

# === כותרת ===
st.markdown(f"""
<h1 style='margin-bottom: 0;'>👷 שלום, {user.get('full_name', 'עובד')}!</h1>
<p style='color: #6B7280; margin-top: 0.25rem;'>הנה סקירת הפעילויות שלך</p>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# === שליפת נתונים ===
try:
    today = datetime.now().date()
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=today.weekday())
    
    # פעילויות החודש
    my_activities = supabase.table("activities") \
        .select("*, schools(name)") \
        .eq("employee_id", user['id']) \
        .gte("date", str(month_start)) \
        .order("date") \
        .execute()
    
    activities_data = my_activities.data if my_activities.data else []
    
    # חישובים
    total_month = len(activities_data)
    completed = len([a for a in activities_data if a['status'] == 'completed'])
    pending_confirm = len([a for a in activities_data if a['status'] in ['planned', 'confirmed'] and not a.get('confirmed_by_employee') and a['date'] <= str(today)])
    upcoming = len([a for a in activities_data if a['date'] >= str(today) and a['status'] in ['planned', 'confirmed']])
    
    # בתי ספר ייחודיים
    unique_schools = len(set([a['school_id'] for a in activities_data if a.get('school_id')]))
    
except Exception as e:
    st.error(f"שגיאה: {str(e)}")
    total_month = completed = pending_confirm = upcoming = unique_schools = 0
    activities_data = []

# === KPIs ===
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div style='background: white; padding: 1.25rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid #3B82F6;'>
        <div style='font-size: 0.85rem; color: #6B7280;'>📅 פעילויות החודש</div>
        <div style='font-size: 2rem; font-weight: 700; color: #1A2840;'>{total_month}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background: white; padding: 1.25rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid #10B981;'>
        <div style='font-size: 0.85rem; color: #6B7280;'>✅ הושלמו</div>
        <div style='font-size: 2rem; font-weight: 700; color: #047857;'>{completed}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    alert_color = "#F59E0B" if pending_confirm > 0 else "#6B7280"
    st.markdown(f"""
    <div style='background: white; padding: 1.25rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid {alert_color};'>
        <div style='font-size: 0.85rem; color: #6B7280;'>⏳ ממתין לאישורך</div>
        <div style='font-size: 2rem; font-weight: 700; color: {alert_color};'>{pending_confirm}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style='background: white; padding: 1.25rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid #6B7280;'>
        <div style='font-size: 0.85rem; color: #6B7280;'>🏫 בתי ספר</div>
        <div style='font-size: 2rem; font-weight: 700; color: #1A2840;'>{unique_schools}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# === התראה לפעילויות שצריך לאשר ===
if pending_confirm > 0:
    st.markdown(f"""
    <div style='background: #FEF3C7; padding: 1rem; border-radius: 10px; border-right: 4px solid #F59E0B; margin-bottom: 1rem;'>
        <div style='font-weight: 600; color: #92400E;'>⚠️ יש לך {pending_confirm} פעילויות שממתינות לאישור ביצוע!</div>
        <div style='font-size: 0.9rem; color: #6B7280;'>לחץ על "אשר ביצוע" בטבלה למטה</div>
    </div>
    """, unsafe_allow_html=True)

# === טבלאות ===
col_upcoming, col_pending = st.columns(2)

with col_upcoming:
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #E5E7EB;'>
        <h3 style='margin: 0 0 1rem 0; font-size: 1rem; color: #374151;'>📅 פעילויות קרובות</h3>
    """, unsafe_allow_html=True)
    
    upcoming_acts = [a for a in activities_data if a['date'] >= str(today) and a['status'] in ['planned', 'confirmed']]
    
    if upcoming_acts:
        for act in upcoming_acts[:5]:
            status_icon = "🟢" if act['status'] == 'confirmed' else "🟡"
            school_name = act['schools']['name'] if act.get('schools') else '-'
            
            st.markdown(f"""
            <div style='background: #F9FAFB; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem;'>
                <div style='font-weight: 600;'>{status_icon} {act['date']}</div>
                <div style='font-size: 0.9rem; color: #6B7280;'>{school_name} | {act['time_start'][:5]} - {act['time_end'][:5]}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("אין פעילויות קרובות")
    
    st.markdown("</div>", unsafe_allow_html=True)

with col_pending:
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #E5E7EB;'>
        <h3 style='margin: 0 0 1rem 0; font-size: 1rem; color: #374151;'>⏳ ממתין לאישור</h3>
    """, unsafe_allow_html=True)
    
    pending_acts = [a for a in activities_data if a['date'] <= str(today) and a['status'] in ['planned', 'confirmed'] and not a.get('confirmed_by_employee')]
    
    if pending_acts:
        for act in pending_acts[:5]:
            school_name = act['schools']['name'] if act.get('schools') else '-'
            
            col_info, col_btn = st.columns([3, 1])
            with col_info:
                st.markdown(f"""
                <div style='background: #FEF3C7; padding: 0.75rem; border-radius: 8px;'>
                    <div style='font-weight: 600;'>{act['date']}</div>
                    <div style='font-size: 0.9rem; color: #6B7280;'>{school_name}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_btn:
                if st.button("✅ אשר", key=f"confirm_{act['id']}"):
                    supabase.table("activities").update({
                        "confirmed_by_employee": True,
                        "status": "completed"
                    }).eq("id", act['id']).execute()
                    st.rerun()
    else:
        st.success("✅ הכל מאושר!")
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# === היסטוריה ===
st.markdown("""
<div style='background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #E5E7EB;'>
    <h3 style='margin: 0 0 1rem 0; font-size: 1rem; color: #374151;'>📋 היסטוריית פעילויות החודש</h3>
""", unsafe_allow_html=True)

if activities_data:
    rows = []
    for act in activities_data:
        status_badge = {
            'planned': '🟡 מתוכנן',
            'confirmed': '🟢 מאושר',
            'completed': '✅ הושלם',
            'cancelled': '🔴 בוטל'
        }.get(act['status'], act['status'])
        
        rows.append({
            'תאריך': act['date'],
            'בית ספר': act['schools']['name'] if act.get('schools') else '-',
            'שעות': f"{act['time_start'][:5]} - {act['time_end'][:5]}",
            'סטטוס': status_badge,
            'אושר': '✅' if act.get('confirmed_by_employee') else '❌'
        })
    
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("אין פעילויות החודש")

st.markdown("</div>", unsafe_allow_html=True)
