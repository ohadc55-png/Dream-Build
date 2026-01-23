import streamlit as st

def apply_custom_css():
    """החלת עיצוב מותאם אישית - גרסת פרונטאנד פרו"""
    
    # כתובות התמונות
    bg_image_url = "https://i.postimg.cc/TY5ZZGd5/סדנא.jpg"
    logo_url = "https://i.postimg.cc/SKL4H4GV/לוגו_D_B.png"
    
    st.markdown(f"""
    <style>
    /* ייבוא פונט היבו */
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700;900&display=swap');
    
    /* הגדרות בסיס */
    * {{
        font-family: 'Heebo', sans-serif !important;
    }}
    
    /* רקע האפליקציה עם Overlay */
    .stApp {{
        background: 
            linear-gradient(rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.92)),
            url('{bg_image_url}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* עיצוב כותרות */
    h1, h2, h3 {{
        color: #1A2840 !important; /* כחול כהה */
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }}
    
    /* הדגשת צבע כתום */
    .highlight {{
        color: #FF8C00;
    }}
    
    /* כפתורים ראשיים */
    .stButton > button {{
        background: linear-gradient(135deg, #FF8C00 0%, #FF6B00 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(255, 140, 0, 0.2);
        transition: all 0.3s ease;
        width: 100%;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 140, 0, 0.3);
    }}
    
    /* כרטיסים (Cards) */
    .stMetric, div[data-testid="stForm"] {{
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }}
    
    /* שדות קלט */
    .stTextInput input, .stSelectbox select, .stNumberInput input {{
        border-radius: 10px !important;
        border: 2px solid #E0E0E0 !important;
        padding: 10px !important;
    }}
    
    .stTextInput input:focus {{
        border-color: #FF8C00 !important;
        box-shadow: 0 0 0 2px rgba(255, 140, 0, 0.1) !important;
    }}
    
    /* סרגל צד */
    [data-testid="stSidebar"] {{
        background-color: #1A2840;
        background-image: linear-gradient(180deg, #1A2840 0%, #0F1724 100%);
        border-left: 1px solid rgba(255,255,255,0.1);
    }}
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
        color: white !important;
    }}
    
    /* התאמת לוגו בתפריט */
    .sidebar-logo {{
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    /* הודעות */
    .stSuccess, .stInfo, .stWarning, .stError {{
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    
    </style>
    """, unsafe_allow_html=True)