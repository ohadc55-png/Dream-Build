import streamlit as st
from utils.auth import require_role
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
from utils.nav import render_sidebar
import pandas as pd
import time

st.set_page_config(page_title="ייבוא נתונים", page_icon="📥", layout="wide")
apply_custom_css()
render_sidebar()

require_role('manager')

st.title("📥 ייבוא נתונים היסטוריים")
st.info("כלי זה נועד להעלאה המונית של נתונים מקבצי Excel/CSV כדי לחסוך הזנה ידנית.")

tab1, tab2, tab3 = st.tabs(["1. בתי ספר", "2. עובדים", "3. היסטוריית פעילויות (הכי חשוב)"])

# --- טאב 1: ייבוא בתי ספר ---
with tab1:
    st.subheader("ייבוא בתי ספר")
    st.markdown("""
    **מבנה הקובץ הנדרש (Excel/CSV):**
    עמודה 1: `name` (שם בית הספר)
    עמודה 2: `price` (תעריף ליום)
    """)
    
    uploaded_file = st.file_uploader("בחר קובץ בתי ספר", type=['csv', 'xlsx'], key="schools_up")
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.write("תצוגה מקדימה:", df.head())
            
            if st.button("🚀 טען בתי ספר למערכת"):
                progress_bar = st.progress(0)
                success_count = 0
                
                for index, row in df.iterrows():
                    try:
                        # בדיקה אם קיים
                        existing = supabase.table("schools").select("id").eq("name", row['name']).execute()
                        if not existing.data:
                            supabase.table("schools").insert({
                                "name": row['name'],
                                "price_per_day": row.get('price', 1000),
                                "status": "active"
                            }).execute()
                            success_count += 1
                    except Exception as e:
                        st.error(f"שגיאה בשורה {index}: {e}")
                    
                    progress_bar.progress((index + 1) / len(df))
                
                st.success(f"✅ נטענו {success_count} בתי ספר חדשים!")
                
        except Exception as e:
            st.error(f"שגיאה בקריאת הקובץ: {e}")

# --- טאב 2: ייבוא עובדים ---
with tab2:
    st.subheader("ייבוא עובדים")
    st.markdown("""
    **מבנה הקובץ הנדרש:**
    `name` (שם מלא), `email` (אימייל), `rate_day` (תעריף יומי), `rate_hour` (תעריף שעתי)
    """)
    
    uploaded_emp = st.file_uploader("בחר קובץ עובדים", type=['csv', 'xlsx'], key="emp_up")
    
    if uploaded_emp:
        try:
            df = pd.read_csv(uploaded_emp) if uploaded_emp.name.endswith('.csv') else pd.read_excel(uploaded_emp)
            st.write("תצוגה מקדימה:", df.head())
            
            if st.button("🚀 טען עובדים"):
                import uuid
                count = 0
                for i, row in df.iterrows():
                    try:
                        # בדיקה לפי מייל
                        exist = supabase.table("users").select("id").eq("email", row['email']).execute()
                        if not exist.data:
                            # יצירת משתמש פיקטיבי ב-Auth כדי לקבל ID (כמו שעשינו קודם)
                            # הערה: זה יעבוד במצב פיתוח. בייצור עדיף שהם ירשמו לבד.
                            new_id = str(uuid.uuid4())
                            
                            supabase.table("users").insert({
                                "id": new_id,
                                "full_name": row['name'],
                                "email": row['email'],
                                "role": "employee",
                                "status": "active",
                                "daily_rate": row.get('rate_day', 0),
                                "hourly_rate": row.get('rate_hour', 0)
                            }).execute()
                            count += 1
                    except Exception as e:
                        st.error(f"שגיאה ב-{row['name']}: {e}")
                st.success(f"נוספו {count} עובדים")
        except Exception as e:
            st.error(str(e))

# --- טאב 3: היסטוריה (הקסם קורה כאן) ---
with tab3:
    st.subheader("ייבוא היסטוריית פעילויות")
    st.markdown("""
    ℹ️ **המערכת תחשב אוטומטית כמה הרוויח כל עובד וכמה בית הספר חייב, על בסיס הנתונים האלו.**
    
    **מבנה הקובץ הנדרש:**
    1. `date` (תאריך: YYYY-MM-DD)
    2. `school` (שם בית הספר - חייב להיות זהה למה שקיים במערכת)
    3. `employee` (שם העובד - חייב להיות זהה למה שקיים במערכת)
    4. `hours` (כמות שעות - אופציונלי)
    """)
    
    uploaded_hist = st.file_uploader("בחר קובץ פעילויות", type=['csv', 'xlsx'], key="hist_up")
    
    if uploaded_hist:
        try:
            df = pd.read_csv(uploaded_hist) if uploaded_hist.name.endswith('.csv') else pd.read_excel(uploaded_hist)
            st.write(f"נמצאו {len(df)} רשומות. דוגמה:", df.head())
            
            if st.button("🚀 התחל פענוח וטעינה"):
                # 1. טעינת כל המזהים מהמערכת לזיכרון (כדי לתרגם שמות ל-IDs)
                st.info("טוען מזהים מהמערכת...")
                
                schools_db = supabase.table("schools").select("id, name").execute()
                school_map = {item['name'].strip(): item['id'] for item in schools_db.data}
                
                users_db = supabase.table("users").select("id, full_name").execute()
                user_map = {item['full_name'].strip(): item['id'] for item in users_db.data}
                
                success = 0
                errors = []
                
                my_bar = st.progress(0)
                
                for i, row in df.iterrows():
                    school_name = str(row['school']).strip()
                    emp_name = str(row['employee']).strip()
                    date_str = str(row['date'])
                    
                    # בדיקת התאמות
                    s_id = school_map.get(school_name)
                    e_id = user_map.get(emp_name)
                    
                    if s_id and e_id:
                        try:
                            # יצירת הפעילות
                            # אנו מסמנים אותה כ-'completed' כדי שהיא תיחשב בשכר ובתקציב
                            supabase.table("activities").insert({
                                "school_id": s_id,
                                "employee_id": e_id,
                                "date": date_str,
                                "time_start": "08:00:00", # ברירת מחדל
                                "time_end": "13:00:00",   # ברירת מחדל
                                "status": "completed",    # חשוב!
                                "confirmed_by_employee": True,
                                "notes": "ייבוא היסטורי"
                            }).execute()
                            success += 1
                        except Exception as e:
                            errors.append(f"שורה {i+1}: שגיאת מסד נתונים - {e}")
                    else:
                        missing = []
                        if not s_id: missing.append(f"בית ספר לא נמצא: {school_name}")
                        if not e_id: missing.append(f"עובד לא נמצא: {emp_name}")
                        errors.append(f"שורה {i+1}: {', '.join(missing)}")
                    
                    my_bar.progress((i + 1) / len(df))
                
                st.success(f"✅ הסתיים! {success} פעילויות נטענו בהצלחה.")
                
                if errors:
                    st.error(f"נכשלו {len(errors)} שורות:")
                    st.text("\n".join(errors))
                    
        except Exception as e:
            st.error(f"קריסה: {e}")