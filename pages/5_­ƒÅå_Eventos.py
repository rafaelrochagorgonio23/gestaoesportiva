import streamlit as st
import pandas as pd
from datetime import date
from database import get_supabase
from auth import require_auth

st.set_page_config(page_title="Eventos", page_icon="🏆", layout="wide")

require_auth()
st.title("🏆 Eventos e Festivais Comunitários")
st.markdown("---")

sb = get_supabase()

grupos_resp = sb.table("grupos").select("id, nome").eq("ativo", True).order("nome").execute()
grupos = grupos_resp.data or []
grupos_map = {g["nome"]: g["id"] for g in grupos}
grupos_map_inv = {g["id"]: g["nome"] for g in grupos}

tab1, tab2, tab3 = st.tabs(["📋 Listar", "➕ Criar Evento", "✏️ Editar / Excluir"])

# ── TAB 1: LISTAR ──────────────────────────────────────────
with tab1:
    st.subheader("Eventos Cadastrados")
    col1, col2 = st.columns(2)
    with col1:
        periodo = st.radio("Período", ["Futuros", "Passados", "Todos"], horizontal=True)

    query = sb.table("eventos").select("*").order("data_evento")
    if periodo == "Futuros":
        query = query.gte("data_evento", str(date.today()))
    elif periodo == "Passados":
        query = query.lt("data_evento", str(date.today()))

    dados = query.execute().data or []
    if dados:
        rows = []
        for d in dados:
            rows.append({
                "ID": d["id"],
                "Evento": d["nome"],
                "Data": d["data_evento"],
                "Local": d["local"] or "—",
                "Grupo": grupos_map_inv.get(d["grupo_id"], "—"),
                "Descrição": d["descricao"] or ""
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
        st.caption(f"Total: {len(dados)} evento(s)")
    else:
        st.info("Nenhum evento encontrado.")

# ── TAB 2: CRIAR ───────────────────────────────────────────
with tab2:
    st.subheader("Novo Evento / Festival")
    with st.form("form_evento"):
        nome = st.text_input("Nome do evento *", placeholder="Ex: Festival de Futebol Comunitário")
        descricao = st.text_area("Descrição", placeholder="Detalhes do evento, objetivo, atividades...")
        col1, col2 = st.columns(2)
        with col1:
            data_ev = st.date_input("Data do evento *", value=date.today())
        with col2:
            local = st.text_input("Local", placeholder="Ex: Ginásio Municipal")
        grupo_sel = st.selectbox("Grupo organizador", ["— Nenhum —"] + list(grupos_map.keys()))
        submitted = st.form_submit_button("✅ Criar Evento", type="primary")
        if submitted:
            if not nome.strip():
                st.error("O nome do evento é obrigatório.")
            else:
                gid = grupos_map.get(grupo_sel) if grupo_sel != "— Nenhum —" else None
                sb.table("eventos").insert({
                    "nome": nome.strip(),
                    "descricao": descricao.strip() or None,
                    "data_evento": str(data_ev),
                    "local": local.strip() or None,
                    "grupo_id": gid
                }).execute()
                st.success(f"Evento **{nome}** criado!")
                st.rerun()

# ── TAB 3: EDITAR / EXCLUIR ────────────────────────────────
with tab3:
    st.subheader("Editar ou Excluir Evento")
    dados_edit = sb.table("eventos").select("id, nome, data_evento").order("data_evento", desc=True).execute().data or []
    if not dados_edit:
        st.info("Nenhum evento para editar.")
    else:
        opcoes = {f"{d['id']} | {d['nome']} | {d['data_evento']}": d["id"] for d in dados_edit}
        escolha = st.selectbox("Evento", list(opcoes.keys()))
        eid = opcoes[escolha]
        ev = sb.table("eventos").select("*").eq("id", eid).single().execute().data

        with st.form("form_editar_evento"):
            nome_e = st.text_input("Nome *", value=ev["nome"])
            desc_e = st.text_area("Descrição", value=ev["descricao"] or "")
            data_e = st.date_input("Data", value=pd.to_datetime(ev["data_evento"]).date())
            local_e = st.text_input("Local", value=ev["local"] or "")
            grupo_opcoes = ["— Nenhum —"] + list(grupos_map.keys())
            grupo_atual = grupos_map_inv.get(ev["grupo_id"], "— Nenhum —")
            idx = grupo_opcoes.index(grupo_atual) if grupo_atual in grupo_opcoes else 0
            grupo_e = st.selectbox("Grupo", grupo_opcoes, index=idx)
            col1, col2 = st.columns(2)
            with col1:
                salvar = st.form_submit_button("💾 Salvar", type="primary")
            with col2:
                excluir = st.form_submit_button("🗑️ Excluir", type="secondary")

        if salvar:
            gid = grupos_map.get(grupo_e) if grupo_e != "— Nenhum —" else None
            sb.table("eventos").update({
                "nome": nome_e.strip(),
                "descricao": desc_e.strip() or None,
                "data_evento": str(data_e),
                "local": local_e.strip() or None,
                "grupo_id": gid
            }).eq("id", eid).execute()
            st.success("Evento atualizado!")
            st.rerun()
        if excluir:
            sb.table("eventos").delete().eq("id", eid).execute()
            st.warning("Evento excluído.")
            st.rerun()
