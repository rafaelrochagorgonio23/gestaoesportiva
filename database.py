import os
from supabase import create_client, Client
import streamlit as st


def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY", "")
    if not url or not key:
        st.error("⚠️ Credenciais do Supabase não configuradas. Verifique o arquivo .env")
        st.stop()
    return create_client(url, key)
