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

MESES = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
         "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

def date_selectors(label, key_prefix, default: date = None):
    """Renderiza seletores de Dia / Mês / Ano e retorna um objeto date ou None."""
    if default is None:
        default = date.today()
    st.markdown(f"**{label}**")
    c1, c2, c3 = st.columns(3)
    with c1:
        dia = st.selectbox("Dia", list(range(1, 32)),
                           index=default.day - 1,
                           key=f"{key_prefix}_dia")
    with c2:
        mes = st.selectbox("Mês", MESES,
                           index=default.month - 1,
                           key=f"{key_prefix}_mes")
    with c3:
        ano_atual = default.year
        anos = list(range(ano_atual - 126, ano_atual + 3))
        ano = st.selectbox("Ano", anos,
                           index=anos.index(ano_atual) if ano_atual in anos else 0,
                           key=f"{key_prefix}_ano")
    try:
        return date(ano, MESES.index(mes) + 1, dia)
    except ValueError:
        st.error("Data inválida. Verifique dia/mês/ano.")
        return None

tab1, tab2, tab3 = st.tabs(["📋 Listar / Relatório", "➕ Registrar Presença", "✏️ Editar / Excluir"])

# ── TAB 1: LISTAR ──────────────────────────────────────────
with tab1:
    st.subheader("Relatório de Presenças")
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_grupo = st.selectbox("Grupo", ["Todos"] + list(grupos_map.keys()), key="f_grupo")

    hoje = date.today()
    primeiro_dia_mes = hoje.replace(day=1)

    data_ini = date_selectors("De", key_prefix="f_ini", default=primeiro_dia_mes)
    data_fim = date_selectors("Até", key_prefix="f_fim", default=hoje)

    if data_ini and data_fim:
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
        grupo_sel = st.selectbox("Grupo *", list(grupos_map.keys()), key="reg_grupo")
        data_atv = date_selectors("Data da atividade *", key_prefix="reg_atv")

        if data_atv:
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
                    sb.table("presencas").delete() \
                      .eq("grupo_id", gid).eq("data_atividade", str(data_atv)).execute()
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

        presente_e = st.checkbox("Presente", value=reg["presente"], key="edit_presente")
        obs_e = st.text_input("Observação", value=reg["observacao"] or "", key="edit_obs")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Salvar", type="primary", key="btn_salvar_p"):
                sb.table("presencas").update({
                    "presente": presente_e,
                    "observacao": obs_e or None
                }).eq("id", pid).execute()
                st.success("Registro atualizado!")
                st.rerun()
        with col2:
            if st.button("🗑️ Excluir", type="secondary", key="btn_excluir_p"):
                sb.table("presencas").delete().eq("id", pid).execute()
                st.warning("Registro excluído.")
                st.rerun()
