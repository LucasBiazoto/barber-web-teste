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
    /* Deixa o botão de continuar verde para destacar */
    .stFormSubmitButton > button {
        background-color: #28a745 !important;
    }
    </style>
""", unsafe_allow_html=True)

# CONFIGURAÇÕES DE ACESSO (Mantenha suas chaves aqui)
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

# --- PASSO 1: IDENTIFICAÇÃO COM BOTÃO ---
# O formulário impede que o site peça "Enter" o tempo todo
with st.form("meu_formulario"):
    st.write("### 👋 Dados do Cliente")
    nome_input = st.text_input("Seu Nome ou Apelido")
    celular_input = st.text_input("Celular com DDD (apenas números)")
    
    # Este é o botão que você pediu!
    botao_continuar = st.form_submit_button("CLIQUE AQUI PARA CONTINUAR")

# --- PASSO 2: LIBERAÇÃO DOS HORÁRIOS ---
if botao_continuar:
    if len(celular_input) >= 10 and nome_input:
        st.session_state.pode_agendar = True
        st.session_state.nome_final = nome_input
        st.session_state.cel_final = celular_input
    else:
        st.error("Preencha seu nome e celular corretamente primeiro!")

# Se o botão foi clicado com sucesso, mostra o resto
if st.session_state.get('pode_agendar'):
    st.markdown("---")
    st.success(f"Olá {st.session_state.nome_final}! Agora escolha abaixo:")
    
    prof = st.selectbox("Escolha o Profissional", list(AGENDAS.keys()))
    data_sel = st.date_input("Escolha a Data", min_value=datetime.now() + timedelta(days=1))
    
    st.write("### 🕒 Escolha o Horário")
    horarios = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    cols = st.columns(3)
    
    for i, hora in enumerate(horarios):
        with cols[i % 3]:
            if st.button(hora, key=f"btn_{hora}"):
                st.balloons()
                st.success(f"Agendado às {hora}!")
