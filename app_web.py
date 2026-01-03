import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Barber Agendamento",
    page_icon="💈",
    layout="centered"
)

# CSS – Botões grandes (mobile friendly)
st.markdown("""
<style>
div.stButton > button:first-child {
    width: 100%;
    height: 3.5em;
    font-size: 18px;
    font-weight: bold;
    border-radius: 12px;
}

.stFormSubmitButton > button {
    background-color: #28a745 !important;
    color: white !important;
    width: 100%;
    height: 3.5em;
    font-size: 18px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# GOOGLE CALENDAR
FILE_KEY = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

def conectar():
    try:
        creds = service_account.Credentials.from_service_account_file(
            FILE_KEY, scopes=SCOPES
        )
        return build('calendar', 'v3', credentials=creds)
    except:
        return None

service = conectar()

# TÍTULO
st.title("💈 Sistema de Agendamento")

# ===============================
# PASSO 1 — FORMULÁRIO
# ===============================
with st.form("dados_cliente"):
    st.subheader("👋 Identificação")
    
    nome = st.text_input("Seu Nome ou Apelido")
    celular = st.text_input("Celular com DDD (apenas números)")
    
    continuar = st.form_submit_button("CONTINUAR")

# ===============================
# VALIDAÇÃO
# ===============================
if continuar:
    if nome.strip() and celular.isdigit() and len(celular) >= 10:
        st.session_state["nome"] = nome
        st.session_state["celular"] = celular
        st.session_state["liberado"] = True
    else:
        st.error("Preencha o nome e um celular válido com DDD.")

# ===============================
# PASSO 2 — AGENDAMENTO
# ===============================
if st.session_state.get("liberado"):
    st.markdown("---")
    st.success(f"Olá, {st.session_state['nome']} 👋")

    profissional = st.selectbox("Escolha o profissional", list(AGENDAS.keys()))
    data = st.date_input(
        "Escolha a data",
        min_value=datetime.now().date() + timedelta(days=1)
    )

    st.write("### 🕒 Escolha o horário")
    horarios = [
        "09:00", "10:00", "11:00",
        "13:00", "14:00", "15:00",
        "16:00", "17:00", "18:00"
    ]

    cols = st.columns(3)
    for i, hora in enumerate(horarios):
        with cols[i % 3]:
            if st.button(hora):
                st.success(
                    f"✅ Agendamento confirmado!\n\n"
                    f"📅 {data.strftime('%d/%m/%Y')} às {hora}\n"
                    f"✂️ {profissional}"
                )
