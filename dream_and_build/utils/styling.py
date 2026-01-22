import streamlit as st

def apply_custom_css():
    """החלת עיצוב מותאם אישית"""
    st.markdown("""
    <style>
    /* ייבוא פונטים בעברית */
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700&display=swap');
    
    /* הגדרות כלליות */
    * {
        font-family: 'Heebo', sans-serif !important;
        direction: rtl;
    }
    
    /* רקע עם תמונת הסדנה */
    .stApp {
        background: linear-gradient(rgba(255, 255, 255, 0.55), rgba(255, 255, 255, 0.55)),
                    url('data:image/jpeg;base64,/9j/4AAQSkZJRg...') center/cover no-repeat fixed;
        background-color: #F5F5F5;
    }
    
    /* צבעים ראשיים */
    :root {
        --orange-primary: #FF8C00;
        --orange-light: #FFA500;
        --blue-dark: #1A2840;
        --blue-medium: #2C3E50;
        --gray-light: #E8E8E8;
        --wood-brown: #A67C52;
        --cream: #F5F5F5;
    }
    
    /* כותרות */
    h1, h2, h3 {
        color: var(--blue-dark) !important;
        font-weight: 700 !important;
    }
    
    /* כפתורים */
    .stButton > button {
        background: linear-gradient(135deg, var(--orange-primary) 0%, var(--orange-light) 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(255, 140, 0, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(255, 140, 0, 0.4);
        background: linear-gradient(135deg, var(--orange-light) 0%, var(--orange-primary) 100%);
    }
    
    /* שדות קלט */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        border: 2px solid var(--gray-light) !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--orange-primary) !important;
        box-shadow: 0 0 0 3px rgba(255, 140, 0, 0.1) !important;
    }
    
    /* טאבים */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        color: var(--blue-dark);
        font-weight: 500;
        border: 2px solid var(--gray-light);
        border-bottom: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--orange-primary) 0%, var(--orange-light) 100%);
        color: white !important;
        border-color: var(--orange-primary);
    }
    
    /* כרטיסים */
    .element-container div[data-testid="stMetric"] {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-right: 4px solid var(--orange-primary);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--blue-dark) 0%, var(--blue-medium) 100%);
        color: white !important;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 140, 0, 0.2);
        border: 2px solid var(--orange-primary);
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: var(--orange-primary);
    }
    
    /* הודעות */
    .stSuccess {
        background-color: rgba(0, 200, 100, 0.1);
        border-right: 4px solid #00C864;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stError {
        background-color: rgba(255, 75, 75, 0.1);
        border-right: 4px solid #FF4B4B;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stWarning {
        background-color: rgba(255, 196, 0, 0.1);
        border-right: 4px solid #FFC400;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stInfo {
        background-color: rgba(33, 150, 243, 0.1);
        border-right: 4px solid #2196F3;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* טבלאות */
    .dataframe {
        border: none !important;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, var(--blue-dark) 0%, var(--blue-medium) 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 1rem !important;
    }
    
    .dataframe tbody tr:hover {
        background-color: rgba(255, 140, 0, 0.05) !important;
    }
    
    /* פורמים */
    .stForm {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border: 1px solid var(--gray-light);
    }
    
    /* Badge לציוד */
    .equipment-badge {
        display: inline-block;
        background: #FF4B4B;
        color: white;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        text-align: center;
        line-height: 24px;
        font-weight: bold;
        font-size: 0.8rem;
        margin-right: 8px;
    }
    
    /* אנימציות */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .element-container {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* התאמה למובייל */
    @media (max-width: 768px) {
        .stButton > button {
            width: 100%;
            padding: 0.75rem;
        }
        
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.25rem !important;
        }
        
        .element-container div[data-testid="stMetric"] {
            padding: 1rem;
        }
    }
    
    /* הסתרת אלמנטים מיותרים */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
