import streamlit as st
import pandas as pd
from datetime import date
from database import get_supabase
from auth import require_auth

st.set_page_config(page_title="Recursos", page_icon="🎽", layout="wide")

require_auth()
st.title("🎽 Gestão de Recursos")
st.markdown("Controle de uniformes, chuteiras e materiais esportivos da ONG/projeto.")
st.markdown("---")

sb = get_supabase()

membros_resp = sb.table("membros").select("id, nome").eq("ativo", True).order("nome").execute()
membros = membros_resp.data or []
membros_map = {m["nome"]: m["id"] for m in membros}
membros_map_inv = {m["id"]: m["nome"] for m in membros}

TIPOS = ["Uniforme", "Chuteira", "Caneleira", "Bola", "Colete", "Meia", "Shorts", "Outro"]

tab1, tab2, tab3 = st.tabs(["📋 Listar", "➕ Registrar Entrega", "✏️ Editar / Excluir"])

# ── TAB 1: LISTAR ──────────────────────────────────────────
with tab1:
    st.subheader("Recursos Entregues")
    filtro = st.radio("Exibir", ["Todos", "Não devolvidos", "Devolvidos"], horizontal=True)
    query = sb.table("recursos").select("*").order("criado_em", desc=True)
    if filtro == "Não devolvidos":
        query = query.eq("devolvido", False)
    elif filtro == "Devolvidos":
        query = query.eq("devolvido", True)
    dados = query.execute().data or []

    if dados:
        rows = []
        for d in dados:
            rows.append({
                "ID": d["id"],
                "Membro": membros_map_inv.get(d["membro_id"], "—"),
                "Tipo": d["tipo"],
                "Descrição": d["descricao"] or "",
                "Data Entrega": d["data_entrega"],
                "Devolvido": "✅ Sim" if d["devolvido"] else "❌ Não"
            })
        df = pd.DataFrame(rows)
        nao_dev = df[df["Devolvido"] == "❌ Não"].shape[0]
        st.metric("Itens não devolvidos", nao_dev)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum recurso registrado.")

# ── TAB 2: REGISTRAR ───────────────────────────────────────
with tab2:
    st.subheader("Registrar Entrega de Recurso")
    if not membros:
        st.warning("Cadastre membros antes de registrar recursos.")
    else:
        with st.form("form_recurso"):
            membro_sel = st.selectbox("Membro *", list(membros_map.keys()))
            col1, col2 = st.columns(2)
            with col1:
                tipo = st.selectbox("Tipo de recurso *", TIPOS)
            with col2:
                data_e = st.date_input("Data de entrega", value=date.today())
            descricao = st.text_input("Descrição", placeholder="Ex: Chuteira nº 38 preta, Uniforme tamanho M")
            submitted = st.form_submit_button("✅ Registrar Entrega", type="primary")
            if submitted:
                sb.table("recursos").insert({
                    "membro_id": membros_map[membro_sel],
                    "tipo": tipo,
                    "descricao": descricao.strip() or None,
                    "data_entrega": str(data_e),
                    "devolvido": False
                }).execute()
                st.success(f"Recurso **{tipo}** registrado para **{membro_sel}**!")
                st.rerun()

# ── TAB 3: EDITAR / EXCLUIR ────────────────────────────────
with tab3:
    st.subheader("Editar / Marcar como Devolvido / Excluir")
    dados_edit = sb.table("recursos").select("*").order("criado_em", desc=True).limit(60).execute().data or []
    if not dados_edit:
        st.info("Nenhum recurso para editar.")
    else:
        opcoes = {
            f"{d['id']} | {membros_map_inv.get(d['membro_id'], '?')} | {d['tipo']} | {d['data_entrega']}": d["id"]
            for d in dados_edit
        }
        escolha = st.selectbox("Recurso", list(opcoes.keys()))
        rid = opcoes[escolha]
        rec = sb.table("recursos").select("*").eq("id", rid).single().execute().data

        with st.form("form_editar_recurso"):
            tipo_e = st.selectbox("Tipo", TIPOS, index=TIPOS.index(rec["tipo"]) if rec["tipo"] in TIPOS else 0)
            desc_e = st.text_input("Descrição", value=rec["descricao"] or "")
            dev_e = st.checkbox("Devolvido ✅", value=rec["devolvido"])
            col1, col2 = st.columns(2)
            with col1:
                salvar = st.form_submit_button("💾 Salvar", type="primary")
            with col2:
                excluir = st.form_submit_button("🗑️ Excluir", type="secondary")

        if salvar:
            sb.table("recursos").update({"tipo": tipo_e, "descricao": desc_e or None, "devolvido": dev_e}).eq("id", rid).execute()
            st.success("Recurso atualizado!")
            st.rerun()
        if excluir:
            sb.table("recursos").delete().eq("id", rid).execute()
            st.warning("Registro excluído.")
            st.rerun()
