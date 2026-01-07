import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# IDs das Agendas
AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

st.set_page_config(page_title="Barber Agendamento", page_icon="💈")

def conectar():
    try:
        # Puxa a chave dos Secrets de forma segura
        raw_key = st.secrets["private_key"]
        clean_key = raw_key.replace('\\n', '\n').strip().strip('"')
        
        info = {
            "type": "service_account",
            "project_id": "winter-anchor-458412-u7",
            "private_key": clean_key,
            "client_email": "bot-salao@winter-anchor-458412-u7.iam.gserviceaccount.com",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=['https://www.googleapis.com/auth/calendar']
        )
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return None

service = conectar()

st.title("💈 Barber Agendamento")

# Campos de entrada
nome = st.text_input("Seu Nome")
celular = st.text_input("Celular")
senha = st.text_input("Senha", type="password")

col1, col2 = st.columns(2)
with col1:
    prof = st.selectbox("Barbeiro", list(AGENDAS.keys()))
with col2:
    servico = st.selectbox("Serviço", ["Corte", "Barba", "Corte e Barba"])

data_sel = st.date_input("Escolha a Data", min_value=datetime.now().date())
h_sel = st.selectbox("Horário", ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"])

if st.button("CONFIRMAR AGENDAMENTO"):
    if nome and celular and senha and service:
        try:
            inicio = datetime.strptime(f"{data_sel} {h_sel}", "%Y-%m-%d %H:%M")
            fim = inicio + timedelta(minutes=45)
            
            evento = {
                'summary': f"{servico}: {nome}",
                'description': f"TEL: {celular} | SENHA: {senha}",
                'start': {'dateTime': inicio.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
                'end': {'dateTime': fim.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
            }
            
            service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
            st.success("✅ Agendado com sucesso!")
            st.balloons()
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")
    else:
        st.warning("Preencha todos os campos.")
