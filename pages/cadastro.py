import streamlit as st
from database import get_supabase


def cadastro_page():
    st.set_page_config(page_title="Definir Senha", page_icon="⚽", layout="centered")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## ⚽ Gestão Esportiva Social")
        st.markdown("### Defina sua senha")
        st.markdown("---")

        params     = st.query_params
        token_hash = params.get("token_hash", "")
        token_type = params.get("type", "")

        if not token_hash or token_type != "invite":
            st.error("Link inválido ou expirado. Peça ao administrador um novo convite.")
            return

        with st.form("form_senha"):
            nova_senha = st.text_input("🔒 Nova senha", type="password")
            confirma   = st.text_input("🔒 Confirme a senha", type="password")
            salvar     = st.form_submit_button(
                "Definir senha", type="primary", use_container_width=True
            )

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
                    # Troca o token_hash por uma sessão válida
                    sb.auth.verify_otp({
                        "token_hash": token_hash,
                        "type": "invite"
                    })
                    # Atualiza a senha
                    sb.auth.update_user({"password": nova_senha})
                    st.success("✅ Senha definida com sucesso! Você já pode fazer login.")
                    st.balloons()
                    st.markdown("👉 [Ir para o login](/)")
                except Exception as e:
                    st.error(f"Erro ao definir senha: {e}")


cadastro_page()
