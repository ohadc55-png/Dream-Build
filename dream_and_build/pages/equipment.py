import streamlit as st
from utils.auth import check_auth
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ניהול ציוד", page_icon="🔧", layout="wide")
apply_custom_css()

# בדיקת אימות
user = check_auth()
is_manager = user.get('role') == 'manager'

st.title("🔧 ניהול ציוד" if is_manager else "🔧 דיווח ציוד")

# טאבים - שונים למנהל ולעובד
if is_manager:
    tab1, tab2, tab3, tab4 = st.tabs(["📦 מלאי", "➕ הוספת פריט", "📝 דיווחי חוסרים", "📊 שימוש"])
else:
    tab1, tab2 = st.tabs(["📝 דיווח חוסר", "📋 הדיווחים שלי"])

# === למנהל ===
if is_manager:
    # טאב 1: מלאי
    with tab1:
        st.subheader("📦 מצב המלאי")
        
        # פילטרים
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            category_filter = st.selectbox("קטגוריה", ["הכל", "כלים", "חומרים"])
        with col_f2:
            stock_filter = st.selectbox("מצב מלאי", ["הכל", "מלאי נמוך", "תקין"])
        
        try:
            query = supabase.table("equipment").select("*").order("name")
            
            if category_filter == "כלים":
                query = query.eq("category", "tools")
            elif category_filter == "חומרים":
                query = query.eq("category", "materials")
            
            equipment = query.execute()
            
            if equipment.data and len(equipment.data) > 0:
                df = pd.DataFrame(equipment.data)
                
                # חישוב מצב מלאי
                df['low_stock'] = df['quantity_available'] <= df['min_threshold']
                
                # פילטר מלאי
                if stock_filter == "מלאי נמוך":
                    df = df[df['low_stock']]
                elif stock_filter == "תקין":
                    df = df[~df['low_stock']]
                
                if len(df) > 0:
                    df_display = df[['name', 'category', 'quantity_total', 'quantity_available', 'min_threshold', 'unit']].copy()
                    df_display.columns = ['שם', 'קטגוריה', 'סה"כ', 'זמין', 'סף מינימום', 'יחידה']
                    df_display['קטגוריה'] = df_display['קטגוריה'].map({'tools': '🔨 כלים', 'materials': '📦 חומרים'})
                    
                    # צביעת שורות עם מלאי נמוך
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                    
                    # התראות
                    low_stock_items = df[df['low_stock']]
                    if len(low_stock_items) > 0:
                        st.warning(f"⚠️ {len(low_stock_items)} פריטים במלאי נמוך!")
                        for _, item in low_stock_items.iterrows():
                            st.markdown(f"- **{item['name']}**: {item['quantity_available']}/{item['min_threshold']} {item['unit']}")
                    
                    # עריכת פריט
                    st.markdown("---")
                    st.subheader("✏️ עריכת פריט")
                    
                    item_names = df['name'].tolist()
                    selected_item = st.selectbox("בחר פריט", item_names)
                    
                    if selected_item:
                        item = df[df['name'] == selected_item].iloc[0]
                        
                        with st.form("edit_equipment_form"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                edit_name = st.text_input("שם", value=item['name'])
                                edit_category = st.selectbox("קטגוריה", ['tools', 'materials'],
                                                            index=0 if item['category'] == 'tools' else 1,
                                                            format_func=lambda x: 'כלים' if x == 'tools' else 'חומרים')
                                edit_total = st.number_input("כמות כוללת", value=int(item['quantity_total']), min_value=0)
                            
                            with col2:
                                edit_available = st.number_input("כמות זמינה", value=int(item['quantity_available']), min_value=0)
                                edit_min = st.number_input("סף מינימום", value=int(item['min_threshold']), min_value=0)
                                edit_unit = st.text_input("יחידת מידה", value=item['unit'])
                            
                            edit_notes = st.text_area("הערות", value=item.get('notes', '') or '')
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                update_btn = st.form_submit_button("💾 שמור", use_container_width=True)
                            with col_btn2:
                                delete_btn = st.form_submit_button("🗑️ מחק", use_container_width=True, type="secondary")
                            
                            if update_btn:
                                try:
                                    update_data = {
                                        "name": edit_name,
                                        "category": edit_category,
                                        "quantity_total": edit_total,
                                        "quantity_available": edit_available,
                                        "min_threshold": edit_min,
                                        "unit": edit_unit,
                                        "notes": edit_notes if edit_notes else None
                                    }
                                    supabase.table("equipment").update(update_data).eq("id", item['id']).execute()
                                    st.success("✅ הפריט עודכן!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ שגיאה: {str(e)}")
                            
                            if delete_btn:
                                try:
                                    supabase.table("equipment").delete().eq("id", item['id']).execute()
                                    st.success("✅ הפריט נמחק!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ שגיאה: {str(e)}")
                else:
                    st.info("אין פריטים התואמים לפילטר")
            else:
                st.info("אין ציוד במערכת. הוסף פריטים בטאב 'הוספת פריט'")
        
        except Exception as e:
            st.error(f"שגיאה: {str(e)}")
    
    # טאב 2: הוספת פריט
    with tab2:
        st.subheader("➕ הוספת פריט חדש")
        
        with st.form("add_equipment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("שם הפריט *")
                new_category = st.selectbox("קטגוריה *", ['tools', 'materials'],
                                           format_func=lambda x: 'כלים' if x == 'tools' else 'חומרים')
                new_total = st.number_input("כמות כוללת *", min_value=0, value=10)
            
            with col2:
                new_available = st.number_input("כמות זמינה", min_value=0, value=10)
                new_min = st.number_input("סף מינימום להתראה", min_value=0, value=5)
                new_unit = st.text_input("יחידת מידה", value="יחידות")
            
            new_notes = st.text_area("הערות")
            
            submit = st.form_submit_button("➕ הוסף פריט", use_container_width=True)
            
            if submit:
                if not new_name:
                    st.error("❌ נא להזין שם פריט")
                else:
                    try:
                        equipment_data = {
                            "name": new_name,
                            "category": new_category,
                            "quantity_total": new_total,
                            "quantity_available": new_available,
                            "min_threshold": new_min,
                            "unit": new_unit,
                            "notes": new_notes if new_notes else None
                        }
                        supabase.table("equipment").insert(equipment_data).execute()
                        st.success(f"✅ הפריט '{new_name}' נוסף!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ שגיאה: {str(e)}")
    
    # טאב 3: דיווחי חוסרים
    with tab3:
        st.subheader("📝 דיווחי חוסרים מעובדים")
        
        try:
            reports = supabase.table("equipment_reports") \
                .select("*, equipment(name), users(full_name)") \
                .order("created_at", desc=True) \
                .execute()
            
            if reports.data and len(reports.data) > 0:
                # פילטר סטטוס
                report_status = st.selectbox("סטטוס", ["ממתינים", "טופלו", "הכל"])
                
                df = pd.DataFrame(reports.data)
                df['equipment_name'] = df['equipment'].apply(lambda x: x['name'] if x else 'לא ידוע')
                df['employee_name'] = df['users'].apply(lambda x: x['full_name'] if x else 'לא ידוע')
                
                if report_status == "ממתינים":
                    df = df[df['status'] == 'pending']
                elif report_status == "טופלו":
                    df = df[df['status'] == 'resolved']
                
                if len(df) > 0:
                    for _, report in df.iterrows():
                        urgency_color = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
                        urgency_text = {'low': 'נמוכה', 'medium': 'בינונית', 'high': 'גבוהה'}
                        
                        with st.expander(f"{urgency_color.get(report['urgency'], '⚪')} {report['equipment_name']} - {report['employee_name']}"):
                            st.markdown(f"**כמות נדרשת:** {report['quantity_needed']}")
                            st.markdown(f"**דחיפות:** {urgency_text.get(report['urgency'], 'לא ידוע')}")
                            st.markdown(f"**תאריך דיווח:** {report['created_at'][:10]}")
                            if report.get('notes'):
                                st.markdown(f"**הערות:** {report['notes']}")
                            
                            if report['status'] == 'pending':
                                if st.button("✅ סמן כטופל", key=f"resolve_{report['id']}"):
                                    try:
                                        supabase.table("equipment_reports") \
                                            .update({"status": "resolved", "resolved_at": datetime.now().isoformat()}) \
                                            .eq("id", report['id']) \
                                            .execute()
                                        st.success("✅ הדיווח סומן כטופל!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"שגיאה: {str(e)}")
                            else:
                                st.success("✅ טופל")
                else:
                    st.info("אין דיווחים בסטטוס זה")
            else:
                st.info("אין דיווחי חוסרים")
        
        except Exception as e:
            st.error(f"שגיאה: {str(e)}")
    
    # טאב 4: שימוש
    with tab4:
        st.subheader("📊 שימוש בציוד")
        st.info("כאן יוצגו נתונים על שימוש בציוד לאורך זמן")
        # TODO: הוסף גרפים ונתונים

# === לעובד ===
else:
    # טאב 1: דיווח חוסר
    with tab1:
        st.subheader("📝 דיווח על חוסר ציוד")
        
        with st.form("report_form"):
            try:
                equipment_list = supabase.table("equipment").select("id, name").execute()
                equipment_options = {item['name']: item['id'] for item in equipment_list.data} if equipment_list.data else {}
            except:
                equipment_options = {}
            
            col1, col2 = st.columns(2)
            
            with col1:
                if equipment_options:
                    selected_equipment = st.selectbox("בחר פריט ציוד *", list(equipment_options.keys()))
                else:
                    st.warning("אין ציוד במערכת")
                    selected_equipment = None
            
            with col2:
                quantity_needed = st.number_input("כמות נדרשת *", min_value=1, value=1)
            
            urgency = st.selectbox("רמת דחיפות *", ["low", "medium", "high"],
                                  format_func=lambda x: {"low": "🟢 נמוכה", "medium": "🟡 בינונית", "high": "🔴 גבוהה"}[x])
            
            notes = st.text_area("הערות נוספות")
            
            submit = st.form_submit_button("📤 שלח דיווח", use_container_width=True)
            
            if submit:
                if not selected_equipment or not equipment_options:
                    st.error("❌ אנא בחר פריט ציוד")
                else:
                    try:
                        report_data = {
                            "equipment_id": equipment_options[selected_equipment],
                            "employee_id": user['id'],
                            "quantity_needed": quantity_needed,
                            "urgency": urgency,
                            "status": "pending",
                            "notes": notes if notes else None
                        }
                        supabase.table("equipment_reports").insert(report_data).execute()
                        st.success("✅ הדיווח נשלח בהצלחה!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ שגיאה: {str(e)}")
    
    # טאב 2: הדיווחים שלי
    with tab2:
        st.subheader("📋 הדיווחים שלי")
        
        try:
            my_reports = supabase.table("equipment_reports") \
                .select("*, equipment(name)") \
                .eq("employee_id", user['id']) \
                .order("created_at", desc=True) \
                .execute()
            
            if my_reports.data and len(my_reports.data) > 0:
                for report in my_reports.data:
                    status_icon = "⏳" if report['status'] == 'pending' else "✅"
                    equipment_name = report['equipment']['name'] if report['equipment'] else 'לא ידוע'
                    
                    st.markdown(f"{status_icon} **{equipment_name}** - {report['quantity_needed']} יח' ({report['created_at'][:10]})")
            else:
                st.info("לא שלחת דיווחים עדיין")
        
        except Exception as e:
            st.error(f"שגיאה: {str(e)}")
