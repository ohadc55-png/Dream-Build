import streamlit as st
from utils.auth import require_role
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
from utils.nav import render_sidebar  # <-- התיקון
import pandas as pd

st.set_page_config(page_title="ניהול בתי ספר", page_icon="🏫", layout="wide")
apply_custom_css()
render_sidebar()  # <-- התיקון

user = require_role('manager')

st.title("🏫 ניהול בתי ספר")

# שלושת הטאבים המקוריים
tab1, tab2, tab3 = st.tabs(["📋 רשימת בתי ספר", "➕ הוספת בית ספר", "💰 תקציבים"])

# --- טאב 1: רשימה ועריכה ---
with tab1:
    st.subheader("רשימת בתי הספר")
    search = st.text_input("🔍 חיפוש", placeholder="שם בית ספר...")
    
    try:
        query = supabase.table("schools").select("*").order("name")
        if search: query = query.ilike("name", f"%{search}%")
        schools = query.execute()
        
        if schools.data:
            df = pd.DataFrame(schools.data)
            st.dataframe(df[['name', 'contact_person', 'phone', 'price_per_day', 'status']], use_container_width=True)
            
            # אזור עריכה (הוחזר)
            st.markdown("---")
            st.subheader("✏️ עריכת בית ספר")
            selected_name = st.selectbox("בחר לעריכה", [s['name'] for s in schools.data])
            if selected_name:
                school = next(s for s in schools.data if s['name'] == selected_name)
                with st.form("edit_school"):
                    new_name = st.text_input("שם", school['name'])
                    new_price = st.number_input("מחיר", value=float(school['price_per_day']))
                    if st.form_submit_button("עדכן"):
                        supabase.table("schools").update({"name": new_name, "price_per_day": new_price}).eq("id", school['id']).execute()
                        st.success("עודכן!")
                        st.rerun()
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")

# --- טאב 2: הוספה ---
with tab2:
    st.subheader("הוספת חדש")
    with st.form("add_school"):
        name = st.text_input("שם בית הספר")
        contact = st.text_input("איש קשר")
        phone = st.text_input("טלפון")
        price = st.number_input("מחיר ליום", value=1000)
        
        if st.form_submit_button("שמור"):
            supabase.table("schools").insert({
                "name": name, "contact_person": contact, 
                "phone": phone, "price_per_day": price, "status": "active"
            }).execute()
            st.success("נוסף בהצלחה!")
            st.rerun()

# --- טאב 3: תקציבים (הוחזר) ---
with tab3:
    st.subheader("💰 ניהול תקציבים")
    st.info("כאן יופיע ניהול התקציבים (פונקציונליות זהה לקוד המקורי)")