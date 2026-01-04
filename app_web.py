import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configurações de Agenda
AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

st.set_page_config(page_title="Barber Agendamento", page_icon="💈")

def conectar():
    try:
        # Puxa a chave do painel Secrets do Streamlit
        raw_key = st.secrets["private_key"]
        # Limpa possíveis erros de escape de caracteres
        clean_key = raw_key.replace('\\n', '\n').strip()
        
        info = {
            "type": "service_account",
            "project_id": "winter-anchor-458412-u7",
            "private_key_id": "defe96a8614801119a264b0a9f94a9a609520534",
            "private_key": clean_key,
            "client_email": "bot-salao@winter-anchor-458412-u7.iam.gserviceaccount.com",
            "client_id": "111589643947434085108",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        creds = service_account.Credentials.from_service_account_info(info, scopes=['https://www.googleapis.com/auth/calendar'])
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Erro na autenticação: {e}")
        return None

service = conectar()

st.title("💈 Agendamento Online")

# Interface simplificada para teste
nome = st.text_input("Seu Nome")
prof = st.selectbox("Barbeiro", list(AGENDAS.keys()))
data_sel = st.date_input("Data", min_value=datetime.now().date() + timedelta(days=1))
hora_sel = st.selectbox("Horário", ["09:00", "10:00", "11:00", "14:00", "15:00", "17:00"])

if st.button("CONFIRMAR AGENDAMENTO"):
    if nome and service:
        inicio = datetime.strptime(f"{data_sel} {hora_sel}", "%Y-%m-%d %H:%M")
        fim = inicio + timedelta(minutes=45)
        
        evento = {
            'summary': f"Corte: {nome}",
            'start': {'dateTime': inicio.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
            'end': {'dateTime': fim.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
        }
        
        try:
            service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
            st.success(f"✅ Feito! Horário marcado com {prof}.")
            st.balloons()
        except Exception as e:
            st.error(f"Erro ao salvar na agenda: {e}")
