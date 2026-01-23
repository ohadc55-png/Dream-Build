import streamlit as st

def apply_custom_css():
    """עיצוב מקצועי בסגנון דשבורד מודרני"""
    
    st.markdown("""
    <style>
    /* ===== ייבוא פונט ===== */
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800;900&display=swap');
    
    /* ===== משתני צבעים ===== */
    :root {
        --primary-dark: #1A2840;
        --primary-blue: #3B82F6;
        --green-dark: #047857;
        --green-light: #10B981;
        --orange-accent: #FF8C00;
        --orange-light: #FFA500;
        --gray-900: #111827;
        --gray-700: #374151;
        --gray-600: #4B5563;
        --gray-500: #6B7280;
        --gray-400: #9CA3AF;
        --gray-200: #E5E7EB;
        --gray-100: #F3F4F6;
        --gray-50: #F9FAFB;
        --white: #FFFFFF;
        --danger: #EF4444;
        --warning: #F59E0B;
    }
    
    /* ===== הגדרות כלליות ===== */
    * {
        font-family: 'Heebo', sans-serif !important;
    }
    
    /* ===== רקע עם תמונת סדנא ===== */
    .stApp {
        background-image: linear-gradient(rgba(243, 244, 246, 0.58), rgba(243, 244, 246, 0.58)), url('https://i.postimg.cc/TY5ZZGd5/סדנא.jpg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }
    
    /* ===== הסתרת תפריט ברירת מחדל של Streamlit ===== */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
    #MainMenu, footer {
        visibility: hidden;
    }
    
    /* ===== וידוא שכפתור פתיחת Sidebar נראה ===== */
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        color: var(--primary-dark) !important;
        background: white !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
    }
    
    [data-testid="collapsedControl"]:hover {
        background: var(--orange-accent) !important;
        color: white !important;
    }
    
    /* ===== שיפור נראות ה-Sidebar Toggle ===== */
    button[kind="header"] {
        display: block !important;
        visibility: visible !important;
    }
    
    /* ===== וידוא נוסף שהחץ נראה ===== */
    .css-1dp5vir, .css-1rs6os, .css-17lntkn {
        visibility: visible !important;
        display: flex !important;
    }
    
    /* ===== לוגו קטן בפינה (בדפים פנימיים) ===== */
    .page-header-logo {
        position: fixed;
        top: 0.75rem;
        left: 1rem;
        z-index: 999;
        opacity: 0.9;
    }
    
    .page-header-logo img {
        width: 50px;
        height: auto;
    }
    
    /* ===== Sidebar ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--primary-dark) 0%, #0F172A 100%);
        border-left: 1px solid rgba(255,255,255,0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: var(--white) !important;
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 140, 0, 0.15);
        border: 1px solid var(--orange-accent);
        color: var(--orange-accent) !important;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: var(--orange-accent);
        color: var(--white) !important;
        transform: translateX(-3px);
    }
    
    /* ===== כותרות ===== */
    h1 {
        color: var(--gray-900) !important;
        font-weight: 800 !important;
        font-size: 2rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2, h3 {
        color: var(--gray-700) !important;
        font-weight: 700 !important;
    }
    
    /* ===== Metric Cards ===== */
    [data-testid="stMetric"] {
        background: var(--white);
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
        border: 1px solid var(--gray-200);
        transition: all 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    [data-testid="stMetric"] label {
        color: var(--gray-500) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--gray-900) !important;
        font-size: 1.875rem !important;
        font-weight: 700 !important;
    }
    
    /* ===== כפתורים ===== */
    .stButton > button {
        background: linear-gradient(135deg, var(--orange-accent) 0%, var(--orange-light) 100%);
        color: var(--white) !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(255, 140, 0, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(255, 140, 0, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* ===== טפסים ===== */
    [data-testid="stForm"] {
        background: var(--white);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--gray-200);
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    /* ===== שדות קלט ===== */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stDateInput > div > div > input,
    .stTimeInput > div > div > input,
    .stNumberInput > div > div > input {
        border-radius: 8px !important;
        border: 1.5px solid var(--gray-200) !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus-within,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary-blue) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* ===== טאבים ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: var(--white);
        border-radius: 10px;
        padding: 4px;
        border: 1px solid var(--gray-200);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        color: var(--gray-600);
        background: transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary-dark) !important;
        color: var(--white) !important;
    }
    
    /* ===== טבלאות (DataFrame) ===== */
    [data-testid="stDataFrame"] {
        background: var(--white);
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--gray-200);
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    [data-testid="stDataFrame"] table {
        width: 100%;
    }
    
    [data-testid="stDataFrame"] thead tr th {
        background: var(--gray-50) !important;
        color: var(--gray-700) !important;
        font-weight: 600 !important;
        padding: 0.875rem 1rem !important;
        border-bottom: 2px solid var(--gray-200) !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    [data-testid="stDataFrame"] tbody tr td {
        padding: 0.75rem 1rem !important;
        border-bottom: 1px solid var(--gray-100) !important;
        color: var(--gray-700) !important;
    }
    
    [data-testid="stDataFrame"] tbody tr:hover td {
        background: var(--gray-50) !important;
    }
    
    /* ===== Expander ===== */
    .streamlit-expanderHeader {
        background: var(--white) !important;
        border: 1px solid var(--gray-200) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        color: var(--gray-700) !important;
    }
    
    .streamlit-expanderContent {
        background: var(--white) !important;
        border: 1px solid var(--gray-200) !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
    }
    
    /* ===== הודעות ===== */
    .stSuccess {
        background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
        color: var(--green-dark) !important;
        border: none;
        border-radius: 8px;
        border-right: 4px solid var(--green-dark);
    }
    
    .stError {
        background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
        color: #991B1B !important;
        border: none;
        border-radius: 8px;
        border-right: 4px solid var(--danger);
    }
    
    .stWarning {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        color: #92400E !important;
        border: none;
        border-radius: 8px;
        border-right: 4px solid var(--warning);
    }
    
    .stInfo {
        background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
        color: #1E40AF !important;
        border: none;
        border-radius: 8px;
        border-right: 4px solid var(--primary-blue);
    }
    
    /* ===== Divider ===== */
    hr {
        border: none;
        height: 1px;
        background: var(--gray-200);
        margin: 1.5rem 0;
    }
    
    /* ===== Progress Bar ===== */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--green-dark) 0%, var(--green-light) 100%);
        border-radius: 10px;
    }
    
    /* ===== Plotly Charts Customization ===== */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* ===== Custom Card Class ===== */
    .custom-card {
        background: var(--white);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--gray-200);
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    
    .card-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--gray-500);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .card-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--gray-900);
    }
    
    .card-value.green { color: var(--green-dark); }
    .card-value.blue { color: var(--primary-blue); }
    .card-value.orange { color: var(--orange-accent); }
    
    /* ===== Badge Styles ===== */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-success { background: #D1FAE5; color: #065F46; }
    .badge-warning { background: #FEF3C7; color: #92400E; }
    .badge-danger { background: #FEE2E2; color: #991B1B; }
    .badge-info { background: #DBEAFE; color: #1E40AF; }
    .badge-gray { background: #F3F4F6; color: #374151; }
    
    /* ===== Animation ===== */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .element-container {
        animation: fadeIn 0.3s ease-out;
    }
    
    /* ===== Responsive ===== */
    @media (max-width: 768px) {
        h1 { font-size: 1.5rem !important; }
        [data-testid="stMetric"] { padding: 1rem; }
        [data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    }
    
    </style>
    """, unsafe_allow_html=True)


def create_metric_card(title: str, value: str, color: str = "default", icon: str = ""):
    """יצירת כרטיס מטריקה מותאם אישית"""
    color_class = f"card-value {color}" if color != "default" else "card-value"
    icon_html = f"<span style='font-size: 1.5rem; margin-left: 0.5rem;'>{icon}</span>" if icon else ""
    
    return f"""
    <div class="custom-card">
        <div class="card-title">{icon_html}{title}</div>
        <div class="{color_class}">{value}</div>
    </div>
    """


def create_badge(text: str, status: str = "info"):
    """יצירת Badge"""
    return f'<span class="badge badge-{status}">{text}</span>'


def show_page_logo():
    """הצגת לוגו קטן בפינת הדף"""
    st.markdown("""
    <div class="page-header-logo">
        <img src='https://i.postimg.cc/SKL4H4GV/לוגו-D-B.png' alt='Logo'>
    </div>
    """, unsafe_allow_html=True)
