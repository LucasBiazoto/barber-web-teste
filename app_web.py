import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# CONFIGURAÇÃO PARA DISPOSITIVOS MÓVEIS
st.set_page_config(page_title="Barber Agendamento", page_icon="💈", layout="centered")

# CSS para botões grandes e fáceis de clicar
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
    </style>
""", unsafe_allow_html=True)

FILE_KEY = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']
AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

def conectar():
    try:
        creds = service_account.Credentials.from_service_account_file(FILE_KEY, scopes=SCOPES)
        return build('calendar', 'v3', credentials=creds)
    except: return None

service = conectar()

st.title("💈 Agendamento Barber")

nome = st.text_input("Seu Nome")
celular = st.text_input("Celular (DDD + Número)")

if celular and len(celular) >= 10:
    st.write("---")
    prof = st.selectbox("Selecione o Barbeiro", list(AGENDAS.keys()))
    data_sel = st.date_input("Escolha a Data", min_value=datetime.now() + timedelta(days=1))
    
    # Tradução para Português
    dias_pt = {"Monday": "Segunda-feira", "Tuesday": "Terça-feira", "Wednesday": "Quarta-feira", 
               "Thursday": "Quinta-feira", "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"}
    st.write(f"Dia selecionado: **{dias_pt[data_sel.strftime('%A')]}**")

    st.write("### 🕒 Escolha o Horário:")
    
    # LISTA DE HORÁRIOS - Criando a grade de 3 colunas para Mobile
    horarios = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    cols = st.columns(3)
    
    for i, hora in enumerate(horarios):
        with cols[i % 3]:
            if st.button(hora, key=hora):
                # Mensagem de sucesso ao clicar no horário
                st.success(f"✅ Agendado! {nome} com {prof} às {hora} do dia {data_sel.strftime('%d/%m')}")
                st.balloons()
