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

# 2. CONEXÃO GOOGLE (RESOLVE O ERRO DE JWT)
AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

def conectar():
    try:
        with open('credentials.json') as f:
            info = json.load(f)
        # Limpa a chave privada de erros de formatação do GitHub
        info['private_key'] = info['private_key'].replace('\\n', '\n')
        creds = service_account.Credentials.from_service_account_info(info, scopes=['https://www.googleapis.com/auth/calendar'])
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Erro na credencial: {e}")
        return None

service = conectar()

# 3. INTERFACE E SERVIÇOS
st.title("💈 Sistema de Agendamento")

if 'liberado' not in st.session_state: st.session_state.liberado = False

tab1, tab2 = st.tabs(["📅 Novo Horário", "🔍 Meus Horários"])

with tab1:
    if not st.session_state.liberado:
        with st.form("dados_cliente"):
            st.write("### 👋 Passo 1: Identificação")
            nome = st.text_input("Seu Nome")
            celular = st.text_input("Celular (apenas números)")
            senha = st.text_input("Crie uma senha (para cancelar depois)", type="password")
            if st.form_submit_button("CONTINUAR PARA HORÁRIOS"):
                if nome and len(celular) >= 10 and senha:
                    st.session_state.update({"liberado": True, "nome": nome, "cel": celular, "senha": senha})
                    st.rerun()
                else:
                    st.error("Preencha Nome, Celular e Senha!")
    else:
        st.write(f"### Olá {st.session_state.nome}, falta pouco!")
        
        # Seleção de Profissional e Serviço
        col_p, col_s = st.columns(2)
        with col_p:
            prof = st.selectbox("Profissional", list(AGENDAS.keys()))
        with col_s:
            servico = st.selectbox("Serviço", ["Corte", "Barba", "Corte e Barba", "Sobrancelha", "Completo"])
            
        data_sel = st.date_input("Escolha o Dia", min_value=datetime.now() + timedelta(days=1))
        
        st.write("---")
        st.write("### Escolha o Horário:")
        horas = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
        cols = st.columns(3)
        
        for i, h in enumerate(horas):
            with cols[i % 3]:
                if st.button(h, key=f"h_{h}"):
                    data_iso = data_sel.strftime('%Y-%m-%d')
                    detalhes = f"Serviço: {servico} | Tel: {st.session_state.cel} | Senha: {st.session_state.senha}"
                    
                    evento = {
                        'summary': f"{servico}: {st.session_state.nome}",
                        'description': detalhes,
                        'start': {'dateTime': f"{data_iso}T{h}:00-03:00", 'timeZone': 'America/Sao_Paulo'},
                        'end': {'dateTime': f"{data_iso}T{h}:30:00-03:00", 'timeZone': 'America/Sao_Paulo'},
                    }
                    
                    try:
                        # Tenta gravar na agenda correspondente
                        service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
                        st.balloons()
                        st.success(f"✅ Sucesso! {servico} com {prof} às {h}.")
                    except Exception as e:
                        st.error(f"Erro ao salvar: O sistema não conseguiu autenticar. Verifique o arquivo credentials.json.")

with tab2:
    st.write("### 🔍 Consultar Agendamento")
    st.info("Digite seu celular e senha para ver ou cancelar seus horários.")
    # Aqui entrará a lógica de busca por eventos que contenham o celular/senha na descrição
