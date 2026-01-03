import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Barber Agendamento", page_icon="💈", layout="centered")

# CSS PARA BOTÕES GRANDES (MOBILE FRIENDLY)
st.markdown("""
<style>
div.stButton > button:first-child {
    width: 100%;
    height: 3.5em;
    font-size: 18px;
    font-weight: bold;
    border-radius: 12px;
    background-color: #007bff;
    color: white;
}
.stFormSubmitButton > button {
    background-color: #28a745 !important;
    color: white !important;
    width: 100%;
    height: 3.5em;
    font-size: 18px;
    font-weight: bold;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# CONFIGURAÇÕES GOOGLE CALENDAR
FILE_KEY = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]
AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

def conectar_google():
    try:
        creds = service_account.Credentials.from_service_account_file(FILE_KEY, scopes=SCOPES)
        return build('calendar', 'v3', credentials=creds)
    except: return None

service = conectar_google()

st.title("💈 Sistema de Agendamento")

# --- PASSO 1: FORMULÁRIO COM BOTÃO CONTINUAR ---
# O 'st.form' faz aparecer o botão e tira o "Press Enter to apply"
with st.form("perfil_cliente"):
    st.write("### 👋 Informe seus dados")
    nome = st.text_input("Seu Nome ou Apelido")
    celular = st.text_input("Celular com DDD (apenas números)")
    
    # Botão que você solicitou
    btn_continuar = st.form_submit_button("CONTINUAR PARA HORÁRIOS")

# --- PASSO 2: EXIBIÇÃO DA AGENDA ---
if btn_continuar or st.session_state.get('pode_mostrar'):
    if len(celular) >= 10 and nome:
        st.session_state.pode_mostrar = True
        st.session_state.nome_cl = nome
        
        st.markdown("---")
        st.success(f"Olá {st.session_state.nome_cl}! Escolha abaixo:")
        
        prof = st.selectbox("Escolha o Profissional", list(AGENDAS.keys()))
        data_sel = st.date_input("Escolha a Data", min_value=datetime.now() + timedelta(days=1))
        
        # Grade de botões de horários (3 por linha)
        st.write("### 🕒 Horários Disponíveis")
        horarios = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
        cols = st.columns(3)
        
        for i, hora in enumerate(horarios):
            with cols[i % 3]:
                if st.button(hora, key=f"hora_{hora}"):
                    st.balloons()
                    st.success(f"✅ Reservado para {st.session_state.nome_cl} às {hora}!")
                    st.info(f"Barbeiro: {prof} | Data: {data_sel.strftime('%d/%m')}")
    else:
        st.error("Por favor, preencha o nome e o celular corretamente.")
