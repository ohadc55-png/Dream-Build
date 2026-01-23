import streamlit as st
from utils.auth import require_role
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="דוחות כספיים", page_icon="💰", layout="wide")
apply_custom_css()

# וידוא הרשאות מנהל
user = require_role('manager')

st.title("💰 דוחות כספיים")

# טאבים
tab1, tab2, tab3, tab4 = st.tabs(["📊 סיכום", "📈 הכנסות", "📉 הוצאות", "➕ הוספת רשומה"])

# טאב 1: סיכום
with tab1:
    st.subheader("📊 סיכום כספי")
    
    # בחירת טווח זמן
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("מתאריך", value=datetime.now().replace(day=1).date())
    with col_date2:
        end_date = st.date_input("עד תאריך", value=datetime.now().date())
    
    try:
        # שליפת רשומות כספיות
        records = supabase.table("financial_records") \
            .select("*, schools(name)") \
            .gte("date", str(start_date)) \
            .lte("date", str(end_date)) \
            .execute()
        
        if records.data and len(records.data) > 0:
            df = pd.DataFrame(records.data)
            
            # חישובים
            total_income = df[df['type'] == 'income']['amount'].sum()
            total_expense = df[df['type'] == 'expense']['amount'].sum()
            balance = total_income - total_expense
            
            # מטריקות
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("💵 הכנסות", f"₪{total_income:,.0f}", "")
            with col2:
                st.metric("💸 הוצאות", f"₪{total_expense:,.0f}", "")
            with col3:
                delta_color = "normal" if balance >= 0 else "inverse"
                st.metric("💰 מאזן", f"₪{balance:,.0f}", 
                         delta=f"{'רווח' if balance >= 0 else 'הפסד'}")
            
            st.markdown("---")
            
            # גרף הכנסות vs הוצאות לפי חודש
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.to_period('M').astype(str)
            
            monthly = df.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0).reset_index()
            
            if 'income' in monthly.columns and 'expense' in monthly.columns:
                fig = go.Figure()
                fig.add_trace(go.Bar(x=monthly['month'], y=monthly['income'], name='הכנסות', marker_color='#32CD32'))
                fig.add_trace(go.Bar(x=monthly['month'], y=monthly['expense'], name='הוצאות', marker_color='#FF6347'))
                fig.update_layout(title='הכנסות vs הוצאות לפי חודש', barmode='group')
                st.plotly_chart(fig, use_container_width=True)
            
            # פירוט לפי קטגוריה
            col_cat1, col_cat2 = st.columns(2)
            
            with col_cat1:
                st.markdown("#### 📈 הכנסות לפי קטגוריה")
                income_by_cat = df[df['type'] == 'income'].groupby('category')['amount'].sum().reset_index()
                if len(income_by_cat) > 0:
                    fig_income = px.pie(income_by_cat, values='amount', names='category', 
                                       color_discrete_sequence=px.colors.sequential.Greens)
                    st.plotly_chart(fig_income, use_container_width=True)
                else:
                    st.info("אין הכנסות בתקופה זו")
            
            with col_cat2:
                st.markdown("#### 📉 הוצאות לפי קטגוריה")
                expense_by_cat = df[df['type'] == 'expense'].groupby('category')['amount'].sum().reset_index()
                if len(expense_by_cat) > 0:
                    fig_expense = px.pie(expense_by_cat, values='amount', names='category',
                                        color_discrete_sequence=px.colors.sequential.Reds)
                    st.plotly_chart(fig_expense, use_container_width=True)
                else:
                    st.info("אין הוצאות בתקופה זו")
        else:
            st.info("אין רשומות כספיות בטווח התאריכים שנבחר")
            
            # מטריקות ריקות
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💵 הכנסות", "₪0")
            with col2:
                st.metric("💸 הוצאות", "₪0")
            with col3:
                st.metric("💰 מאזן", "₪0")
    
    except Exception as e:
        st.error(f"שגיאה בטעינת נתונים: {str(e)}")

# טאב 2: הכנסות
with tab2:
    st.subheader("📈 הכנסות")
    
    try:
        income_records = supabase.table("financial_records") \
            .select("*, schools(name)") \
            .eq("type", "income") \
            .order("date", desc=True) \
            .execute()
        
        if income_records.data and len(income_records.data) > 0:
            df_income = pd.DataFrame(income_records.data)
            df_income['school_name'] = df_income['schools'].apply(lambda x: x['name'] if x else '-')
            
            df_display = df_income[['date', 'amount', 'category', 'school_name', 'description']].copy()
            df_display.columns = ['תאריך', 'סכום (₪)', 'קטגוריה', 'בית ספר', 'תיאור']
            df_display['סכום (₪)'] = df_display['סכום (₪)'].apply(lambda x: f"₪{x:,.0f}")
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # סיכום
            total = df_income['amount'].sum()
            st.success(f"**סה״כ הכנסות:** ₪{total:,.0f}")
        else:
            st.info("אין רשומות הכנסה")
    
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")

