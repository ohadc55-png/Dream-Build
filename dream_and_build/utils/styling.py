import streamlit as st

def apply_custom_css():
    """החלת עיצוב מותאם אישית - כולל הסתרת תפריט ברירת מחדל"""
    
    bg_image_url = "https://i.postimg.cc/TY5ZZGd5/סדנא.jpg"
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700;900&display=swap');
    
    * {{ font-family: 'Heebo', sans-serif !important; }}
    
    .stApp {{
        background: linear-gradient(rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.92)),
                    url('{bg_image_url}');
        background-size: cover;
        background-attachment: fixed;
    }}
    
    /* --- קריטי: הסתרת התפריט האוטומטי באנגלית --- */
    [data-testid="stSidebarNav"] {{
        display: none !important;
    }}
    
    /* עיצוב כפתורים וכרטיסים */
    .stButton > button {{
        background: linear-gradient(135deg, #FF8C00 0%, #FF6B00 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(255, 140, 0, 0.2);
    }}
    
    h1, h2, h3 {{ color: #1A2840 !important; font-weight: 800 !important; }}
    
    .stMetric, div[data-testid="stForm"] {{
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }}
    
    /* Sidebar עיצוב */
    [data-testid="stSidebar"] {{
        background-image: linear-gradient(180deg, #1A2840 0%, #0F1724 100%);
    }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    
    </style>
    """, unsafe_allow_html=True)