import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# CONFIGURAÇÃO DE TELA
st.set_page_config(page_title="Barber Agendamento", page_icon="💈", layout="centered")

# CSS para botões grandes (Estilo App Mobile)
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

# CONFIGURAÇÕES DE ACESSO
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
    except:
        return None

service = conectar()

st.title("💈 Agendamento Barber")

# Entrada de dados do cliente
nome = st.text_input("Seu Nome ou Apelido")
celular = st.text_input("Celular com DDD (apenas números)")

if celular and len(celular) >= 10:
    st.markdown("---")
    
    # Seleção de Profissional e Data
    prof = st.selectbox("Escolha o Profissional", list(AGENDAS.keys()))
    data_sel = st.date_input("Escolha a Data", min_value=datetime.now() + timedelta(days=1))
    
    dias_pt = {
        "Monday": "Segunda-feira", "Tuesday": "Terça-feira", "Wednesday": "Quarta-feira", 
        "Thursday": "Quinta-feira", "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"
    }
    dia_nome = dias_pt.get(data_sel.strftime('%A'), data_sel.strftime('%A'))
    st.write(f"Dia selecionado: **{dia_nome}**")

    st.write("### 🕒 Escolha o Horário:")
    
    # Grade de horários 3x3 para facilitar no celular
    horarios = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    cols = st.columns(3)
    
    for i, hora in enumerate(horarios):
        with cols[i % 3]:
            # O segredo é o 'key' ser único para cada botão
            if st.button(hora, key=f"btn_{hora}"):
                st.success(f"✅ Horário Reservado!")
                st.balloons()
                st.info(f"Confirmado: {nome} com {prof} às {hora} do dia {data_sel.strftime('%d/%m')}.")
