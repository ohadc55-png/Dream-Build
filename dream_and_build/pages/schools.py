import streamlit as st
from utils.auth import require_role
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
import pandas as pd

st.set_page_config(page_title="ניהול בתי ספר", page_icon="🏫", layout="wide")
apply_custom_css()

# וידוא הרשאות מנהל
user = require_role('manager')

st.title("🏫 ניהול בתי ספר")

# טאבים
tab1, tab2, tab3 = st.tabs(["📋 רשימת בתי ספר", "➕ הוספת בית ספר", "💰 תקציבים"])

# טאב 1: רשימת בתי ספר
with tab1:
    st.subheader("רשימת בתי הספר")
    
    # חיפוש
    search = st.text_input("🔍 חיפוש בית ספר", placeholder="הקלד שם בית ספר...")
    
    try:
        # שליפת בתי ספר
        query = supabase.table("schools").select("*").order("name")
        
        if search:
            query = query.ilike("name", f"%{search}%")
        
        schools = query.execute()
        
        if schools.data and len(schools.data) > 0:
            # הצגה בטבלה
            df = pd.DataFrame(schools.data)
            df_display = df[['name', 'contact_person', 'phone', 'email', 'price_per_day', 'status']]
            df_display.columns = ['שם בית ספר', 'איש קשר', 'טלפון', 'אימייל', 'מחיר ליום (₪)', 'סטטוס']
            df_display['סטטוס'] = df_display['סטטוס'].map({'active': '✅ פעיל', 'inactive': '❌ לא פעיל'})
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # עריכת בית ספר
            st.subheader("✏️ עריכת בית ספר")
            school_names = [s['name'] for s in schools.data]
            selected_school_name = st.selectbox("בחר בית ספר לעריכה", school_names)
            
            if selected_school_name:
                selected_school = next((s for s in schools.data if s['name'] == selected_school_name), None)
                
                if selected_school:
                    with st.form("edit_school_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_name = st.text_input("שם בית הספר", value=selected_school['name'])
                            edit_contact = st.text_input("איש קשר", value=selected_school.get('contact_person', ''))
                            edit_phone = st.text_input("טלפון", value=selected_school.get('phone', ''))
                        
                        with col2:
                            edit_email = st.text_input("אימייל", value=selected_school.get('email', ''))
                            edit_price = st.number_input("מחיר ליום (₪)", value=float(selected_school['price_per_day']), min_value=0.0, step=100.0)
                            edit_status = st.selectbox("סטטוס", ['active', 'inactive'], 
                                                      index=0 if selected_school['status'] == 'active' else 1,
                                                      format_func=lambda x: 'פעיל' if x == 'active' else 'לא פעיל')
                        
                        edit_address = st.text_area("כתובת", value=selected_school.get('address', ''))
                        edit_notes = st.text_area("הערות", value=selected_school.get('notes', ''))
                        
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            update_btn = st.form_submit_button("💾 שמור שינויים", use_container_width=True)
                        
                        with col_btn2:
                            delete_btn = st.form_submit_button("🗑️ מחק בית ספר", use_container_width=True, type="secondary")
                        
                        if update_btn:
                            try:
                                update_data = {
                                    "name": edit_name,
                                    "contact_person": edit_contact,
                                    "phone": edit_phone,
                                    "email": edit_email,
                                    "address": edit_address,
                                    "price_per_day": edit_price,
                                    "notes": edit_notes,
                                    "status": edit_status
                                }
                                
                                supabase.table("schools").update(update_data).eq("id", selected_school['id']).execute()
                                st.success("✅ בית הספר עודכן בהצלחה!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ שגיאה בעדכון: {str(e)}")
                        
                        if delete_btn:
                            try:
                                supabase.table("schools").delete().eq("id", selected_school['id']).execute()
                                st.success("✅ בית הספר נמחק בהצלחה!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ שגיאה במחיקה: {str(e)}")
        else:
            st.info("אין בתי ספר במערכת. הוסף בית ספר ראשון בטאב 'הוספת בית ספר'")
    
    except Exception as e:
        st.error(f"שגיאה בטעינת בתי ספר: {str(e)}")

# טאב 2: הוספת בית ספר
with tab2:
    st.subheader("הוסף בית ספר חדש")
    
    with st.form("add_school_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("שם בית הספר *", placeholder="לדוגמה: בית ספר תל אביב")
            contact_person = st.text_input("איש קשר", placeholder="שם איש הקשר")
            phone = st.text_input("טלפון", placeholder="050-1234567")
        
        with col2:
            email = st.text_input("אימייל", placeholder="school@example.com")
            price_per_day = st.number_input("מחיר ליום פעילות (₪) *", min_value=0.0, value=1000.0, step=100.0)
            status = st.selectbox("סטטוס", ['active', 'inactive'], 
                                 format_func=lambda x: 'פעיל' if x == 'active' else 'לא פעיל')
        
        address = st.text_area("כתובת", placeholder="רחוב העצמאות 123, תל אביב")
        notes = st.text_area("הערות", placeholder="הערות נוספות על בית הספר...")
        
        submit = st.form_submit_button("➕ הוסף בית ספר", use_container_width=True)
        
        if submit:
            if not name or price_per_day <= 0:
                st.error("❌ נא למלא את השדות החובה: שם בית ספר ומחיר ליום")
            else:
                try:
                    school_data = {
                        "name": name,
                        "contact_person": contact_person if contact_person else None,
                        "phone": phone if phone else None,
                        "email": email if email else None,
                        "address": address if address else None,
                        "price_per_day": price_per_day,
                        "notes": notes if notes else None,
                        "status": status
                    }
                    
                    supabase.table("schools").insert(school_data).execute()
                    st.success(f"✅ בית הספר '{name}' נוסף בהצלחה!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ שגיאה בהוספה: {str(e)}")

# טאב 3: תקציבים
with tab3:
    st.subheader("💰 ניהול תקציבים לבתי ספר")
    
    try:
        # שליפת בתי ספר
        schools = supabase.table("schools").select("*").eq("status", "active").execute()
        
        if schools.data and len(schools.data) > 0:
            # בחירת בית ספר
            school_names = {s['name']: s['id'] for s in schools.data}
            selected_school = st.selectbox("בחר בית ספר", list(school_names.keys()))
            
            if selected_school:
                school_id = school_names[selected_school]
                
                # שליפת תקציב קיים
                current_year = pd.Timestamp.now().year
                budget = supabase.table("school_budgets") \
                    .select("*") \
                    .eq("school_id", school_id) \
                    .eq("year", current_year) \
                    .execute()
                
                # טופס הגדרת/עדכון תקציב
                with st.form("budget_form"):
                    col1, col2, col3 = st.columns(3)
                    
                    if budget.data and len(budget.data) > 0:
                        current_budget = budget.data[0]
                        
                        with col1:
                            budget_amount = st.number_input(
                                "תקציב שנתי (₪)", 
                                value=float(current_budget['budget_amount']), 
                                min_value=0.0, 
                                step=1000.0
                            )
                        
                        with col2:
                            spent_amount = st.number_input(
                                "סכום שהושקע (₪)", 
                                value=float(current_budget['spent_amount']), 
                                min_value=0.0, 
                                step=100.0
                            )
                        
                        with col3:
                            alert_threshold = st.number_input(
                                "התראה ב-₪ לפני הגבול", 
                                value=float(current_budget.get('alert_threshold', 1000)), 
                                min_value=0.0, 
                                step=100.0
                            )
                        
                        notes = st.text_area("הערות", value=current_budget.get('notes', ''))
                        
                        submit_budget = st.form_submit_button("💾 עדכן תקציב", use_container_width=True)
                        
                        if submit_budget:
                            try:
                                update_data = {
                                    "budget_amount": budget_amount,
                                    "spent_amount": spent_amount,
                                    "alert_threshold": alert_threshold,
                                    "notes": notes if notes else None
                                }
                                
                                supabase.table("school_budgets") \
                                    .update(update_data) \
                                    .eq("id", current_budget['id']) \
                                    .execute()
                                
                                st.success("✅ התקציב עודכן בהצלחה!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ שגיאה: {str(e)}")
                        
                        # הצגת מצב תקציב
                        remaining = budget_amount - spent_amount
                        progress = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0
                        
                        st.markdown("---")
                        st.markdown("### 📊 מצב תקציב נוכחי")
                        
                        col_status1, col_status2, col_status3 = st.columns(3)
                        with col_status1:
                            st.metric("תקציב כולל", f"{budget_amount:,.0f}₪")
                        with col_status2:
                            st.metric("הושקע", f"{spent_amount:,.0f}₪")
                        with col_status3:
                            st.metric("יתרה", f"{remaining:,.0f}₪", 
                                     delta="⚠️ התראה" if remaining <= alert_threshold else None)
                        
                        st.progress(progress / 100)
                        st.caption(f"נוצל {progress:.1f}% מהתקציב")
                        
                        if remaining <= alert_threshold:
                            st.warning(f"⚠️ התראה: נותרו רק {remaining:,.0f}₪ מהתקציב!")
                    
                    else:
                        # יצירת תקציב חדש
                        with col1:
                            budget_amount = st.number_input("תקציב שנתי (₪)", min_value=0.0, value=50000.0, step=1000.0)
                        
                        with col2:
                            spent_amount = st.number_input("סכום שהושקע (₪)", min_value=0.0, value=0.0, step=100.0)
                        
                        with col3:
                            alert_threshold = st.number_input("התראה ב-₪ לפני הגבול", min_value=0.0, value=1000.0, step=100.0)
                        
                        notes = st.text_area("הערות")
                        
                        submit_new_budget = st.form_submit_button("➕ צור תקציב", use_container_width=True)
                        
                        if submit_new_budget:
                            try:
                                budget_data = {
                                    "school_id": school_id,
                                    "budget_amount": budget_amount,
                                    "spent_amount": spent_amount,
                                    "year": current_year,
                                    "alert_threshold": alert_threshold,
                                    "notes": notes if notes else None
                                }
                                
                                supabase.table("school_budgets").insert(budget_data).execute()
                                st.success("✅ התקציב נוצר בהצלחה!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ שגיאה: {str(e)}")
        else:
            st.info("אין בתי ספר פעילים. הוסף בית ספר תחילה.")
    
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")
