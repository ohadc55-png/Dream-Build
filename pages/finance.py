import streamlit as st
from utils.auth import require_role
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
from utils.nav import render_sidebar
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# === הגדרות עמוד ===
st.set_page_config(page_title="דוחות כספיים | Dream & Build", page_icon="💰", layout="wide")
apply_custom_css()
render_sidebar()

# === וידוא הרשאות ===
user = require_role('manager')

# === כותרת ===
st.markdown("""
<h1 style='margin-bottom: 0;'>💰 דוחות כספיים ותקציב</h1>
<p style='color: #6B7280; margin-top: 0.25rem;'>מעקב הכנסות, הוצאות וניצול תקציבים</p>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# === טאבים ===
tab1, tab2, tab3, tab4 = st.tabs(["📊 סיכום", "📈 הכנסות (אוטומטי)", "📉 הוצאות", "➕ הוספת רשומה"])

# ========================================
# טאב 1: סיכום
# ========================================
with tab1:
    # בחירת תקופה
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input("מתאריך", value=datetime.now().replace(day=1).date(), key="sum_start")
    with col_d2:
        end_date = st.date_input("עד תאריך", value=datetime.now().date(), key="sum_end")
    
    try:
        # === הכנסות (מפעילויות) ===
        activities = supabase.table("activities") \
            .select("school_id, status") \
            .gte("date", str(start_date)) \
            .lte("date", str(end_date)) \
            .in_("status", ["completed", "confirmed"]) \
            .execute()
        
        schools = supabase.table("schools").select("id, name, price_per_day").execute()
        school_prices = {s['id']: s.get('price_per_day', 0) or 0 for s in schools.data} if schools.data else {}
        school_names = {s['id']: s['name'] for s in schools.data} if schools.data else {}
        
        total_income = 0
        income_by_school = {}
        if activities.data:
            for act in activities.data:
                sid = act['school_id']
                price = school_prices.get(sid, 0)
                total_income += price
                name = school_names.get(sid, 'לא ידוע')
                income_by_school[name] = income_by_school.get(name, 0) + price
        
        # === הוצאות (ידניות) ===
        expenses = supabase.table("financial_records") \
            .select("*") \
            .eq("type", "expense") \
            .gte("date", str(start_date)) \
            .lte("date", str(end_date)) \
            .execute()
        
        total_expenses = sum([e.get('amount', 0) for e in expenses.data]) if expenses.data else 0
        
        # === הכנסות נוספות (ידניות) ===
        additional_income = supabase.table("financial_records") \
            .select("*") \
            .eq("type", "income") \
            .gte("date", str(start_date)) \
            .lte("date", str(end_date)) \
            .execute()
        
        additional_income_total = sum([e.get('amount', 0) for e in additional_income.data]) if additional_income.data else 0
        
        # === KPIs ===
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid #10B981;'>
                <div style='font-size: 0.85rem; color: #6B7280;'>💵 הכנסות מפעילויות</div>
                <div style='font-size: 2rem; font-weight: 700; color: #047857;'>₪{total_income:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid #3B82F6;'>
                <div style='font-size: 0.85rem; color: #6B7280;'>💰 הכנסות נוספות</div>
                <div style='font-size: 2rem; font-weight: 700; color: #3B82F6;'>₪{additional_income_total:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid #EF4444;'>
                <div style='font-size: 0.85rem; color: #6B7280;'>💸 הוצאות</div>
                <div style='font-size: 2rem; font-weight: 700; color: #EF4444;'>₪{total_expenses:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        net_profit = total_income + additional_income_total - total_expenses
        profit_color = "#047857" if net_profit >= 0 else "#EF4444"
        
        with col4:
            st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #E5E7EB; border-right: 4px solid {profit_color};'>
                <div style='font-size: 0.85rem; color: #6B7280;'>📊 רווח נקי</div>
                <div style='font-size: 2rem; font-weight: 700; color: {profit_color};'>₪{net_profit:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        
        # גרפים
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("#### 📈 הכנסות לפי בית ספר")
            if income_by_school:
                df_income = pd.DataFrame([{'בית ספר': k, 'הכנסות': v} for k, v in income_by_school.items()])
                fig1 = go.Figure()
                fig1.add_trace(go.Pie(
                    labels=df_income['בית ספר'],
                    values=df_income['הכנסות'],
                    hole=0.4,
                    marker_colors=['#10B981', '#3B82F6', '#6B7280', '#F59E0B', '#EF4444', '#8B5CF6']
                ))
                fig1.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("אין נתוני הכנסות")
        
        with col_chart2:
            st.markdown("#### 💸 הוצאות לפי קטגוריה")
            if expenses.data:
                df_exp = pd.DataFrame(expenses.data)
                exp_by_cat = df_exp.groupby('category')['amount'].sum().reset_index()
                
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    x=exp_by_cat['category'],
                    y=exp_by_cat['amount'],
                    marker_color='#EF4444'
                ))
                fig2.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("אין נתוני הוצאות")
                
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")

# ========================================
# טאב 2: הכנסות (אוטומטי)
# ========================================
with tab2:
    st.markdown("### 📈 הכנסות מפעילויות (חישוב אוטומטי)")
    st.info("💡 ההכנסות מחושבות אוטומטית לפי פעילויות שהושלמו × מחיר ליום של בית הספר")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        inc_start = st.date_input("מתאריך", value=datetime.now().replace(day=1).date(), key="inc_start")
    with col_d2:
        inc_end = st.date_input("עד תאריך", value=datetime.now().date(), key="inc_end")
    
    try:
        activities = supabase.table("activities") \
            .select("*, schools(name, price_per_day)") \
            .gte("date", str(inc_start)) \
            .lte("date", str(inc_end)) \
            .in_("status", ["completed", "confirmed"]) \
            .order("date") \
            .execute()
        
        if activities.data:
            rows = []
            total = 0
            for act in activities.data:
                price = act['schools']['price_per_day'] if act.get('schools') else 0
                total += price
                rows.append({
                    'תאריך': act['date'],
                    'בית ספר': act['schools']['name'] if act.get('schools') else '-',
                    'סטטוס': 'הושלם' if act['status'] == 'completed' else 'מאושר',
                    'סכום': price
                })
            
            df = pd.DataFrame(rows)
            st.dataframe(df.style.format({'סכום': '₪{:,.0f}'}), use_container_width=True, hide_index=True)
            
            st.markdown(f"""
            <div style='background: #D1FAE5; padding: 1rem; border-radius: 10px; text-align: center; margin-top: 1rem;'>
                <span style='font-size: 1.1rem;'>סה״כ הכנסות: </span>
                <span style='font-size: 1.5rem; font-weight: 700; color: #047857;'>₪{total:,}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("אין פעילויות בתקופה זו")
            
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")

# ========================================
# טאב 3: הוצאות
# ========================================
with tab3:
    st.markdown("### 📉 הוצאות")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        exp_start = st.date_input("מתאריך", value=datetime.now().replace(day=1).date(), key="exp_start")
    with col_d2:
        exp_end = st.date_input("עד תאריך", value=datetime.now().date(), key="exp_end")
    
    try:
        expenses = supabase.table("financial_records") \
            .select("*") \
            .eq("type", "expense") \
            .gte("date", str(exp_start)) \
            .lte("date", str(exp_end)) \
            .order("date", desc=True) \
            .execute()
        
        if expenses.data:
            df = pd.DataFrame(expenses.data)
            df_display = df[['date', 'category', 'description', 'amount']].copy()
            df_display.columns = ['תאריך', 'קטגוריה', 'תיאור', 'סכום']
            
            st.dataframe(df_display.style.format({'סכום': '₪{:,.0f}'}), use_container_width=True, hide_index=True)
            
            total = df['amount'].sum()
            st.markdown(f"""
            <div style='background: #FEE2E2; padding: 1rem; border-radius: 10px; text-align: center; margin-top: 1rem;'>
                <span style='font-size: 1.1rem;'>סה״כ הוצאות: </span>
                <span style='font-size: 1.5rem; font-weight: 700; color: #991B1B;'>₪{total:,}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("אין הוצאות בתקופה זו")
            
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")

# ========================================
# טאב 4: הוספת רשומה
# ========================================
with tab4:
    st.markdown("### ➕ הוספת רשומה ידנית")
    
    with st.form("add_record"):
        col1, col2 = st.columns(2)
        
        with col1:
            record_type = st.selectbox("סוג", ["expense", "income"], format_func=lambda x: "הוצאה" if x == "expense" else "הכנסה")
            amount = st.number_input("סכום (₪)", min_value=0.0, step=100.0)
            category = st.selectbox("קטגוריה", ["חומרים", "ציוד", "משכורות", "שיווק", "נסיעות", "תיקונים", "אחר"])
        
        with col2:
            record_date = st.date_input("תאריך", value=datetime.now().date())
            description = st.text_input("תיאור")
        
        if st.form_submit_button("💾 שמור", use_container_width=True):
            if amount <= 0:
                st.error("❌ נא להזין סכום")
            else:
                try:
                    supabase.table("financial_records").insert({
                        "type": record_type,
                        "amount": amount,
                        "category": category,
                        "date": str(record_date),
                        "description": description or None,
                        "created_by": user['id']
                    }).execute()
                    st.success("✅ נשמר!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ שגיאה: {str(e)}")
