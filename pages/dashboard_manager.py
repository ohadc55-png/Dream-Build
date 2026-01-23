import streamlit as st
from utils.auth import require_role
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
from utils.nav import render_sidebar
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# === הגדרות עמוד ===
st.set_page_config(page_title="דשבורד מנהלים | Dream & Build", page_icon="📊", layout="wide")
apply_custom_css()
render_sidebar()

# === וידוא הרשאות ===
user = require_role('manager')

# === כותרת עמוד ===
col_title, col_date = st.columns([3, 1])
with col_title:
    st.markdown(f"""
    <h1 style='margin-bottom: 0;'>📊 דשבורד מנהלים</h1>
    <p style='color: #6B7280; margin-top: 0.25rem;'>שלום {user.get('full_name', 'מנהל')}, הנה סקירת המערכת שלך</p>
    """, unsafe_allow_html=True)
with col_date:
    st.markdown(f"""
    <div style='text-align: left; padding: 1rem; background: white; border-radius: 10px; border: 1px solid #E5E7EB;'>
        <div style='font-size: 0.75rem; color: #6B7280;'>תאריך היום</div>
        <div style='font-size: 1.1rem; font-weight: 600; color: #1A2840;'>{datetime.now().strftime('%d/%m/%Y')}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# === שליפת נתונים ===
try:
    today = datetime.now().date()
    month_start = today.replace(day=1)
    
    # פעילויות
    activities_today = supabase.table("activities").select("*").eq("date", str(today)).execute()
    activities_month = supabase.table("activities").select("*").gte("date", str(month_start)).execute()
    activities_completed = supabase.table("activities").select("*").eq("status", "completed").gte("date", str(month_start)).execute()
    
    # עובדים
    employees = supabase.table("users").select("*").eq("role", "employee").eq("status", "active").execute()
    
    # בתי ספר
    schools = supabase.table("schools").select("*").eq("status", "active").execute()
    
    # ציוד במלאי נמוך
    equipment = supabase.table("equipment").select("*").execute()
    low_stock = [item for item in equipment.data if item.get('quantity_available', 0) <= item.get('min_threshold', 0)]
    
    # הכנסות החודש (מפעילויות שהושלמו)
    total_income = 0
    if activities_completed.data and schools.data:
        school_prices = {s['id']: s['price_per_day'] for s in schools.data}
        for act in activities_completed.data:
            total_income += school_prices.get(act.get('school_id'), 0)

except Exception as e:
    st.error(f"שגיאה בטעינת נתונים: {str(e)}")
    activities_today = type('obj', (object,), {'data': []})()
    activities_month = type('obj', (object,), {'data': []})()
    employees = type('obj', (object,), {'data': []})()
    schools = type('obj', (object,), {'data': []})()
    low_stock = []
    total_income = 0

# === KPI Cards ===
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div style='background: white; padding: 1.25rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid #3B82F6;'>
        <div style='font-size: 0.8rem; color: #6B7280; margin-bottom: 0.5rem;'>📅 פעילויות היום</div>
        <div style='font-size: 2rem; font-weight: 700; color: #1A2840;'>{len(activities_today.data) if activities_today.data else 0}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background: white; padding: 1.25rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid #10B981;'>
        <div style='font-size: 0.8rem; color: #6B7280; margin-bottom: 0.5rem;'>📆 פעילויות החודש</div>
        <div style='font-size: 2rem; font-weight: 700; color: #1A2840;'>{len(activities_month.data) if activities_month.data else 0}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style='background: white; padding: 1.25rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid #047857;'>
        <div style='font-size: 0.8rem; color: #6B7280; margin-bottom: 0.5rem;'>💰 הכנסות החודש</div>
        <div style='font-size: 2rem; font-weight: 700; color: #047857;'>₪{total_income:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style='background: white; padding: 1.25rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid #6B7280;'>
        <div style='font-size: 0.8rem; color: #6B7280; margin-bottom: 0.5rem;'>👥 עובדים פעילים</div>
        <div style='font-size: 2rem; font-weight: 700; color: #1A2840;'>{len(employees.data) if employees.data else 0}</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    alert_color = "#EF4444" if low_stock else "#10B981"
    alert_icon = "⚠️" if low_stock else "✅"
    st.markdown(f"""
    <div style='background: white; padding: 1.25rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid {alert_color};'>
        <div style='font-size: 0.8rem; color: #6B7280; margin-bottom: 0.5rem;'>{alert_icon} התראות ציוד</div>
        <div style='font-size: 2rem; font-weight: 700; color: {alert_color};'>{len(low_stock)}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# === גרפים ===
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #E5E7EB;'>
        <h3 style='margin: 0 0 1rem 0; font-size: 1rem; color: #374151;'>📈 פעילויות לפי חודש</h3>
    """, unsafe_allow_html=True)
    
    try:
        six_months_ago = (datetime.now() - timedelta(days=180)).date()
        activities_history = supabase.table("activities").select("date, status").gte("date", str(six_months_ago)).execute()
        
        if activities_history.data:
            df = pd.DataFrame(activities_history.data)
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.strftime('%Y-%m')
            monthly = df.groupby('month').size().reset_index(name='count')
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=monthly['month'],
                y=monthly['count'],
                marker_color='#10B981',
                marker_line_color='#047857',
                marker_line_width=1
            ))
            fig.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                height=250,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#F3F4F6')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("אין מספיק נתונים")
    except:
        st.info("אין מספיק נתונים")
    
    st.markdown("</div>", unsafe_allow_html=True)

with col_chart2:
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #E5E7EB;'>
        <h3 style='margin: 0 0 1rem 0; font-size: 1rem; color: #374151;'>🏫 הכנסות לפי בית ספר</h3>
    """, unsafe_allow_html=True)
    
    try:
        if activities_completed.data and schools.data:
            school_names = {s['id']: s['name'] for s in schools.data}
            school_prices = {s['id']: s['price_per_day'] for s in schools.data}
            
            income_by_school = {}
            for act in activities_completed.data:
                sid = act.get('school_id')
                if sid:
                    name = school_names.get(sid, 'לא ידוע')
                    income_by_school[name] = income_by_school.get(name, 0) + school_prices.get(sid, 0)
            
            if income_by_school:
                df_income = pd.DataFrame([
                    {'school': k, 'income': v} for k, v in income_by_school.items()
                ]).sort_values('income', ascending=True)
                
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    y=df_income['school'],
                    x=df_income['income'],
                    orientation='h',
                    marker_color='#3B82F6'
                ))
                fig2.update_layout(
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=250,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=True, gridcolor='#F3F4F6'),
                    yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("אין נתוני הכנסות")
        else:
            st.info("אין נתוני הכנסות")
    except:
        st.info("אין מספיק נתונים")
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# === טבלאות ===
col_table, col_alerts = st.columns([2, 1])

