
import streamlit as st
from database import get_supabase

def cadastro_page():
    st.set_page_config(page_title="Definir Senha", page_icon="⚽", layout="centered")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## ⚽ Gestão Esportiva Social")
        st.markdown("### Defina sua senha")
        st.markdown("---")
        
        # Pega o token da URL
        params = st.query_params
        token = params.get("token", None)
        token_type = params.get("type", None)
        
        if not token or token_type != "invite":
            st.error("Link inválido ou expirado. Peça ao administrador um novo convite.")
            st.stop()
        
        with st.form("form_senha"):
            nova_senha = st.text_input("🔒 Nova senha", type="password")
            confirma = st.text_input("🔒 Confirme a senha", type="password")
            salvar = st.form_submit_button("Definir senha", type="primary", use_container_width=True)
        
        if salvar:
            if not nova_senha or not confirma:
                st.error("Preencha os dois campos.")
            elif nova_senha != confirma:
                st.error("As senhas não coincidem.")
            elif len(nova_senha) < 6:
                st.error("A senha deve ter pelo menos 6 caracteres.")
            else:
                sb = get_supabase()
                try:
                    # Troca o token pela sessão e atualiza a senha
                    sb.auth.exchange_code_for_session({"token": token, "type": "invite"})
                    sb.auth.update_user({"password": nova_senha})
                    st.success("Senha definida com sucesso! Você já pode fazer login.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro ao definir senha: {e}")
