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

        # ── Passo 1: JS lê o fragmento da janela PAI e redireciona ──────────
        if "access_token" not in params:
            st.components.v1.html("""
                <script>
                    try {
                        // O Streamlit roda em iframe — precisa acessar a janela pai
                        const hash = (window.parent || window).location.hash.substring(1);

                        if (hash && hash.includes("access_token")) {
                            const p = new URLSearchParams(hash);
                            const at = p.get("access_token") || "";
                            const rt = p.get("refresh_token") || "";
                            const tp = p.get("type") || "";

                            const base = (window.parent || window).location.origin
                                       + (window.parent || window).location.pathname;

                            (window.parent || window).location.href = base
                                + "?access_token=" + encodeURIComponent(at)
                                + "&refresh_token=" + encodeURIComponent(rt)
                                + "&type="          + encodeURIComponent(tp);
                        } else {
                            document.getElementById("msg").innerText =
                                "❌ Link inválido ou expirado. Peça ao administrador um novo convite.";
                        }
                    } catch(e) {
                        document.getElementById("msg").innerText = "Erro: " + e.message;
                    }
                </script>
                <p id="msg" style="font-family:sans-serif;color:gray;">🔄 Carregando, aguarde...</p>
            """, height=60)
            return

        # ── Passo 2: tokens disponíveis, mostra formulário ─────────────────
        access_token  = params.get("access_token", "")
        refresh_token = params.get("refresh_token", "")
        token_type    = params.get("type", "")

        if not access_token or token_type != "invite":
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
                    sb.auth.set_session(access_token, refresh_token)
                    sb.auth.update_user({"password": nova_senha})
                    st.success("✅ Senha definida com sucesso! Você já pode fazer login.")
                    st.balloons()
                    st.markdown("👉 [Ir para o login](/)")
                except Exception as e:
                    st.error(f"Erro ao definir senha: {e}")


cadastro_page()
