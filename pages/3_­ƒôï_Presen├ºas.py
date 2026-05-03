import streamlit as st
import pandas as pd
from datetime import date
from database import get_supabase
from auth import require_auth

st.set_page_config(page_title="Presenças", page_icon="📋", layout="wide")

require_auth()
st.title("📋 Controle de Presenças")
st.markdown("---")

sb = get_supabase()

grupos_resp = sb.table("grupos").select("id, nome").eq("ativo", True).order("nome").execute()
grupos = grupos_resp.data or []
grupos_map = {g["nome"]: g["id"] for g in grupos}
grupos_map_inv = {g["id"]: g["nome"] for g in grupos}

tab1, tab2, tab3 = st.tabs(["📋 Listar / Relatório", "➕ Registrar Presença", "✏️ Editar / Excluir"])

# ── TAB 1: LISTAR ──────────────────────────────────────────
with tab1:
    st.subheader("Relatório de Presenças")
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_grupo = st.selectbox("Grupo", ["Todos"] + list(grupos_map.keys()), key="f_grupo")
    with col2:
        data_ini = st.date_input("De", value=date.today().replace(day=1))
    with col3:
        data_fim = st.date_input("Até", value=date.today())

    query = sb.table("presencas").select("*, membros(nome), grupos(nome)") \
              .gte("data_atividade", str(data_ini)).lte("data_atividade", str(data_fim)) \
              .order("data_atividade", desc=True)
    if filtro_grupo != "Todos":
        query = query.eq("grupo_id", grupos_map[filtro_grupo])

    dados = query.execute().data or []
    if dados:
        rows = []
        for d in dados:
            rows.append({
                "ID": d["id"],
                "Membro": d["membros"]["nome"] if d["membros"] else "—",
                "Grupo": d["grupos"]["nome"] if d["grupos"] else "—",
                "Data": d["data_atividade"],
                "Presente": "✅" if d["presente"] else "❌",
                "Observação": d["observacao"] or ""
            })
        df = pd.DataFrame(rows)
        presentes = df[df["Presente"] == "✅"].shape[0]
        total = len(df)
        st.metric("Taxa de Presença", f"{presentes}/{total} ({int(presentes/total*100) if total else 0}%)")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum registro encontrado para o período selecionado.")

# ── TAB 2: REGISTRAR ───────────────────────────────────────
with tab2:
    st.subheader("Registrar Presença em Lote (por grupo/dia)")
    if not grupos:
        st.warning("Cadastre grupos antes de registrar presenças.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            grupo_sel = st.selectbox("Grupo *", list(grupos_map.keys()), key="reg_grupo")
        with col2:
            data_atv = st.date_input("Data da atividade *", value=date.today())

        gid = grupos_map[grupo_sel]
        membros_resp = sb.table("membros").select("id, nome").eq("grupo_id", gid).eq("ativo", True).order("nome").execute()
        membros = membros_resp.data or []

        if not membros:
            st.info("Nenhum membro ativo neste grupo.")
        else:
            st.markdown("**Marque os presentes:**")
            presencas_registrar = {}
            for m in membros:
                presencas_registrar[m["id"]] = st.checkbox(m["nome"], value=True, key=f"p_{m['id']}")

            obs_geral = st.text_input("Observação geral (opcional)")
            if st.button("✅ Salvar Presenças", type="primary"):
                # Remove registros duplicados do mesmo dia/grupo se existirem
                sb.table("presencas").delete() \
                  .eq("grupo_id", gid).eq("data_atividade", str(data_atv)).execute()
                # Insere novos
                inserts = [
                    {"membro_id": mid, "grupo_id": gid,
                     "data_atividade": str(data_atv),
                     "presente": presente,
                     "observacao": obs_geral or None}
                    for mid, presente in presencas_registrar.items()
                ]
                sb.table("presencas").insert(inserts).execute()
                st.success(f"Presenças do dia {data_atv} salvas com sucesso!")
                st.rerun()

# ── TAB 3: EDITAR / EXCLUIR ────────────────────────────────
with tab3:
    st.subheader("Editar ou Excluir Registro")
    dados_edit = sb.table("presencas").select("id, data_atividade, presente, membros(nome)") \
                   .order("data_atividade", desc=True).limit(50).execute().data or []
    if not dados_edit:
        st.info("Nenhum registro para editar.")
    else:
        opcoes = {f"{d['id']} | {d['membros']['nome'] if d['membros'] else '?'} | {d['data_atividade']}": d["id"]
                  for d in dados_edit}
        escolha = st.selectbox("Registro", list(opcoes.keys()))
        pid = opcoes[escolha]
        reg = sb.table("presencas").select("*").eq("id", pid).single().execute().data

        with st.form("form_editar_presenca"):
            presente_e = st.checkbox("Presente", value=reg["presente"])
            obs_e = st.text_input("Observação", value=reg["observacao"] or "")
            col1, col2 = st.columns(2)
            with col1:
                salvar = st.form_submit_button("💾 Salvar", type="primary")
            with col2:
                excluir = st.form_submit_button("🗑️ Excluir", type="secondary")

        if salvar:
            sb.table("presencas").update({"presente": presente_e, "observacao": obs_e or None}).eq("id", pid).execute()
            st.success("Registro atualizado!")
            st.rerun()
        if excluir:
            sb.table("presencas").delete().eq("id", pid).execute()
            st.warning("Registro excluído.")
            st.rerun()
