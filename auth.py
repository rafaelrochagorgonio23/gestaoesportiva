import streamlit as st
from database import get_supabase, get_supabase_admin


# ─────────────────────────────────────────────
# CONVITE DE USUÁRIO
# ─────────────────────────────────────────────

def convidar_usuario(email: str) -> tuple[bool, str]:
    """
    Admin envia convite por e-mail.
    O usuário recebe um link para definir a própria senha.
    Requer service_role key no Supabase (Admin API).
    """
    sb = get_supabase_admin()
    try:
        sb.auth.admin.invite_user_by_email(email)
        return True, f"Convite enviado para {email} com sucesso!"
    except Exception as e:
        msg = str(e)
        if "already registered" in msg or "already been registered" in msg:
            return False, "Este e-mail já está cadastrado no sistema."
        elif "invalid" in msg.lower():
            return False, "E-mail inválido."
        else:
            return False, f"Erro ao enviar convite: {msg}"


# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────

def login_page():
    """Renderiza a tela de login."""
    st.set_page_config(page_title="Login", page_icon="⚽", layout="centered")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## ⚽ Gestão Esportiva Social")
        st.markdown("### Acesso ao Sistema")
        st.markdown("---")

        with st.form("form_login"):
            email = st.text_input("📧 E-mail", placeholder="seu@email.com")
            senha = st.text_input("🔒 Senha", type="password", placeholder="••••••••")
            entrar = st.form_submit_button("Entrar", type="primary", use_container_width=True)

        if entrar:
            if not email.strip() or not senha.strip():
                st.error("Preencha e-mail e senha.")
                return

            sb = get_supabase()
            try:
                resp = sb.auth.sign_in_with_password({"email": email.strip(), "password": senha.strip()})
                st.session_state["user"] = resp.user
                st.session_state["session"] = resp.session
                st.rerun()
            except Exception as e:
                msg = str(e)
                if "Invalid login" in msg or "invalid_credentials" in msg:
                    st.error("E-mail ou senha incorretos.")
                elif "Email not confirmed" in msg:
                    st.warning("Confirme seu e-mail antes de acessar.")
                else:
                    st.error(f"Erro ao autenticar: {msg}")

        st.markdown("---")

        # ── Painel de convite (protegido por senha admin) ─────────────────
        with st.expander("👤 Convidar novo usuário"):
            SENHA_ADMIN = st.secrets.get("ADMIN_PASSWORD", "admin123")

            senha_admin = st.text_input(
                "🔑 Senha do administrador",
                type="password",
                key="senha_admin_convite",
                placeholder="Digite a senha de admin"
            )

            if senha_admin and senha_admin != SENHA_ADMIN:
                st.error("Senha incorreta.")

            elif senha_admin == SENHA_ADMIN:
                with st.form("form_convite"):
                    email_novo = st.text_input(
                        "📧 E-mail do novo usuário",
                        placeholder="novo@email.com"
                    )
                    enviar = st.form_submit_button(
                        "📨 Enviar convite",
                        type="primary",
                        use_container_width=True
                    )

                if enviar:
                    if not email_novo.strip():
                        st.error("Informe o e-mail.")
                    else:
                        ok, msg = convidar_usuario(email_novo.strip())
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)


def logout():
    """Realiza logout e limpa a sessão."""
    sb = get_supabase()
    try:
        sb.auth.sign_out()
    except Exception:
        pass
    st.session_state.pop("user", None)
    st.session_state.pop("session", None)
    st.rerun()


def require_auth():
    """
    Verifica autenticação. Chame no topo de cada página.
    Redireciona para login se não autenticado.
    Retorna o usuário autenticado.
    """
    if "user" not in st.session_state or st.session_state["user"] is None:
        login_page()
        st.stop()

    # Botão de logout fixo na sidebar
    with st.sidebar:
        st.markdown("---")
        user = st.session_state["user"]
        st.caption(f"👤 {user.email}")
        if st.button("🚪 Sair", use_container_width=True):
            logout()

    return st.session_state["user"]
