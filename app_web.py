import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

# 1. CONFIGURAÇÃO E ESTILO
st.set_page_config(page_title="Barber Agendamento", page_icon="💈", layout="centered")

st.markdown("""
    <style>
    div.stButton > button:first-child { width: 100%; height: 3.5em; font-size: 18px; font-weight: bold; border-radius: 12px; background-color: #007bff; color: white; }
    .stFormSubmitButton > button { background-color: #28a745 !important; color: white !important; font-weight: bold; height: 3.5em; border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# 2. CONEXÃO GOOGLE (COM LIMPEZA AUTOMÁTICA DA CHAVE)
AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

def conectar():
    try:
        with open('credentials.json') as f:
            info = json.load(f)
        # CORREÇÃO VITAL: Converte os '\n' de texto para quebras de linha reais
        info['private_key'] = info['private_key'].replace('\\n', '\n')
        creds = service_account.Credentials.from_service_account_info(info, scopes=['https://www.googleapis.com/auth/calendar'])
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Erro Crítico nas Credenciais: {e}")
        return None

service = conectar()

# 3. INTERFACE E LÓGICA DE ESTADO
if 'liberado' not in st.session_state: st.session_state.liberado = False

st.title("💈 Sistema de Agendamento")

# TABS PARA ORGANIZAR
tab1, tab2 = st.tabs(["📅 Novo Horário", "🔍 Meus Horários / Cancelar"])

with tab1:
    if not st.session_state.liberado:
        with st.form("dados_cliente"):
            st.write("### 👋 Passo 1: Identificação")
            nome = st.text_input("Seu Nome ou Apelido")
            celular = st.text_input("Celular (DDD + Número)")
            senha = st.text_input("Crie uma Senha (para cancelar depois)", type="password")
            
            if st.form_submit_button("CONTINUAR PARA HORÁRIOS"):
                if nome and len(celular) >= 10 and senha:
                    st.session_state.update({"liberado": True, "nome": nome, "cel": celular, "senha": senha})
                    st.rerun()
                else:
                    st.error("Preencha todos os campos corretamente!")
    else:
        st.write(f"### Olá {st.session_state.nome}, escolha o horário:")
        prof = st.selectbox("Escolha o Profissional", list(AGENDAS.keys()))
        data_sel = st.date_input("Escolha a Data", min_value=datetime.now() + timedelta(days=1))
        
        st.write("---")
        horas = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
        cols = st.columns(3)
        
        for i, h in enumerate(horas):
            with cols[i % 3]:
                if st.button(h, key=f"h_{h}"):
                    data_iso = data_sel.strftime('%Y-%m-%d')
                    evento = {
                        'summary': f"Corte: {st.session_state.nome}",
                        'description': f"Senha: {st.session_state.senha} | Tel: {st.session_state.cel}",
                        'start': {'dateTime': f"{data_iso}T{h}:00-03:00", 'timeZone': 'America/Sao_Paulo'},
                        'end': {'dateTime': f"{data_iso}T{h}:30:00-03:00", 'timeZone': 'America/Sao_Paulo'},
                    }
                    try:
                        service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
                        st.balloons()
                        st.success(f"✅ Agendado com {prof} às {h} no dia {data_sel.strftime('%d/%m')}!")
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")

with tab2:
    st.write("### 🔍 Consultar ou Cancelar")
    st.info("Esta função busca agendamentos na agenda do Bruno por padrão.")
    cel_busca = st.text_input("Digite seu Celular para buscar")
    senha_busca = st.text_input("Digite sua Senha", type="password")
    
    if st.button("Buscar Agendamentos"):
        st.warning("Busca em desenvolvimento. Verifique seu calendário ou fale com o barbeiro.")
