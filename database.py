import os
from supabase import create_client, Client
import streamlit as st


def get_supabase() -> Client:
    """Cliente normal (anon key) — uso geral no app."""
    url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY", "")
    if not url or not key:
        st.error("⚠️ Credenciais do Supabase não configuradas. Verifique o arquivo .env")
        st.stop()
    return create_client(url, key)


def get_supabase_admin() -> Client:
    """Cliente admin (service_role key) — apenas para operações administrativas.
    NUNCA exponha a service_role key no frontend ou para o usuário.
    """
    url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL", "")
    service_key = os.getenv("SUPABASE_SERVICE_KEY") or st.secrets.get("SUPABASE_SERVICE_KEY", "")
    if not url or not service_key:
        st.error("⚠️ Service key do Supabase não configurada. Adicione SUPABASE_SERVICE_KEY no secrets.")
        st.stop()
    return create_client(url, service_key)