with col_table:
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #E5E7EB;'>
        <h3 style='margin: 0 0 1rem 0; font-size: 1rem; color: #374151;'>📅 פעילויות קרובות</h3>
    """, unsafe_allow_html=True)
    
    try:
        end_date = (datetime.now() + timedelta(days=7)).date()
        upcoming = supabase.table("activities") \
            .select("*, schools(name), users(full_name)") \
            .gte("date", str(today)) \
            .lte("date", str(end_date)) \
            .order("date") \
            .limit(10) \
            .execute()
        
        if upcoming.data:
            rows = []
            for act in upcoming.data:
                status_badge = {
                    'planned': '🟡 מתוכנן',
                    'confirmed': '🟢 מאושר',
                    'completed': '✅ הושלם',
                    'cancelled': '🔴 בוטל'
                }.get(act['status'], act['status'])
                
                rows.append({
                    'תאריך': act['date'],
                    'בית ספר': act['schools']['name'] if act.get('schools') else '-',
                    'עובד': act['users']['full_name'] if act.get('users') else '❌ לא שובץ',
                    'שעות': f"{act['time_start'][:5]} - {act['time_end'][:5]}",
                    'סטטוס': status_badge
                })
            
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("אין פעילויות קרובות")
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

with col_alerts:
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #E5E7EB; height: 100%;'>
        <h3 style='margin: 0 0 1rem 0; font-size: 1rem; color: #374151;'>🚨 התראות</h3>
    """, unsafe_allow_html=True)
    
    # התראות ציוד
    if low_stock:
        for item in low_stock[:5]:
            st.markdown(f"""
            <div style='background: #FEF2F2; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem; border-right: 3px solid #EF4444;'>
                <div style='font-weight: 600; color: #991B1B; font-size: 0.9rem;'>⚠️ {item['name']}</div>
                <div style='font-size: 0.8rem; color: #6B7280;'>נותרו {item['quantity_available']} יח' (מינימום: {item['min_threshold']})</div>
            </div>
            """, unsafe_allow_html=True)
    
    # פעילויות ללא עובד
    try:
        unassigned = supabase.table("activities").select("*, schools(name)").is_("employee_id", "null").gte("date", str(today)).execute()
        if unassigned.data:
            for act in unassigned.data[:3]:
                st.markdown(f"""
                <div style='background: #FEF3C7; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem; border-right: 3px solid #F59E0B;'>
                    <div style='font-weight: 600; color: #92400E; font-size: 0.9rem;'>👷 חסר שיבוץ עובד</div>
                    <div style='font-size: 0.8rem; color: #6B7280;'>{act['date']} - {act['schools']['name'] if act.get('schools') else '-'}</div>
                </div>
                """, unsafe_allow_html=True)
    except:
        pass
    
    if not low_stock:
        st.markdown("""
        <div style='background: #D1FAE5; padding: 0.75rem; border-radius: 8px; border-right: 3px solid #10B981;'>
            <div style='font-weight: 600; color: #065F46; font-size: 0.9rem;'>✅ הכל תקין</div>
            <div style='font-size: 0.8rem; color: #6B7280;'>אין התראות פעילות</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
