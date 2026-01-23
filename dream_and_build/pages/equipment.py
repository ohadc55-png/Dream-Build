import streamlit as st
from utils.auth import check_auth
from utils.styling import apply_custom_css
from utils.supabase_client import supabase
from utils.nav import render_sidebar
import pandas as pd
from datetime import datetime

# === הגדרות עמוד ===
st.set_page_config(page_title="ניהול ציוד | Dream & Build", page_icon="🔧", layout="wide")
apply_custom_css()
render_sidebar()

# === וידוא הרשאות ===
user = check_auth()
is_manager = user.get('role') == 'manager'

# === כותרת ===
st.markdown(f"""
<h1 style='margin-bottom: 0;'>🔧 {'ניהול ציוד ומלאי' if is_manager else 'דיווח ציוד'}</h1>
<p style='color: #6B7280; margin-top: 0.25rem;'>{'מעקב מלאי, התראות וחוסרים' if is_manager else 'דיווח על חוסרים ותקלות'}</p>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# === טאבים ===
if is_manager:
    tab1, tab2, tab3, tab4 = st.tabs(["📦 מצב מלאי", "⚠️ התראות", "➕ הוספת פריט", "📝 דיווחי עובדים"])
else:
    tab1, tab2 = st.tabs(["📝 דיווח חוסר", "📋 הדיווחים שלי"])

# ========================================
# מנהל - טאב 1: מצב מלאי
# ========================================
if is_manager:
    with tab1:
        # פילטרים
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            search = st.text_input("🔍 חיפוש", placeholder="שם פריט...")
        with col_f2:
            category_options = ["הכל", "כלים", "חומרים", "בטיחות", "אחר"]
            category_filter = st.selectbox("קטגוריה", category_options)
        
        try:
            # שליפת ציוד
            query = supabase.table("equipment").select("*").order("name")
            if search:
                query = query.ilike("name", f"%{search}%")
            if category_filter != "הכל":
                query = query.eq("category", category_filter)
            
            equipment = query.execute()
            
            if equipment.data:
                # סטטיסטיקות
                total_items = len(equipment.data)
                low_stock = [e for e in equipment.data if (e.get('quantity_available', 0) or 0) <= (e.get('min_threshold', 0) or 0)]
                out_of_stock = [e for e in equipment.data if (e.get('quantity_available', 0) or 0) == 0]
                
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    st.metric("סה״כ פריטים", total_items)
                with col_s2:
                    st.metric("⚠️ מלאי נמוך", len(low_stock))
                with col_s3:
                    st.metric("❌ אזל מהמלאי", len(out_of_stock))
                
                st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                
                # טבלת מלאי
                rows = []
                for item in equipment.data:
                    qty = item.get('quantity_available', 0) or 0
                    threshold = item.get('min_threshold', 0) or 0
                    
                    if qty == 0:
                        status = "❌ אזל"
                        bg_color = "#FEE2E2"
                    elif qty <= threshold:
                        status = "⚠️ נמוך"
                        bg_color = "#FEF3C7"
                    else:
                        status = "✅ תקין"
                        bg_color = "#D1FAE5"
                    
                    rows.append({
                        'id': item['id'],
                        'שם': item['name'],
                        'קטגוריה': item.get('category', '-') or '-',
                        'זמין': qty,
                        'מינימום': threshold,
                        'סטטוס': status
                    })
                
                df = pd.DataFrame(rows)
                st.dataframe(df[['שם', 'קטגוריה', 'זמין', 'מינימום', 'סטטוס']], use_container_width=True, hide_index=True)
                
                # עריכת פריט
                st.markdown("---")
                st.markdown("### ⚙️ עדכון מלאי")
                
                item_names = [e['name'] for e in equipment.data]
                selected_item_name = st.selectbox("בחר פריט", item_names)
                
                if selected_item_name:
                    selected_item = next(e for e in equipment.data if e['name'] == selected_item_name)
                    
                    with st.form("update_stock"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_qty = st.number_input("כמות זמינה", value=int(selected_item.get('quantity_available', 0) or 0), min_value=0)
                        with col2:
                            edit_threshold = st.number_input("מינימום להתראה", value=int(selected_item.get('min_threshold', 0) or 0), min_value=0)
                        
                        if st.form_submit_button("💾 עדכן", use_container_width=True):
                            supabase.table("equipment").update({
                                "quantity_available": edit_qty,
                                "min_threshold": edit_threshold
                            }).eq("id", selected_item['id']).execute()
                            st.success("✅ עודכן!")
                            st.rerun()
            else:
                st.info("אין פריטים במערכת")
                
        except Exception as e:
            st.error(f"שגיאה: {str(e)}")
    
    # מנהל - טאב 2: התראות
    with tab2:
        st.markdown("### ⚠️ פריטים הדורשים התייחסות")
        
        try:
            equipment = supabase.table("equipment").select("*").execute()
            
            if equipment.data:
                alerts = []
                for item in equipment.data:
                    qty = item.get('quantity_available', 0) or 0
                    threshold = item.get('min_threshold', 0) or 0
                    
                    if qty <= threshold:
                        urgency = "קריטי" if qty == 0 else "נמוך"
                        alerts.append({
                            'פריט': item['name'],
                            'קטגוריה': item.get('category', '-'),
                            'זמין': qty,
                            'מינימום': threshold,
                            'חסר': max(0, threshold - qty),
                            'דחיפות': urgency
                        })
                
                if alerts:
                    df_alerts = pd.DataFrame(alerts)
                    
                    # הצגת התראות
                    for _, alert in df_alerts.iterrows():
                        color = "#FEE2E2" if alert['דחיפות'] == "קריטי" else "#FEF3C7"
                        border_color = "#EF4444" if alert['דחיפות'] == "קריטי" else "#F59E0B"
                        icon = "🔴" if alert['דחיפות'] == "קריטי" else "🟡"
                        
                        st.markdown(f"""
                        <div style='background: {color}; padding: 1rem; border-radius: 10px; border-right: 4px solid {border_color}; margin-bottom: 0.5rem;'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <div style='font-weight: 600;'>{icon} {alert['פריט']}</div>
                                    <div style='font-size: 0.85rem; color: #6B7280;'>זמין: {alert['זמין']} | מינימום: {alert['מינימום']} | חסר: {alert['חסר']}</div>
                                </div>
                                <span style='background: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem;'>{alert['דחיפות']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("✅ אין התראות - כל הפריטים במלאי תקין!")
            else:
                st.info("אין פריטים במערכת")
                
        except Exception as e:
            st.error(f"שגיאה: {str(e)}")
    
    # מנהל - טאב 3: הוספת פריט
    with tab3:
        st.markdown("### ➕ הוספת פריט חדש למלאי")
        
        with st.form("add_equipment"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("שם הפריט *")
                new_category = st.selectbox("קטגוריה", ["כלים", "חומרים", "בטיחות", "אחר"])
            
            with col2:
                new_qty = st.number_input("כמות התחלתית", min_value=0, value=0)
                new_threshold = st.number_input("מינימום להתראה", min_value=0, value=5)
            
            new_notes = st.text_area("הערות")
            
            if st.form_submit_button("➕ הוסף פריט", use_container_width=True):
                if not new_name:
                    st.error("❌ נא למלא שם פריט")
                else:
                    try:
                        supabase.table("equipment").insert({
                            "name": new_name,
                            "category": new_category,
                            "quantity_available": new_qty,
                            "min_threshold": new_threshold,
                            "notes": new_notes or None
                        }).execute()
                        st.success(f"✅ הפריט '{new_name}' נוסף!")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ שגיאה: {str(e)}")
    
    # מנהל - טאב 4: דיווחי עובדים
    with tab4:
        st.markdown("### 📝 דיווחי חוסרים מעובדים")
        
        try:
            reports = supabase.table("equipment_reports") \
                .select("*, users(full_name), equipment(name)") \
                .order("created_at", desc=True) \
                .limit(50) \
                .execute()
            
            if reports.data:
                for report in reports.data:
                    status_color = "#FEF3C7" if report.get('status') == 'pending' else "#D1FAE5"
                    status_text = "ממתין" if report.get('status') == 'pending' else "טופל"
                    
                    st.markdown(f"""
                    <div style='background: {status_color}; padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem;'>
                        <div style='display: flex; justify-content: space-between;'>
                            <div>
                                <div style='font-weight: 600;'>{report['equipment']['name'] if report.get('equipment') else 'לא ידוע'}</div>
                                <div style='font-size: 0.85rem; color: #6B7280;'>
                                    דיווח: {report['users']['full_name'] if report.get('users') else '-'} | 
                                    {report.get('created_at', '')[:10]}
                                </div>
                                <div style='font-size: 0.9rem; margin-top: 0.25rem;'>{report.get('description', '')}</div>
                            </div>
                            <span style='font-size: 0.8rem;'>{status_text}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # כפתור לסימון כטופל
                    if report.get('status') == 'pending':
                        if st.button("✅ סמן כטופל", key=f"resolve_{report['id']}"):
                            supabase.table("equipment_reports").update({"status": "resolved"}).eq("id", report['id']).execute()
                            st.rerun()
            else:
                st.success("✅ אין דיווחים ממתינים")
                
        except Exception as e:
            st.error(f"שגיאה: {str(e)}")

# ========================================
# עובד - טאב 1: דיווח חוסר
# ========================================
else:
    with tab1:
        st.markdown("### 📝 דיווח על חוסר ציוד")
        
        try:
            equipment = supabase.table("equipment").select("id, name").order("name").execute()
            
            if equipment.data:
                with st.form("report_shortage"):
                    item_options = {e['name']: e['id'] for e in equipment.data}
                    selected_item = st.selectbox("בחר פריט", list(item_options.keys()))
                    
                    report_type = st.selectbox("סוג הדיווח", ["חוסר במלאי", "פריט פגום", "צריך להזמין", "אחר"])
                    description = st.text_area("תיאור הבעיה")
                    
                    if st.form_submit_button("📤 שלח דיווח", use_container_width=True):
                        if not description:
                            st.error("❌ נא לתאר את הבעיה")
                        else:
                            supabase.table("equipment_reports").insert({
                                "equipment_id": item_options[selected_item],
                                "reported_by": user['id'],
                                "report_type": report_type,
                                "description": description,
                                "status": "pending"
                            }).execute()
                            st.success("✅ הדיווח נשלח בהצלחה!")
                            st.balloons()
            else:
                st.info("אין פריטי ציוד במערכת")
                
        except Exception as e:
            st.error(f"שגיאה: {str(e)}")
    
    # עובד - טאב 2: הדיווחים שלי
    with tab2:
        st.markdown("### 📋 הדיווחים שלי")
        
        try:
            my_reports = supabase.table("equipment_reports") \
                .select("*, equipment(name)") \
                .eq("reported_by", user['id']) \
                .order("created_at", desc=True) \
                .execute()
            
            if my_reports.data:
                for report in my_reports.data:
                    status_color = "#FEF3C7" if report.get('status') == 'pending' else "#D1FAE5"
                    status_text = "⏳ ממתין" if report.get('status') == 'pending' else "✅ טופל"
                    
                    st.markdown(f"""
                    <div style='background: {status_color}; padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem;'>
                        <div style='font-weight: 600;'>{report['equipment']['name'] if report.get('equipment') else '-'}</div>
                        <div style='font-size: 0.85rem; color: #6B7280;'>{report.get('created_at', '')[:10]} | {status_text}</div>
                        <div style='margin-top: 0.25rem;'>{report.get('description', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("לא שלחת דיווחים עדיין")
                
        except Exception as e:
            st.error(f"שגיאה: {str(e)}")
