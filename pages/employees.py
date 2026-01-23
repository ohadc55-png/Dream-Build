import streamlit as st
from utils.auth import require_role, create_employee_by_manager
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
from utils.nav import render_sidebar
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

# === הגדרות עמוד ===
st.set_page_config(page_title="ניהול עובדים | Dream & Build", page_icon="👥", layout="wide")
apply_custom_css()
render_sidebar()

# === וידוא הרשאות ===
user = require_role('manager')

# === כותרת ===
st.markdown("""
<h1 style='margin-bottom: 0;'>👥 ניהול עובדים ושכר</h1>
<p style='color: #6B7280; margin-top: 0.25rem;'>ניהול צוות, תנאי העסקה וחישוב שכר</p>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# === טאבים ===
tab1, tab2, tab3 = st.tabs(["📋 רשימת עובדים", "💰 חישוב שכר", "➕ הוספת עובד"])

# ========================================
# טאב 1: רשימת עובדים
# ========================================
with tab1:
    # פילטרים
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        search = st.text_input("🔍 חיפוש", placeholder="שם או אימייל...")
    with col_f2:
        status_filter = st.selectbox("סטטוס", ["הכל", "פעיל", "לא פעיל"])
    
    try:
        # שליפת עובדים
        query = supabase.table("users").select("*").eq("role", "employee").order("full_name")
        if search:
            query = query.or_(f"full_name.ilike.%{search}%,email.ilike.%{search}%")
        if status_filter == "פעיל":
            query = query.eq("status", "active")
        elif status_filter == "לא פעיל":
            query = query.eq("status", "inactive")
        
        employees = query.execute()
        
        # שליפת פעילויות לסטטיסטיקה
        month_start = datetime.now().replace(day=1).date()
        activities = supabase.table("activities").select("employee_id, status").gte("date", str(month_start)).execute()
        
        # חישוב פעילויות לכל עובד
        emp_activities = {}
        emp_completed = {}
        if activities.data:
            for act in activities.data:
                eid = act['employee_id']
                if eid:
                    emp_activities[eid] = emp_activities.get(eid, 0) + 1
                    if act['status'] == 'completed':
                        emp_completed[eid] = emp_completed.get(eid, 0) + 1
        
        if employees.data:
            # סטטיסטיקות
            col_s1, col_s2, col_s3 = st.columns(3)
            total_emps = len(employees.data)
            active_emps = len([e for e in employees.data if e.get('status') == 'active'])
            total_month_activities = sum(emp_activities.values())
            
            with col_s1:
                st.metric("סה״כ עובדים", total_emps)
            with col_s2:
                st.metric("עובדים פעילים", active_emps)
            with col_s3:
                st.metric("פעילויות החודש", total_month_activities)
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            # טבלת עובדים
            rows = []
            for emp in employees.data:
                eid = emp['id']
                status_badge = "✅ פעיל" if emp.get('status') == 'active' else "❌ לא פעיל"
                
                rows.append({
                    'id': eid,
                    'שם מלא': emp.get('full_name', '-'),
                    'אימייל': emp.get('email', '-'),
                    'טלפון': emp.get('phone', '-') or '-',
                    'תעריף שעתי': f"₪{emp.get('hourly_rate', 0) or 0:,.0f}",
                    'תעריף יומי': f"₪{emp.get('daily_rate', 0) or 0:,.0f}",
                    'פעילויות החודש': emp_activities.get(eid, 0),
                    'הושלמו': emp_completed.get(eid, 0),
                    'סטטוס': status_badge
                })
            
            df = pd.DataFrame(rows)
            st.dataframe(df[['שם מלא', 'טלפון', 'תעריף שעתי', 'תעריף יומי', 'פעילויות החודש', 'הושלמו', 'סטטוס']], 
                        use_container_width=True, hide_index=True)
            
            # === עריכת עובד ===
            st.markdown("---")
            st.markdown("### ⚙️ עריכת עובד")
            
            emp_names = [e['full_name'] for e in employees.data]
            selected_name = st.selectbox("בחר עובד", emp_names)
            
            if selected_name:
                selected_emp = next(e for e in employees.data if e['full_name'] == selected_name)
                
                with st.form("edit_employee"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edit_name = st.text_input("שם מלא", value=selected_emp.get('full_name', ''))
                        edit_phone = st.text_input("טלפון", value=selected_emp.get('phone', '') or '')
                        edit_hourly = st.number_input("תעריף שעתי (₪)", value=float(selected_emp.get('hourly_rate', 0) or 0), min_value=0.0)
                    
                    with col2:
                        edit_email = st.text_input("אימייל", value=selected_emp.get('email', ''))
                        edit_status = st.selectbox("סטטוס", ['active', 'inactive'], 
                                                   index=0 if selected_emp.get('status') == 'active' else 1,
                                                   format_func=lambda x: 'פעיל' if x == 'active' else 'לא פעיל')
                        edit_daily = st.number_input("תעריף יומי (₪)", value=float(selected_emp.get('daily_rate', 0) or 0), min_value=0.0)
                    
                    if st.form_submit_button("💾 שמור שינויים", use_container_width=True):
                        supabase.table("users").update({
                            "full_name": edit_name,
                            "phone": edit_phone or None,
                            "hourly_rate": edit_hourly,
                            "daily_rate": edit_daily,
                            "status": edit_status
                        }).eq("id", selected_emp['id']).execute()
                        st.success("✅ נשמר!")
                        st.rerun()
        else:
            st.info("אין עובדים במערכת")
            
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")

# ========================================
# טאב 2: חישוב שכר
# ========================================
with tab2:
    st.markdown("### 💰 חישוב שכר לפי פעילויות")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input("מתאריך", value=datetime.now().replace(day=1).date(), key="salary_start")
    with col_d2:
        end_date = st.date_input("עד תאריך", value=datetime.now().date(), key="salary_end")
    
    if st.button("🧮 חשב שכר", use_container_width=True):
        try:
            # שליפת עובדים
            employees = supabase.table("users").select("id, full_name, hourly_rate, daily_rate").eq("role", "employee").execute()
            
            # שליפת פעילויות שהושלמו
            activities = supabase.table("activities") \
                .select("employee_id, time_start, time_end") \
                .gte("date", str(start_date)) \
                .lte("date", str(end_date)) \
                .eq("status", "completed") \
                .execute()
            
            if employees.data:
                salary_data = []
                
                for emp in employees.data:
                    eid = emp['id']
                    emp_acts = [a for a in activities.data if a['employee_id'] == eid] if activities.data else []
                    count = len(emp_acts)
                    
                    # חישוב שכר
                    salary = 0
                    method = "-"
                    
                    if emp.get('daily_rate') and emp['daily_rate'] > 0:
                        salary = count * emp['daily_rate']
                        method = "יומי"
                    elif emp.get('hourly_rate') and emp['hourly_rate'] > 0:
                        # חישוב שעות (הערכה של 5 שעות לפעילות)
                        hours = count * 5
                        salary = hours * emp['hourly_rate']
                        method = "שעתי"
                    
                    salary_data.append({
                        'עובד': emp['full_name'],
                        'פעילויות': count,
                        'שיטת חישוב': method,
                        'שכר': salary
                    })
                
                df_salary = pd.DataFrame(salary_data)
                
                # סיכום
                total_salary = df_salary['שכר'].sum()
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.dataframe(df_salary.style.format({'שכר': '₪{:,.0f}'}), use_container_width=True, hide_index=True)
                with col2:
                    st.markdown(f"""
                    <div style='background: #D1FAE5; padding: 1.5rem; border-radius: 12px; text-align: center;'>
                        <div style='font-size: 0.9rem; color: #065F46;'>סה״כ לתשלום</div>
                        <div style='font-size: 2rem; font-weight: 700; color: #047857;'>₪{total_salary:,.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # גרף
                if df_salary['שכר'].sum() > 0:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=df_salary['עובד'],
                        y=df_salary['שכר'],
                        marker_color='#10B981'
                    ))
                    fig.update_layout(title="שכר לפי עובד", height=300)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("אין עובדים במערכת")
                
        except Exception as e:
            st.error(f"שגיאה: {str(e)}")

