import streamlit as st
from utils.auth import require_role
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
from utils.nav import render_sidebar
import pandas as pd

st.set_page_config(page_title="ניהול בתי ספר", page_icon="🏫", layout="wide")
apply_custom_css()
render_sidebar() # חובה!

user = require_role('manager')

st.title("🏫 ניהול בתי ספר")

tab1, tab2 = st.tabs(["📋 רשימת בתי ספר", "➕ הוספת בית ספר"])

with tab1:
    st.subheader("רשימת בתי הספר")
    try:
        response = supabase.table("schools").select("*").order("name").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            st.dataframe(df[['name', 'contact_person', 'phone', 'address', 'price_per_day']], use_container_width=True)
        else:
            st.info("אין בתי ספר במערכת")
    except:
        st.error("שגיאה בטעינה")

with tab2:
    st.subheader("הוספת בית ספר חדש")
    with st.form("add_school"):
        name = st.text_input("שם בית הספר")
        contact = st.text_input("איש קשר")
        phone = st.text_input("טלפון")
        price = st.number_input("מחיר ליום", value=1000)
        
        if st.form_submit_button("שמור"):
            try:
                supabase.table("schools").insert({
                    "name": name, "contact_person": contact, 
                    "phone": phone, "price_per_day": price, "status": "active"
                }).execute()
                st.success("נוסף בהצלחה!")
                st.rerun()
            except Exception as e:
                st.error(str(e))