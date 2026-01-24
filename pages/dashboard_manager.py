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

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# === טאבים ===
tab_dashboard, tab_import, tab_admin = st.tabs(["📊 דשבורד", "📥 ייבוא נתונים", "⚙️ ניהול מערכת"])

# ========================================
# טאב 1: דשבורד
# ========================================
with tab_dashboard:
    try:
        today = datetime.now().date()
        month_start = today.replace(day=1)
        
        activities_today = supabase.table("activities").select("*").eq("date", str(today)).execute()
        activities_month = supabase.table("activities").select("*").gte("date", str(month_start)).execute()
        activities_completed = supabase.table("activities").select("*").eq("status", "completed").gte("date", str(month_start)).execute()
        employees = supabase.table("users").select("*").eq("role", "employee").eq("status", "active").execute()
        schools = supabase.table("schools").select("*").eq("status", "active").execute()
        equipment = supabase.table("equipment").select("*").execute()
        low_stock = [item for item in equipment.data if item.get('quantity_available', 0) <= item.get('min_threshold', 0)]
        
        total_income = 0
        if activities_completed.data and schools.data:
            school_prices = {s['id']: s['price_per_day'] for s in schools.data}
            for act in activities_completed.data:
                total_income += school_prices.get(act.get('school_id'), 0)
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")
        activities_today = type('obj', (object,), {'data': []})()
        activities_month = type('obj', (object,), {'data': []})()
        employees = type('obj', (object,), {'data': []})()
        schools = type('obj', (object,), {'data': []})()
        low_stock = []
        total_income = 0

    # KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div style='background: white; padding: 1.25rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid #3B82F6;'>
            <div style='font-size: 0.8rem; color: #6B7280;'>📅 פעילויות היום</div>
            <div style='font-size: 2rem; font-weight: 700; color: #1A2840;'>{len(activities_today.data) if activities_today.data else 0}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: white; padding: 1.25rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid #10B981;'>
            <div style='font-size: 0.8rem; color: #6B7280;'>📆 פעילויות החודש</div>
            <div style='font-size: 2rem; font-weight: 700; color: #1A2840;'>{len(activities_month.data) if activities_month.data else 0}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: white; padding: 1.25rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid #047857;'>
            <div style='font-size: 0.8rem; color: #6B7280;'>💰 הכנסות החודש</div>
            <div style='font-size: 2rem; font-weight: 700; color: #047857;'>₪{total_income:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: white; padding: 1.25rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid #6B7280;'>
            <div style='font-size: 0.8rem; color: #6B7280;'>👥 מדריכים פעילים</div>
            <div style='font-size: 2rem; font-weight: 700; color: #1A2840;'>{len(employees.data) if employees.data else 0}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        alert_color = "#EF4444" if low_stock else "#10B981"
        st.markdown(f"""
        <div style='background: white; padding: 1.25rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid {alert_color};'>
            <div style='font-size: 0.8rem; color: #6B7280;'>⚠️ התראות ציוד</div>
            <div style='font-size: 2rem; font-weight: 700; color: {alert_color};'>{len(low_stock)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # פעילויות קרובות והתראות
    col_table, col_alerts = st.columns([2, 1])
    
    with col_table:
        st.markdown("#### 📅 פעילויות קרובות")
        try:
            end_date = (datetime.now() + timedelta(days=7)).date()
            upcoming = supabase.table("activities").select("*, schools(name), users(full_name)").gte("date", str(today)).lte("date", str(end_date)).order("date").limit(8).execute()
            
            if upcoming.data:
                for act in upcoming.data:
                    status_icon = {'planned': '🟡', 'confirmed': '🟢', 'completed': '✅', 'cancelled': '🔴'}.get(act['status'], '⚪')
                    emp_name = act['users']['full_name'] if act.get('users') else '❌ לא שובץ'
                    school_name = act['schools']['name'] if act.get('schools') else '-'
                    
                    st.markdown(f"""
                    <div style='background: white; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem; border-right: 3px solid #3B82F6;'>
                        <span style='font-weight: 600;'>{status_icon} {act['date']}</span>
                        <span style='color: #6B7280; margin-right: 1rem;'>🏫 {school_name} | 👷 {emp_name}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("אין פעילויות קרובות")
        except Exception as e:
            st.error(f"שגיאה: {str(e)}")
    
    with col_alerts:
        st.markdown("#### 🚨 התראות")
        
        if low_stock:
            for item in low_stock[:5]:
                st.markdown(f"""
                <div style='background: #FEF2F2; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem; border-right: 3px solid #EF4444;'>
                    <div style='font-weight: 600; color: #991B1B;'>⚠️ {item['name']}</div>
                    <div style='font-size: 0.8rem; color: #6B7280;'>נותרו {item['quantity_available']} יח'</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background: #D1FAE5; padding: 0.75rem; border-radius: 8px; border-right: 3px solid #10B981;'>
                <div style='font-weight: 600; color: #065F46;'>✅ הכל תקין</div>
            </div>
            """, unsafe_allow_html=True)

# ========================================
# טאב 2: ייבוא נתונים
# ========================================
with tab_import:
    st.markdown("### 📥 ייבוא נתונים היסטוריים")
    st.info("💡 העלה קובץ Excel או CSV עם נתונים היסטוריים לייבוא למערכת")
    
    import_type = st.selectbox("סוג הנתונים לייבוא", 
        ["בתי ספר", "עובדים/מדריכים", "פעילויות היסטוריות", "רשומות כספיות"])
    
    instructions = {
        "בתי ספר": "**עמודות:** name (חובה), contact_person, phone, email, price_per_day (חובה), address",
        "עובדים/מדריכים": "**עמודות:** full_name (חובה), email (חובה), phone, hourly_rate, daily_rate",
        "פעילויות היסטוריות": "**עמודות:** date (YYYY-MM-DD), school_name, employee_name, time_start, time_end, status",
        "רשומות כספיות": "**עמודות:** date (YYYY-MM-DD), type (income/expense), amount, category, description"
    }
    
    st.markdown(instructions[import_type])
    
    uploaded_file = st.file_uploader("📁 העלה קובץ", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.markdown("#### 👀 תצוגה מקדימה:")
            st.dataframe(df.head(10), use_container_width=True)
            st.markdown(f"**סה״כ שורות:** {len(df)}")
            
            if st.button("🚀 ייבא נתונים", use_container_width=True):
                success_count = 0
                error_count = 0
                
                with st.spinner("מייבא..."):
                    if import_type == "בתי ספר":
                        for _, row in df.iterrows():
                            try:
                                supabase.table("schools").insert({
                                    "name": row.get('name'),
                                    "contact_person": row.get('contact_person') if pd.notna(row.get('contact_person')) else None,
                                    "phone": str(row.get('phone', '')) if pd.notna(row.get('phone')) else None,
                                    "email": row.get('email') if pd.notna(row.get('email')) else None,
                                    "price_per_day": float(row.get('price_per_day', 0)),
                                    "address": row.get('address') if pd.notna(row.get('address')) else None,
                                    "status": "active"
                                }).execute()
                                success_count += 1
                            except:
                                error_count += 1
                    
                    elif import_type == "עובדים/מדריכים":
                        for _, row in df.iterrows():
                            try:
                                supabase.table("users").insert({
                                    "id": row.get('email'),
                                    "email": row.get('email'),
                                    "full_name": row.get('full_name'),
                                    "phone": str(row.get('phone', '')) if pd.notna(row.get('phone')) else None,
                                    "role": "employee",
                                    "status": "active",
                                    "hourly_rate": float(row.get('hourly_rate', 0)) if pd.notna(row.get('hourly_rate')) else 0,
                                    "daily_rate": float(row.get('daily_rate', 0)) if pd.notna(row.get('daily_rate')) else 0
                                }).execute()
                                success_count += 1
                            except:
                                error_count += 1
                    
                    elif import_type == "פעילויות היסטוריות":
                        schools_db = supabase.table("schools").select("id, name").execute()
                        employees_db = supabase.table("users").select("id, full_name").eq("role", "employee").execute()
                        school_map = {s['name']: s['id'] for s in schools_db.data} if schools_db.data else {}
                        emp_map = {e['full_name']: e['id'] for e in employees_db.data} if employees_db.data else {}
                        
                        for _, row in df.iterrows():
                            try:
                                school_id = school_map.get(row.get('school_name'))
                                emp_id = emp_map.get(row.get('employee_name'))
                                if school_id and emp_id:
                                    supabase.table("activities").insert({
                                        "school_id": school_id,
                                        "employee_id": emp_id,
                                        "date": str(row.get('date'))[:10],
                                        "time_start": str(row.get('time_start', '08:00')),
                                        "time_end": str(row.get('time_end', '14:00')),
                                        "status": row.get('status', 'completed'),
                                        "confirmed_by_employee": True
                                    }).execute()
                                    success_count += 1
                                else:
                                    error_count += 1
                            except:
                                error_count += 1
                    
                    elif import_type == "רשומות כספיות":
                        for _, row in df.iterrows():
                            try:
                                supabase.table("financial_records").insert({
                                    "date": str(row.get('date'))[:10],
                                    "type": row.get('type', 'expense'),
                                    "amount": float(row.get('amount', 0)),
                                    "category": row.get('category', 'אחר') if pd.notna(row.get('category')) else 'אחר',
                                    "description": row.get('description') if pd.notna(row.get('description')) else None,
                                    "created_by": user['id']
                                }).execute()
                                success_count += 1
                            except:
                                error_count += 1
                
                if success_count > 0:
                    st.success(f"✅ יובאו {success_count} רשומות!")
                    st.balloons()
                if error_count > 0:
                    st.warning(f"⚠️ {error_count} שגיאות")
                    
        except Exception as e:
            st.error(f"❌ שגיאה: {str(e)}")
    
    # תבניות להורדה
    st.markdown("---")
    st.markdown("### 📄 הורדת תבניות")
    
    col1, col2 = st.columns(2)
    with col1:
        template_schools = pd.DataFrame({
            'name': ['בית ספר לדוגמה'],
            'contact_person': ['ישראל ישראלי'],
            'phone': ['050-1234567'],
            'email': ['school@example.com'],
            'price_per_day': [1500],
            'address': ['תל אביב']
        })
        st.download_button("📥 תבנית בתי ספר", template_schools.to_csv(index=False).encode('utf-8-sig'), "template_schools.csv", use_container_width=True)
    
    with col2:
        template_activities = pd.DataFrame({
            'date': ['2025-01-15'],
            'school_name': ['שם בית הספר'],
            'employee_name': ['שם המדריך'],
            'time_start': ['08:00'],
            'time_end': ['14:00'],
            'status': ['completed']
        })
        st.download_button("📥 תבנית פעילויות", template_activities.to_csv(index=False).encode('utf-8-sig'), "template_activities.csv", use_container_width=True)

# ========================================
# טאב 3: ניהול מערכת
# ========================================
with tab_admin:
    st.markdown("### ⚙️ ניהול מערכת")
    st.warning("⚠️ פעולות בדף זה הן בלתי הפיכות!")
    
    st.markdown("---")
    st.markdown("### 🗑️ מחיקת נתונים")
    
    delete_type = st.selectbox("בחר מה למחוק", [
        "בחר...",
        "פעילויות ישנות (לפני תאריך)",
        "כל הפעילויות",
        "כל הרשומות הכספיות",
        "כל דיווחי הציוד",
        "🔴 איפוס מלא"
    ])
    
    if delete_type == "פעילויות ישנות (לפני תאריך)":
        delete_before = st.date_input("מחק פעילויות לפני", value=datetime.now().date() - timedelta(days=365))
        st.info(f"ימחקו כל הפעילויות מלפני {delete_before}")
    
    if delete_type != "בחר...":
        st.markdown("---")
        st.markdown("#### ⚠️ אישור מחיקה")
        
        confirm_text = st.text_input("הקלד 'מחק' לאישור:")
        
        col_del1, col_del2 = st.columns(2)
        
        with col_del1:
            if st.button("🗑️ מחק לצמיתות", use_container_width=True, type="primary"):
                if confirm_text != "מחק":
                    st.error("❌ הקלד 'מחק' לאישור")
                else:
                    try:
                        with st.spinner("מוחק..."):
                            if delete_type == "פעילויות ישנות (לפני תאריך)":
                                supabase.table("activities").delete().lt("date", str(delete_before)).execute()
                                st.success(f"✅ נמחקו פעילויות מלפני {delete_before}")
                            elif delete_type == "כל הפעילויות":
                                supabase.table("activities").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                                st.success("✅ נמחקו כל הפעילויות")
                            elif delete_type == "כל הרשומות הכספיות":
                                supabase.table("financial_records").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                                st.success("✅ נמחקו כל הרשומות")
                            elif delete_type == "כל דיווחי הציוד":
                                supabase.table("equipment_reports").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                                st.success("✅ נמחקו כל הדיווחים")
                            elif delete_type == "🔴 איפוס מלא":
                                supabase.table("equipment_reports").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                                supabase.table("financial_records").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                                supabase.table("activities").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                                supabase.table("school_budgets").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                                st.success("✅ המערכת אופסה")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ שגיאה: {str(e)}")
        
        with col_del2:
            if st.button("❌ ביטול", use_container_width=True):
                st.rerun()
    
    # סטטיסטיקות
    st.markdown("---")
    st.markdown("### 📊 סטטיסטיקות מערכת")
    
    try:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            count = supabase.table("schools").select("id").execute()
            st.metric("בתי ספר", len(count.data) if count.data else 0)
        with col2:
            count = supabase.table("users").select("id").execute()
            st.metric("משתמשים", len(count.data) if count.data else 0)
        with col3:
            count = supabase.table("activities").select("id").execute()
            st.metric("פעילויות", len(count.data) if count.data else 0)
        with col4:
            count = supabase.table("equipment").select("id").execute()
            st.metric("פריטי ציוד", len(count.data) if count.data else 0)
    except:
        pass