# ========================================
# טאב 3: הוספת עובד
# ========================================
with tab3:
    st.markdown("### ➕ הוספת עובד חדש")
    
    with st.form("add_employee"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("שם מלא *")
            new_email = st.text_input("אימייל *")
            new_phone = st.text_input("טלפון")
        
        with col2:
            new_hourly = st.number_input("תעריף שעתי (₪)", min_value=0.0, value=0.0)
            new_daily = st.number_input("תעריף יומי (₪)", min_value=0.0, value=0.0)
        
        st.info("💡 העובד יירשם עם סיסמה זמנית. הסיסמה תוצג לאחר ההוספה - העבר אותה לעובד כדי שיוכל להתחבר")
        
        if st.form_submit_button("➕ הוסף עובד", use_container_width=True):
            if not new_name or not new_email:
                st.error("❌ נא למלא שם ואימייל")
            else:
                with st.spinner("מוסיף עובד..."):
                    result = create_employee_by_manager(
                        email=new_email,
                        full_name=new_name,
                        phone=new_phone,
                        hourly_rate=new_hourly,
                        daily_rate=new_daily
                    )
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                    st.balloons()
                    
                    # הצגת סיסמה זמנית
                    st.markdown("---")
                    st.markdown("### 🔑 פרטי התחברות לעובד")
                    st.markdown(f"""
                    <div style='background: #FEF3C7; padding: 1.5rem; border-radius: 12px; border-right: 4px solid #F59E0B;'>
                        <div style='font-weight: 600; color: #92400E; margin-bottom: 0.5rem;'>⚠️ חשוב: העבר את הפרטים הבאים לעובד</div>
                        <div style='margin-bottom: 0.5rem;'><strong>אימייל:</strong> {new_email}</div>
                        <div style='margin-bottom: 0.5rem;'><strong>סיסמה זמנית:</strong> <code style='background: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 1.1rem;'>{result['temp_password']}</code></div>
                        <div style='font-size: 0.9rem; color: #78350F; margin-top: 0.5rem;'>💡 העובד יוכל לשנות את הסיסמה לאחר ההתחברות הראשונה</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")
