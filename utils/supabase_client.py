from supabase import create_client, Client
import streamlit as st

@st.cache_resource
def get_supabase_client() -> Client:
    """יצירת חיבור ל-Supabase"""
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# יצירת instance גלובלי
supabase: Client = get_supabase_client()
