import streamlit as st
import pandas as pd
from database import get_supabase
from auth import require_auth

st.set_page_config(page_title="Grupos", page_icon="👥", layout="wide")

require_auth()
st.title("👥 Grupos / Turmas / Patotas")
st.markdown("---")

sb = get_supabase()

tab1, tab2, tab3 = st.tabs(["📋 Listar", "➕ Cadastrar", "✏️ Editar / Excluir"])

# ── TAB 1: LISTAR ──────────────────────────────────────────
with tab1:
    st.subheader("Grupos Cadastrados")
    resp = sb.table("grupos").select("*").order("criado_em", desc=True).execute()
    dados = resp.data
    if dados:
        df = pd.DataFrame(dados)
        df["ativo"] = df["ativo"].map({True: "✅ Ativo", False: "❌ Inativo"})
        df = df.rename(columns={
            "id": "ID", "nome": "Nome", "descricao": "Descrição",
            "local": "Local", "dia_semana": "Dia", "horario": "Horário", "ativo": "Status"
        })
        st.dataframe(df[["ID","Nome","Descrição","Local","Dia","Horário","Status"]], use_container_width=True)
        st.caption(f"Total: {len(dados)} grupo(s)")
    else:
        st.info("Nenhum grupo cadastrado ainda.")

# ── TAB 2: CADASTRAR ───────────────────────────────────────
with tab2:
    st.subheader("Novo Grupo")
    with st.form("form_novo_grupo"):
        nome = st.text_input("Nome do grupo *", placeholder="Ex: Patota da Várzea - Manhã")
        descricao = st.text_area("Descrição", placeholder="Breve descrição do grupo ou projeto")
        local = st.text_input("Local / Quadra", placeholder="Ex: Campo Municipal do Bairro X")
        col1, col2 = st.columns(2)
        with col1:
            dia_semana = st.selectbox("Dia da semana", ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"])
        with col2:
            horario = st.time_input("Horário da atividade")
        submitted = st.form_submit_button("✅ Salvar Grupo", type="primary")
        if submitted:
            if not nome.strip():
                st.error("O nome do grupo é obrigatório.")
            else:
                sb.table("grupos").insert({
                    "nome": nome.strip(),
                    "descricao": descricao.strip() or None,
                    "local": local.strip() or None,
                    "dia_semana": dia_semana,
                    "horario": str(horario),
                    "ativo": True
                }).execute()
                st.success(f"Grupo **{nome}** cadastrado com sucesso!")
                st.rerun()

# ── TAB 3: EDITAR / EXCLUIR ────────────────────────────────
with tab3:
    st.subheader("Editar ou Excluir Grupo")
    resp2 = sb.table("grupos").select("id, nome").order("nome").execute()
    opcoes = {f"{g['id']} - {g['nome']}": g["id"] for g in (resp2.data or [])}
    if not opcoes:
        st.info("Nenhum grupo para editar.")
    else:
        escolha = st.selectbox("Selecione o grupo", list(opcoes.keys()))
        gid = opcoes[escolha]
        grupo = sb.table("grupos").select("*").eq("id", gid).single().execute().data

        with st.form("form_editar_grupo"):
            nome_e = st.text_input("Nome *", value=grupo["nome"])
            desc_e = st.text_area("Descrição", value=grupo["descricao"] or "")
            local_e = st.text_input("Local", value=grupo["local"] or "")
            dias = ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"]
            dia_e = st.selectbox("Dia", dias, index=dias.index(grupo["dia_semana"]) if grupo["dia_semana"] in dias else 0)
            ativo_e = st.checkbox("Ativo", value=grupo["ativo"])
            col1, col2 = st.columns(2)
            with col1:
                salvar = st.form_submit_button("💾 Salvar alterações", type="primary")
            with col2:
                excluir = st.form_submit_button("🗑️ Excluir grupo", type="secondary")

        if salvar:
            sb.table("grupos").update({
                "nome": nome_e.strip(),
                "descricao": desc_e.strip() or None,
                "local": local_e.strip() or None,
                "dia_semana": dia_e,
                "ativo": ativo_e
            }).eq("id", gid).execute()
            st.success("Grupo atualizado com sucesso!")
            st.rerun()

        if excluir:
            sb.table("grupos").delete().eq("id", gid).execute()
            st.warning("Grupo excluído.")
            st.rerun()
