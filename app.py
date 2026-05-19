import streamlit as st
from auth import require_auth

st.set_page_config(
    page_title="Gestão Esportiva Social",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

require_auth()

st.title("⚽ Sistema de Gestão de Projetos Esportivos Sociais")
st.markdown("---")

st.markdown("""
### Bem-vindo ao sistema!

Este sistema foi desenvolvido como **atividade de extensão universitária** (UNIASSELVI),
com foco em inclusão social por meio do esporte.

Utilize o **menu lateral** para navegar entre os módulos:

| Módulo | Descrição |
|--------|-----------|
| 👥 **Grupos** | Cadastro e gestão de turmas |
| 🙋 **Membros** | Cadastro de participantes e jovens |
| 📋 **Presenças** | Controle de frequência nas atividades |
| 🎽 **Recursos** | Gestão de uniformes e materiais esportivos |
| 🏆 **Eventos** | Organização de festivais e atividades comunitárias |

---
**Modelo 3C de Colaboração:** *Comunicação · Cooperação · Coordenação*
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.info("💡 **Comunicação**\nConecta membros e coordenadores por meio de registros compartilhados.")
with col2:
    st.success("🤝 **Cooperação**\nGestão coletiva de recursos e presença para maior engajamento.")
with col3:
    st.warning("📅 **Coordenação**\nOrganização de horários, eventos e atividades da comunidade.")