# טאב 3: הוצאות
with tab3:
    st.subheader("📉 הוצאות")
    
    try:
        expense_records = supabase.table("financial_records") \
            .select("*, schools(name)") \
            .eq("type", "expense") \
            .order("date", desc=True) \
            .execute()
        
        if expense_records.data and len(expense_records.data) > 0:
            df_expense = pd.DataFrame(expense_records.data)
            df_expense['school_name'] = df_expense['schools'].apply(lambda x: x['name'] if x else '-')
            
            df_display = df_expense[['date', 'amount', 'category', 'school_name', 'description']].copy()
            df_display.columns = ['תאריך', 'סכום (₪)', 'קטגוריה', 'בית ספר', 'תיאור']
            df_display['סכום (₪)'] = df_display['סכום (₪)'].apply(lambda x: f"₪{x:,.0f}")
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # סיכום
            total = df_expense['amount'].sum()
            st.error(f"**סה״כ הוצאות:** ₪{total:,.0f}")
        else:
            st.info("אין רשומות הוצאה")
    
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")

# טאב 4: הוספת רשומה
with tab4:
    st.subheader("➕ הוספת רשומה כספית")
    
    with st.form("add_financial_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            record_type = st.selectbox("סוג *", ['income', 'expense'],
                                      format_func=lambda x: '💵 הכנסה' if x == 'income' else '💸 הוצאה')
            amount = st.number_input("סכום (₪) *", min_value=0.0, value=0.0, step=100.0)
            record_date = st.date_input("תאריך *", value=datetime.now().date())
        
        with col2:
            # קטגוריות לפי סוג
            if record_type == 'income':
                categories = ['תשלום מבית ספר', 'סדנה פרטית', 'מכירת מוצרים', 'אחר']
            else:
                categories = ['ציוד', 'חומרים', 'משכורות', 'שכירות', 'נסיעות', 'אחר']
            
            category = st.selectbox("קטגוריה *", categories)
            
            # בית ספר (אופציונלי)
            try:
                schools = supabase.table("schools").select("id, name").execute()
                school_options = {"ללא": None}
                if schools.data:
                    school_options.update({s['name']: s['id'] for s in schools.data})
            except:
                school_options = {"ללא": None}
            
            school = st.selectbox("בית ספר (אופציונלי)", list(school_options.keys()))
        
        description = st.text_area("תיאור")
        
        submit = st.form_submit_button("➕ הוסף רשומה", use_container_width=True)
        
        if submit:
            if amount <= 0:
                st.error("❌ נא להזין סכום חיובי")
            else:
                try:
                    record_data = {
                        "type": record_type,
                        "amount": amount,
                        "category": category,
                        "date": str(record_date),
                        "school_id": school_options[school],
                        "description": description if description else None,
                        "created_by": user['id']
                    }
                    
                    supabase.table("financial_records").insert(record_data).execute()
                    st.success("✅ הרשומה נוספה בהצלחה!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ שגיאה: {str(e)}")

# הוספת מידע על תקציבי בתי ספר
st.markdown("---")
st.subheader("🏫 מצב תקציבים לבתי ספר")

try:
    budgets = supabase.table("school_budgets") \
        .select("*, schools(name)") \
        .eq("year", datetime.now().year) \
        .execute()
    
    if budgets.data and len(budgets.data) > 0:
        for budget in budgets.data:
            school_name = budget['schools']['name'] if budget['schools'] else 'לא ידוע'
            remaining = budget['budget_amount'] - budget['spent_amount']
            progress = (budget['spent_amount'] / budget['budget_amount'] * 100) if budget['budget_amount'] > 0 else 0
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{school_name}**")
                st.progress(min(progress / 100, 1.0))
            with col2:
                if remaining <= budget.get('alert_threshold', 1000):
                    st.warning(f"₪{remaining:,.0f}")
                else:
                    st.success(f"₪{remaining:,.0f}")
    else:
        st.info("לא הוגדרו תקציבים לבתי ספר השנה")

except Exception as e:
    st.info("טרם הוגדרו תקציבים")
