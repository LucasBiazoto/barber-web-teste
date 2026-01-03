import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 1. CONFIGURAÇÃO E ESTILO (MOBILE FIRST)
st.set_page_config(page_title="Barber Agendamento", page_icon="💈", layout="centered")

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
        font-weight: bold;
        height: 3.5em;
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CONFIGURAÇÕES GOOGLE
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

# 3. INTERFACE E LÓGICA DE ESTADO
st.title("💈 Sistema de Agendamento")

# Inicializa variáveis de controle
if 'liberado' not in st.session_state:
    st.session_state.liberado = False
if 'nome_cl' not in st.session_state:
    st.session_state.nome_cl = ""

# PASSO 1: IDENTIFICAÇÃO
if not st.session_state.liberado:
    with st.form("dados_cliente"):
        st.write("### 👋 Passo 1: Identificação")
        nome = st.text_input("Seu Nome")
        celular = st.text_input("Celular (apenas números)")
        btn_continuar = st.form_submit_button("CLIQUE AQUI PARA CONTINUAR")
        
        if btn_continuar:
            if len(celular) >= 10 and nome:
                st.session_state.liberado = True
                st.session_state.nome_cl = nome
                st.rerun() # Força a atualização para mostrar o Passo 2
            else:
                st.error("Preencha nome e celular corretamente!")

# PASSO 2: HORÁRIOS (SÓ APARECE APÓS O CONTINUAR)
else:
    st.write(f"### 🕒 Passo 2: Escolha o Horário, {st.session_state.nome_cl}")
    
    barbeiro = st.selectbox("Selecione o Profissional", list(AGENDAS.keys()))
    data_sel = st.date_input("Escolha o Dia", min_value=datetime.now() + timedelta(days=1))
    
    st.write("---")
    st.write("### Selecione uma hora:")
    
    horas = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    cols = st.columns(3)
    
    for i, h in enumerate(horas):
        with cols[i % 3]:
            if st.button(h, key=f"h_{h}"):
                # MENSAGEM DE SUCESSO
                st.balloons()
                st.success(f"✅ Agendado com sucesso!")
                st.write(f"**Cliente:** {st.session_state.nome_cl}")
                st.write(f"**Profissional:** {barbeiro}")
                st.write(f"**Data:** {data_sel.strftime('%d/%m/%Y')} às {h}")
                
                # Botão para novo agendamento
                if st.button("Fazer novo agendamento"):
                    st.session_state.liberado = False
                    st.rerun()
