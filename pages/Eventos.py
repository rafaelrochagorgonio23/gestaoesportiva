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
        anos = list(range(ano_atual - 126, ano_atual + 11))
        ano = st.selectbox("Ano", anos,
                           index=anos.index(ano_atual) if ano_atual in anos else 0,
                           key=f"{key_prefix}_ano")
    try:
        return date(ano, MESES.index(mes) + 1, dia)
    except ValueError:
        st.error("Data inválida. Verifique dia/mês/ano.")
        return None

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
    nome = st.text_input("Nome do evento *", placeholder="Ex: Festival de Futebol Comunitário")
    descricao = st.text_area("Descrição", placeholder="Detalhes do evento, objetivo, atividades...")
    data_ev = date_selectors("Data do evento *", key_prefix="criar_ev")
    local = st.text_input("Local", placeholder="Ex: Ginásio Municipal")
    grupo_sel = st.selectbox("Grupo organizador", ["— Nenhum —"] + list(grupos_map.keys()))

    if st.button("✅ Criar Evento", type="primary"):
        if not nome.strip():
            st.error("O nome do evento é obrigatório.")
        elif data_ev is None:
            st.error("Informe uma data válida.")
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

        nome_e = st.text_input("Nome *", value=ev["nome"], key="edit_nome")
        desc_e = st.text_area("Descrição", value=ev["descricao"] or "", key="edit_desc")
        default_data = pd.to_datetime(ev["data_evento"]).date()
        data_e = date_selectors("Data", key_prefix="edit_ev", default=default_data)
        local_e = st.text_input("Local", value=ev["local"] or "", key="edit_local")
        grupo_opcoes = ["— Nenhum —"] + list(grupos_map.keys())
        grupo_atual = grupos_map_inv.get(ev["grupo_id"], "— Nenhum —")
        idx = grupo_opcoes.index(grupo_atual) if grupo_atual in grupo_opcoes else 0
        grupo_e = st.selectbox("Grupo", grupo_opcoes, index=idx, key="edit_grupo")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Salvar", type="primary", key="btn_salvar"):
                if data_e:
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
        with col2:
            if st.button("🗑️ Excluir", type="secondary", key="btn_excluir"):
                sb.table("eventos").delete().eq("id", eid).execute()
                st.warning("Evento excluído.")
                st.rerun()
