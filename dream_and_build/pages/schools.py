import streamlit as st
from utils.auth import require_role
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
from utils.nav import render_sidebar
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# === הגדרות עמוד ===
st.set_page_config(page_title="ניהול בתי ספר | Dream & Build", page_icon="🏫", layout="wide")
apply_custom_css()
render_sidebar()

# === וידוא הרשאות ===
user = require_role('manager')

# === כותרת ===
st.markdown("""
<h1 style='margin-bottom: 0;'>🏫 ניהול בתי ספר</h1>
<p style='color: #6B7280; margin-top: 0.25rem;'>ניהול לקוחות, תקציבים ופעילויות</p>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# === טאבים ===
tab1, tab2, tab3 = st.tabs(["📋 רשימה ותקציבים", "➕ הוספת בית ספר", "📊 ניתוח"])

# ========================================
# טאב 1: רשימה ותקציבים
# ========================================
with tab1:
    try:
        # שליפת בתי ספר
        schools = supabase.table("schools").select("*").order("name").execute()
        
        # שליפת תקציבים
        current_year = datetime.now().year
        budgets = supabase.table("school_budgets").select("*").eq("year", current_year).execute()
        budgets_dict = {b['school_id']: b for b in budgets.data} if budgets.data else {}
        
        # שליפת פעילויות שהושלמו השנה
        year_start = f"{current_year}-01-01"
        activities = supabase.table("activities").select("school_id, status").gte("date", year_start).in_("status", ["completed", "confirmed"]).execute()
        
        # חישוב פעילויות לכל בית ספר
        activities_count = {}
        if activities.data:
            for act in activities.data:
                sid = act['school_id']
                activities_count[sid] = activities_count.get(sid, 0) + 1
        
        if schools.data:
            # יצירת טבלת סיכום
            rows = []
            for school in schools.data:
                sid = school['id']
                act_count = activities_count.get(sid, 0)
                price = school.get('price_per_day', 0) or 0
                
                # חישוב ניצול תקציב (אוטומטי!)
                used_budget = act_count * price
                
                # תקציב מוגדר
                budget_info = budgets_dict.get(sid, {})
                total_budget = budget_info.get('budget_amount', 0) or 0
                remaining = total_budget - used_budget
                usage_pct = (used_budget / total_budget * 100) if total_budget > 0 else 0
                
                rows.append({
                    'id': sid,
                    'שם': school['name'],
                    'איש קשר': school.get('contact_person', '-') or '-',
                    'טלפון': school.get('phone', '-') or '-',
                    'מחיר ליום': f"₪{price:,}",
                    'פעילויות': act_count,
                    'ניצול תקציב': f"₪{used_budget:,}",
                    'תקציב כולל': f"₪{total_budget:,}" if total_budget > 0 else 'לא הוגדר',
                    'יתרה': remaining,
                    'אחוז': usage_pct,
                    'סטטוס': school.get('status', 'active')
                })
            
            df = pd.DataFrame(rows)
            
            # === סטטיסטיקות מהירות ===
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("סה״כ בתי ספר", len(schools.data))
            with col2:
                total_activities = sum(activities_count.values())
                st.metric("סה״כ פעילויות השנה", total_activities)
            with col3:
                total_income = sum([activities_count.get(s['id'], 0) * (s.get('price_per_day', 0) or 0) for s in schools.data])
                st.metric("סה״כ הכנסות", f"₪{total_income:,}")
            with col4:
                active_schools = len([s for s in schools.data if s.get('status') == 'active'])
                st.metric("בתי ספר פעילים", active_schools)
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            # === טבלה ראשית ===
            st.markdown("### 📋 רשימת בתי ספר")
            
            # הצגת טבלה עם עמודות נבחרות
            display_df = df[['שם', 'איש קשר', 'טלפון', 'מחיר ליום', 'פעילויות', 'ניצול תקציב', 'תקציב כולל']].copy()
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            
            # === ניהול תקציב ועריכה ===
            st.markdown("### ⚙️ ניהול בית ספר")
            
            col_select, col_actions = st.columns([1, 2])
            
            with col_select:
                school_names = [s['name'] for s in schools.data]
                selected_name = st.selectbox("בחר בית ספר", school_names)
            
            if selected_name:
                selected_school = next(s for s in schools.data if s['name'] == selected_name)
                selected_id = selected_school['id']
                selected_budget = budgets_dict.get(selected_id, {})
                
                with col_actions:
                    # מידע על הבית ספר הנבחר
                    act_count = activities_count.get(selected_id, 0)
                    price = selected_school.get('price_per_day', 0) or 0
                    used = act_count * price
                    budget_amt = selected_budget.get('budget_amount', 0) or 0
                    
                    st.markdown(f"""
                    <div style='background: #F0FDF4; padding: 1rem; border-radius: 10px; border: 1px solid #BBF7D0;'>
                        <div style='font-weight: 600; color: #166534; margin-bottom: 0.5rem;'>📊 סיכום אוטומטי</div>
                        <div style='display: flex; gap: 2rem;'>
                            <div><span style='color: #6B7280;'>פעילויות:</span> <strong>{act_count}</strong></div>
                            <div><span style='color: #6B7280;'>נוצל:</span> <strong>₪{used:,}</strong></div>
                            <div><span style='color: #6B7280;'>תקציב:</span> <strong>₪{budget_amt:,}</strong></div>
                            <div><span style='color: #6B7280;'>יתרה:</span> <strong style='color: {"#10B981" if budget_amt - used >= 0 else "#EF4444"};'>₪{budget_amt - used:,}</strong></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # טאבים לעריכה
                edit_tab1, edit_tab2 = st.tabs(["✏️ פרטי בית ספר", "💰 הגדרת תקציב"])
                
                with edit_tab1:
                    with st.form("edit_school_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            edit_name = st.text_input("שם", value=selected_school['name'])
                            edit_contact = st.text_input("איש קשר", value=selected_school.get('contact_person', '') or '')
                            edit_phone = st.text_input("טלפון", value=selected_school.get('phone', '') or '')
                        with col2:
                            edit_email = st.text_input("אימייל", value=selected_school.get('email', '') or '')
                            edit_price = st.number_input("מחיר ליום (₪)", value=float(selected_school.get('price_per_day', 0) or 0), min_value=0.0, step=100.0)
                            edit_status = st.selectbox("סטטוס", ['active', 'inactive'], 
                                                       index=0 if selected_school.get('status') == 'active' else 1,
                                                       format_func=lambda x: '✅ פעיל' if x == 'active' else '❌ לא פעיל')
                        
                        edit_address = st.text_input("כתובת", value=selected_school.get('address', '') or '')
                        edit_notes = st.text_area("הערות", value=selected_school.get('notes', '') or '')
                        
                        if st.form_submit_button("💾 שמור שינויים", use_container_width=True):
                            supabase.table("schools").update({
                                "name": edit_name,
                                "contact_person": edit_contact,
                                "phone": edit_phone,
                                "email": edit_email,
                                "price_per_day": edit_price,
                                "status": edit_status,
                                "address": edit_address,
                                "notes": edit_notes
                            }).eq("id", selected_id).execute()
                            st.success("✅ נשמר בהצלחה!")
                            st.rerun()
                
                with edit_tab2:
                    st.markdown("#### 💰 הגדרת תקציב שנתי")
                    st.info("💡 התקציב מתעדכן אוטומטית לפי פעילויות שבוצעו")
                    
                    with st.form("budget_form"):
                        budget_amount = st.number_input(
                            "תקציב שנתי (₪)", 
                            value=float(selected_budget.get('budget_amount', 0) or 0),
                            min_value=0.0,
                            step=1000.0
                        )
                        alert_threshold = st.number_input(
                            "התראה כשנותרו (₪)",
                            value=float(selected_budget.get('alert_threshold', 1000) or 1000),
                            min_value=0.0,
                            step=500.0
                        )
                        
                        if st.form_submit_button("💾 שמור תקציב", use_container_width=True):
                            budget_data = {
                                "school_id": selected_id,
                                "budget_amount": budget_amount,
                                "year": current_year,
                                "alert_threshold": alert_threshold
                            }
                            
                            if selected_budget:
                                # עדכון
                                supabase.table("school_budgets").update(budget_data).eq("id", selected_budget['id']).execute()
                            else:
                                # יצירה
                                supabase.table("school_budgets").insert(budget_data).execute()
                            
                            st.success("✅ התקציב נשמר!")
                            st.rerun()
                    
                    # Progress bar
                    if budget_amt > 0:
                        progress = min(used / budget_amt, 1.0)
                        color = "#10B981" if progress < 0.8 else "#F59E0B" if progress < 1.0 else "#EF4444"
                        st.markdown(f"""
                        <div style='margin-top: 1rem;'>
                            <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                                <span style='font-size: 0.85rem; color: #6B7280;'>ניצול תקציב</span>
                                <span style='font-size: 0.85rem; font-weight: 600; color: {color};'>{progress*100:.1f}%</span>
                            </div>
                            <div style='background: #E5E7EB; border-radius: 10px; height: 10px; overflow: hidden;'>
                                <div style='background: {color}; height: 100%; width: {progress*100}%; border-radius: 10px;'></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("אין בתי ספר במערכת. הוסף בית ספר ראשון!")
            
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")

# ========================================
# טאב 2: הוספת בית ספר
# ========================================
with tab2:
    st.markdown("### ➕ הוספת בית ספר חדש")
    
    with st.form("add_school_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("שם בית הספר *")
            new_contact = st.text_input("איש קשר")
            new_phone = st.text_input("טלפון")
        
        with col2:
            new_email = st.text_input("אימייל")
            new_price = st.number_input("מחיר ליום (₪) *", min_value=0.0, value=1000.0, step=100.0)
            new_address = st.text_input("כתובת")
        
        new_notes = st.text_area("הערות")
        
        # תקציב ראשוני (אופציונלי)
        st.markdown("---")
        st.markdown("#### 💰 תקציב שנתי (אופציונלי)")
        new_budget = st.number_input("תקציב שנתי (₪)", min_value=0.0, value=0.0, step=1000.0)
        
        if st.form_submit_button("➕ הוסף בית ספר", use_container_width=True):
            if not new_name or new_price <= 0:
                st.error("❌ נא למלא שם ומחיר")
            else:
                try:
                    # הוספת בית ספר
                    result = supabase.table("schools").insert({
                        "name": new_name,
                        "contact_person": new_contact or None,
                        "phone": new_phone or None,
                        "email": new_email or None,
                        "price_per_day": new_price,
                        "address": new_address or None,
                        "notes": new_notes or None,
                        "status": "active"
                    }).execute()
                    
                    # הוספת תקציב אם הוזן
                    if new_budget > 0 and result.data:
                        school_id = result.data[0]['id']
                        supabase.table("school_budgets").insert({
                            "school_id": school_id,
                            "budget_amount": new_budget,
                            "year": datetime.now().year,
                            "alert_threshold": 1000
                        }).execute()
                    
                    st.success(f"✅ בית הספר '{new_name}' נוסף בהצלחה!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ שגיאה: {str(e)}")

# ========================================
# טאב 3: ניתוח
# ========================================
with tab3:
    st.markdown("### 📊 ניתוח בתי ספר")
    
    try:
        schools = supabase.table("schools").select("*").eq("status", "active").execute()
        
        if schools.data:
            # שליפת כל הפעילויות
            all_activities = supabase.table("activities").select("school_id, date, status").execute()
            
            if all_activities.data:
                # ניתוח
                df_acts = pd.DataFrame(all_activities.data)
                school_names = {s['id']: s['name'] for s in schools.data}
                school_prices = {s['id']: s.get('price_per_day', 0) or 0 for s in schools.data}
                
                df_acts['school_name'] = df_acts['school_id'].map(school_names)
                df_acts['price'] = df_acts['school_id'].map(school_prices)
                
                # גרף פעילויות לפי בית ספר
                school_counts = df_acts['school_name'].value_counts().reset_index()
                school_counts.columns = ['בית ספר', 'פעילויות']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig1 = go.Figure()
                    fig1.add_trace(go.Pie(
                        labels=school_counts['בית ספר'],
                        values=school_counts['פעילויות'],
                        hole=0.4,
                        marker_colors=['#10B981', '#3B82F6', '#6B7280', '#F59E0B', '#EF4444']
                    ))
                    fig1.update_layout(title="התפלגות פעילויות", height=350)
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # הכנסות לפי בית ספר
                    completed = df_acts[df_acts['status'].isin(['completed', 'confirmed'])]
                    income_by_school = completed.groupby('school_name')['price'].sum().reset_index()
                    income_by_school.columns = ['בית ספר', 'הכנסות']
                    
                    fig2 = go.Figure()
                    fig2.add_trace(go.Bar(
                        x=income_by_school['בית ספר'],
                        y=income_by_school['הכנסות'],
                        marker_color='#047857'
                    ))
                    fig2.update_layout(title="הכנסות לפי בית ספר", height=350)
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("אין פעילויות לניתוח")
        else:
            st.info("אין בתי ספר פעילים")
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")
