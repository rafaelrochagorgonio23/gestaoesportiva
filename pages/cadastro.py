import streamlit as st
from database import get_supabase


def cadastro_page():
    st.set_page_config(page_title="Definir Senha", page_icon="⚽", layout="centered")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## ⚽ Gestão Esportiva Social")
        st.markdown("### Defina sua senha")
        st.markdown("---")

        params = st.query_params

        # ── Passo 1: token ainda está no fragmento (#) da URL ─────────────
        # JS lê o fragmento e redireciona adicionando como query param
        if "access_token" not in params:
            st.components.v1.html("""
                <script>
                    const hash = window.location.hash.substring(1);
                    if (hash) {
                        const hashParams = new URLSearchParams(hash);
                        const access_token = hashParams.get("access_token");
                        const refresh_token = hashParams.get("refresh_token");
                        const type = hashParams.get("type");

                        if (access_token) {
                            const newUrl = window.location.pathname
                                + "?access_token=" + encodeURIComponent(access_token)
                                + "&refresh_token=" + encodeURIComponent(refresh_token || "")
                                + "&type=" + encodeURIComponent(type || "");
                            window.location.replace(newUrl);
                        }
                    }
                </script>
                <p style="color: gray; font-size: 13px;">Carregando...</p>
            """, height=40)
            st.stop()

        # ── Passo 2: token disponível como query param ─────────────────────
        access_token  = params.get("access_token", "")
        refresh_token = params.get("refresh_token", "")
        token_type    = params.get("type", "")

        if not access_token or token_type != "invite":
            st.error("Link inválido ou expirado. Peça ao administrador um novo convite.")
            st.stop()

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
                    # Estabelece sessão a partir dos tokens do convite
                    sb.auth.set_session(access_token, refresh_token)
                    # Atualiza a senha do usuário
                    sb.auth.update_user({"password": nova_senha})
                    st.success("✅ Senha definida com sucesso! Você já pode fazer login.")
                    st.balloons()
                    st.markdown("👉 [Ir para o login](/)")
                except Exception as e:
                    st.error(f"Erro ao definir senha: {e}")


cadastro_page()
