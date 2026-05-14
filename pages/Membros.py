import locale
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

import streamlit as st
import pandas as pd
from database import get_supabase
from auth import require_auth
from datetime import date


st.set_page_config(page_title="Membros", page_icon="🙋", layout="wide")

require_auth()
st.title("🙋 Membros / Participantes")
st.markdown("---")

sb = get_supabase()

# Carrega grupos para uso nos selects
grupos_resp = sb.table("grupos").select("id, nome").eq("ativo", True).order("nome").execute()
grupos = grupos_resp.data or []
grupos_map = {g["nome"]: g["id"] for g in grupos}
grupos_map_inv = {g["id"]: g["nome"] for g in grupos}

tab1, tab2, tab3 = st.tabs(["📋 Listar", "➕ Cadastrar", "✏️ Editar / Excluir"])

# ── TAB 1: LISTAR ──────────────────────────────────────────
with tab1:
    st.subheader("Membros Cadastrados")
    filtro_grupo = st.selectbox("Filtrar por grupo", ["Todos"] + list(grupos_map.keys()))

    query = sb.table("membros").select("*").order("nome")
    if filtro_grupo != "Todos":
        query = query.eq("grupo_id", grupos_map[filtro_grupo])
    dados = query.execute().data or []

    if dados:
        df = pd.DataFrame(dados)
        df["grupo"] = df["grupo_id"].map(grupos_map_inv).fillna("—")
        df["ativo"] = df["ativo"].map({True: "✅", False: "❌"})
        df = df.rename(columns={
            "id": "ID", "nome": "Nome", "data_nascimento": "Nascimento",
            "contato": "Contato", "responsavel": "Responsável", "grupo": "Grupo", "ativo": "Ativo"
        })
        st.dataframe(df[["ID","Nome","Nascimento","Contato","Responsável","Grupo","Ativo"]], use_container_width=True)
        st.caption(f"Total: {len(dados)} membro(s)")
    else:
        st.info("Nenhum membro encontrado.")

# ── TAB 2: CADASTRAR ───────────────────────────────────────
with tab2:
    st.subheader("Novo Membro")
    with st.form("form_novo_membro"):
        nome = st.text_input("Nome completo *", placeholder="Ex: João da Silva")
        col1, col2 = st.columns(2)
        with col1:
            # nasc = st.date_input("Data de nascimento", value=None)
            nasc = st.date_input("Data de nascimento", value=None, min_value=date(1900, 1, 1))
        with col2:
            contato = st.text_input("Contato (WhatsApp)", placeholder="(11) 99999-9999")
        responsavel = st.text_input("Responsável (se menor de idade)", placeholder="Nome do responsável")
        grupo_sel = st.selectbox("Grupo / Turma", ["— Nenhum —"] + list(grupos_map.keys()))
        submitted = st.form_submit_button("✅ Cadastrar Membro", type="primary")
        if submitted:
            if not nome.strip():
                st.error("O nome é obrigatório.")
            else:
                gid = grupos_map.get(grupo_sel) if grupo_sel != "— Nenhum —" else None
                sb.table("membros").insert({
                    "nome": nome.strip(),
                    "data_nascimento": str(nasc) if nasc else None,
                    "contato": contato.strip() or None,
                    "responsavel": responsavel.strip() or None,
                    "grupo_id": gid,
                    "ativo": True
                }).execute()
                
                
                st.success(f"Membro **{nome}** cadastrado!")
                st.rerun()

# ── TAB 3: EDITAR / EXCLUIR ────────────────────────────────
with tab3:
    st.subheader("Editar ou Excluir Membro")
    membros_resp = sb.table("membros").select("id, nome").order("nome").execute()
    membros_lista = membros_resp.data or []
    opcoes = {f"{m['id']} - {m['nome']}": m["id"] for m in membros_lista}

    if not opcoes:
        st.info("Nenhum membro para editar.")
    else:
        escolha = st.selectbox("Selecione o membro", list(opcoes.keys()))
        mid = opcoes[escolha]
        m = sb.table("membros").select("*").eq("id", mid).single().execute().data

        with st.form("form_editar_membro"):
            nome_e = st.text_input("Nome *", value=m["nome"])
            col1, col2 = st.columns(2)
            with col1:
                nasc_e = st.date_input("Nascimento", value=pd.to_datetime(m["data_nascimento"]).date() if m["data_nascimento"] else None)
            with col2:
                contato_e = st.text_input("Contato", value=m["contato"] or "")
            resp_e = st.text_input("Responsável", value=m["responsavel"] or "")
            grupo_opcoes = ["— Nenhum —"] + list(grupos_map.keys())
            grupo_atual = grupos_map_inv.get(m["grupo_id"], "— Nenhum —")
            idx = grupo_opcoes.index(grupo_atual) if grupo_atual in grupo_opcoes else 0
            grupo_e = st.selectbox("Grupo", grupo_opcoes, index=idx)
            ativo_e = st.checkbox("Ativo", value=m["ativo"])

            col1, col2 = st.columns(2)
            with col1:
                salvar = st.form_submit_button("💾 Salvar", type="primary")
            with col2:
                excluir = st.form_submit_button("🗑️ Excluir", type="secondary")

        if salvar:
            gid = grupos_map.get(grupo_e) if grupo_e != "— Nenhum —" else None
            sb.table("membros").update({
                "nome": nome_e.strip(),
                "data_nascimento": str(nasc_e) if nasc_e else None,
                "contato": contato_e.strip() or None,
                "responsavel": resp_e.strip() or None,
                "grupo_id": gid,
                "ativo": ativo_e
            }).eq("id", mid).execute()
            st.success("Membro atualizado!")
            st.rerun()

        if excluir:
            sb.table("membros").delete().eq("id", mid).execute()
            st.warning("Membro excluído.")
            st.rerun()
