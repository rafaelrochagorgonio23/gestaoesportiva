# ⚽ Sistema de Gestão de Projetos Esportivos Sociais

Projeto desenvolvido como **atividade de extensão universitária** (UNIASSELVI - Inteligência Artificial e Machine Learning).

Fundamentado no **Modelo 3C de Colaboração** (Comunicação, Cooperação, Coordenação), este sistema permite
que ONGs e projetos sociais que utilizam o futebol como ferramenta de inclusão gerenciem suas atividades de forma colaborativa.

---

## 📦 Tecnologias

- **Frontend/Backend:** [Streamlit](https://streamlit.io/)
- **Banco de dados:** [Supabase](https://supabase.com/) (PostgreSQL)
- **Linguagem:** Python 3.10+

---

## 🚀 Configuração Passo a Passo

### 1. Criar projeto no Supabase

1. Acesse [https://supabase.com](https://supabase.com) e crie uma conta gratuita
2. Crie um **novo projeto**
3. Vá em **SQL Editor** e cole o conteúdo do arquivo `schema.sql` e execute
4. Vá em **Project Settings > API** e copie:
   - `Project URL` → será seu `SUPABASE_URL`
   - `anon public` key → será seu `SUPABASE_KEY`

### 2. Configurar credenciais locais

Crie um arquivo `.env` na raiz do projeto (copie de `.env.example`):

```
SUPABASE_URL=https://xxxxxxxxxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=seu-anon-key-aqui
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Rodar o projeto

```bash
streamlit run app.py
```

O sistema abrirá automaticamente em `http://localhost:8501`

---

## 🗂️ Estrutura do Projeto

```
gestao_esportiva_social/
├── app.py                    # Página inicial
├── database.py               # Conexão com Supabase
├── schema.sql                # Script SQL para criar as tabelas
├── requirements.txt          # Dependências Python
├── .env.example              # Modelo de configuração
├── .streamlit/
│   └── config.toml           # Tema visual
└── pages/
    ├── 1_👥_Grupos.py        # CRUD de Grupos/Turmas
    ├── 2_🙋_Membros.py       # CRUD de Membros/Participantes
    ├── 3_📋_Presenças.py     # CRUD de Controle de Presença
    ├── 4_🎽_Recursos.py      # CRUD de Recursos (uniformes, etc.)
    └── 5_🏆_Eventos.py       # CRUD de Eventos/Festivais
```

---

## ✅ Funcionalidades (CRUD completo)

| Módulo | Create | Read | Update | Delete |
|--------|--------|------|--------|--------|
| Grupos | ✅ | ✅ | ✅ | ✅ |
| Membros | ✅ | ✅ | ✅ | ✅ |
| Presenças | ✅ | ✅ | ✅ | ✅ |
| Recursos | ✅ | ✅ | ✅ | ✅ |
| Eventos | ✅ | ✅ | ✅ | ✅ |

---

## 🌐 Deploy gratuito no Streamlit Cloud (opcional)

1. Suba o projeto para um repositório no GitHub
2. Acesse [https://share.streamlit.io](https://share.streamlit.io)
3. Conecte seu repositório
4. Em **Secrets**, adicione suas variáveis:
   ```toml
   SUPABASE_URL = "https://..."
   SUPABASE_KEY = "..."
   ```

---

## 📚 Referencial teórico aplicado

- **Modelo 3C de Colaboração** (Fuks et al., 2005): As funcionalidades do sistema foram organizadas nos três pilares — Comunicação (registro de membros/contatos), Cooperação (gestão compartilhada de recursos e presenças) e Coordenação (organização de horários e eventos).
- **Material Design** e **Heurísticas de Nielsen**: Interface limpa, feedback imediato ao usuário, prevenção de erros com validações.
- **WCAG**: Uso de linguagem clara, contraste adequado e navegação consistente.

---

*Rafael Rocha Gorgonio — UNIASSELVI — Atividade de Extensão 207h*
