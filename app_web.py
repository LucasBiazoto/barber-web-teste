import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# CONFIGURAÇÃO DE TELA
st.set_page_config(page_title="Barber Agendamento", page_icon="💈", layout="centered")

# CSS para botões grandes e fáceis de clicar no celular
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
    /* Estilo para o botão de Continuar (Verde) */
    .stFormSubmitButton > button {
        background-color: #28a745 !important;
        width: 100%;
        height: 3.5em;
        color: white !important;
        font-weight: bold;
        border-radius: 12px;
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
    except: return None

service = conectar()

st.title("💈 Sistema de Agendamento")

# --- PASSO 1: FORMULÁRIO DE IDENTIFICAÇÃO ---
# O 'st.form' remove o "Press Enter to apply" automaticamente
with st.form("identificacao_cliente"):
    st.write("### 👋 Dados de Acesso")
    nome = st.text_input("Seu Nome ou Apelido")
    celular = st.text_input("Celular com DDD (apenas números)")
    
    # Botão de submissão do formulário
    avancar = st.form_submit_button("CONTINUAR PARA AGENDAMENTO")

# --- PASSO 2: EXIBIÇÃO DOS HORÁRIOS ---
# O conteúdo abaixo só aparece após clicar no botão acima
if avancar:
    if len(celular) >= 10 and nome:
        st.session_state.pode_agendar = True
        st.session_state.nome_cliente = nome
        st.session_state.cel_cliente = celular
    else:
        st.error("Por favor, preencha o nome e o celular corretamente.")

# Se os dados foram validados, mostra as opções
if st.session_state.get('pode_agendar'):
    st.markdown("---")
    st.success(f"Olá {st.session_state.nome_cliente}! Escolha os detalhes abaixo:")
    
    prof = st.selectbox("Escolha o Profissional", list(AGENDAS.keys()))
    data_sel = st.date_input("Escolha a Data", min_value=datetime.now() + timedelta(days=1))
    
    dias_pt = {"Monday": "Segunda-feira", "Tuesday": "Terça-feira", "Wednesday": "Quarta-feira", 
               "Thursday": "Quinta-feira", "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"}
    st.write(f"Dia selecionado: **{dias_pt.get(data_sel.strftime('%A'))}**")

    st.write("### 🕒 Escolha o Horário:")
    horarios = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    cols = st.columns(3)
    
    for i, hora in enumerate(horarios):
        with cols[i % 3]:
            if st.button(hora, key=f"btn_{hora}"):
                st.balloons()
                st.success(f"✅ Agendado para {st.session_state.nome_cliente} às {hora}!")
