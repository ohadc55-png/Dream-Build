import streamlit as st
from utils.auth import require_role
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
from utils.nav import render_sidebar
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="דוחות כספיים", page_icon="💰", layout="wide")
apply_custom_css()
render_sidebar()

user = require_role('manager')

st.title("💰 דוחות כספיים וניהול תקציב")

# מדדים ראשיים (KPIs)
col1, col2, col3 = st.columns(3)

try:
    # שליפת נתוני תקציב
    budgets = supabase.table("school_budgets").select("*, schools(name)").execute()
    
    total_budget = 0
    total_spent = 0
    
    if budgets.data:
        df = pd.DataFrame(budgets.data)
        total_budget = df['budget_amount'].sum()
        total_spent = df['spent_amount'].sum()
        
    remaining = total_budget - total_spent
    
    with col1:
        st.metric("תקציב כולל שנתי", f"₪{total_budget:,.0f}")
    with col2:
        st.metric("נוצל עד כה", f"₪{total_spent:,.0f}", delta=f"{(total_spent/total_budget)*100:.1f}%" if total_budget else "0%")
    with col3:
        st.metric("יתרה כוללת", f"₪{remaining:,.0f}", delta_color="normal" if remaining > 0 else "inverse")

    st.markdown("---")

    # גרפים וניתוחים
    col_chart1, col_chart2 = st.columns([2, 1])

    with col_chart1:
        st.subheader("📊 ניצול תקציב לפי בית ספר")
        if budgets.data:
            # הכנת דאטה לגרף
            chart_data = []
            for item in budgets.data:
                school_name = item['schools']['name'] if item['schools'] else 'לא ידוע'
                chart_data.append({'בית ספר': school_name, 'סוג': 'תקציב', 'סכום': item['budget_amount']})
                chart_data.append({'בית ספר': school_name, 'סוג': 'נוצל', 'סכום': item['spent_amount']})
            
            df_chart = pd.DataFrame(chart_data)
            
            fig = px.bar(df_chart, x='בית ספר', y='סכום', color='סוג', barmode='group',
                        color_discrete_map={'תקציב': '#E0E0E0', 'נוצל': '#FF8C00'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("אין נתוני תקציב להצגה")

    with col_chart2:
        st.subheader("⚠️ חריגות והתראות")
        if budgets.data:
            alerts = []
            for b in budgets.data:
                rem = b['budget_amount'] - b['spent_amount']
                threshold = b.get('alert_threshold', 1000)
                if rem <= threshold:
                    school_name = b['schools']['name']
                    alerts.append(f"**{school_name}**: נותרו ₪{rem:,.0f} בלבד!")
            
            if alerts:
                for alert in alerts:
                    st.error(alert)
            else:
                st.success("כל התקציבים במצב תקין")
                
except Exception as e:
    st.error(f"שגיאה בטעינת נתונים כספיים: {str(e)}")

st.markdown("---")
st.subheader("📋 פירוט מלא")
if 'df' in locals() and not df.empty:
    display_df = df.copy()
    display_df['school_name'] = display_df['schools'].apply(lambda x: x['name'])
    st.dataframe(
        display_df[['school_name', 'year', 'budget_amount', 'spent_amount', 'notes']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "school_name": "בית ספר",
            "year": "שנה",
            "budget_amount": st.column_config.NumberColumn("תקציב", format="₪%d"),
            "spent_amount": st.column_config.NumberColumn("נוצל", format="₪%d"),
            "notes": "הערות"
        }
    )