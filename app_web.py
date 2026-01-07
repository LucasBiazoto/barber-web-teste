import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# IDs das Agendas - Verifique se os IDs estão corretos nas configurações do Google
AGENDAS = {
    "Bruno": "vários-números@group.calendar.google.com", # USE O ID QUE VOCÊ COPIOU DO GOOGLE
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

st.set_page_config(page_title="Barber Agendamento", page_icon="💈")

def conectar():
    try:
        raw_key = st.secrets["private_key"]
        clean_key = raw_key.replace('\\n', '\n').strip().strip('"')
        info = {
            "type": "service_account",
            "project_id": "winter-anchor-458412-u7",
            "private_key": clean_key,
            "client_email": "bot-salao@winter-anchor-458412-u7.iam.gserviceaccount.com",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        creds = service_account.Credentials.from_service_account_info(info, scopes=['https://www.googleapis.com/auth/calendar'])
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return None

service = conectar()

# --- NOVA FUNÇÃO: BUSCAR HORÁRIOS OCUPADOS ---
def get_ocupados(calendar_id, data):
    try:
        min_time = datetime.combine(data, datetime.min.time()).isoformat() + "Z"
        max_time = datetime.combine(data, datetime.max.time()).isoformat() + "Z"
        
        events_result = service.events().list(
            calendarId=calendar_id, timeMin=min_time, timeMax=max_time,
            singleEvents=True, orderBy='startTime'
        ).execute()
        
        eventos = events_result.get('items', [])
        ocupados = []
        for ev in eventos:
            start = ev['start'].get('dateTime', ev['start'].get('date'))
            # Extrai apenas HH:MM do horário de início
            ocupados.append(start[11:16])
        return ocupados
    except:
        return []

st.title("💈 Barber Agendamento")

nome = st.text_input("Seu Nome")
celular = st.text_input("Celular")
senha = st.text_input("Senha", type="password")

col_p, col_s = st.columns(2)
with col_p:
    prof = st.selectbox("Barbeiro", list(AGENDAS.keys()))
with col_s:
    servico = st.selectbox("Serviço", ["Corte", "Barba", "Corte e Barba"])

data_sel = st.date_input("Data", min_value=datetime.now().date())

# --- LÓGICA DE EXIBIÇÃO DE HORÁRIOS ---
st.write("### Horários Disponíveis:")
todos_horarios = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]

# Busca o que já está agendado no Google para esse barbeiro nesta data
ocupados = get_ocupados(AGENDAS[prof], data_sel)

cols = st.columns(3)
for i, h in enumerate(todos_horarios):
    with cols[i % 3]:
        # Se o horário estiver na lista de ocupados, o botão fica desativado
        if h in ocupados:
            st.button(f"🚫 {h}", key=f"btn_{h}", disabled=True, use_container_width=True)
        else:
            if st.button(h, key=f"btn_{h}", use_container_width=True):
                if nome and celular and senha:
                    try:
                        inicio = datetime.strptime(f"{data_sel} {h}", "%Y-%m-%d %H:%M")
                        fim = inicio + timedelta(minutes=45)
                        
                        evento = {
                            'summary': f"{servico}: {nome}",
                            'description': f"TEL: {celular} | SENHA: {senha}",
                            'start': {'dateTime': inicio.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
                            'end': {'dateTime': fim.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
                        }
                        service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
                        st.success(f"✅ Agendado para {h}!")
                        st.rerun() # Atualiza a tela para sumir o horário agendado
                    except Exception as e:
                        st.error(f"Erro: {e}")
                else:
                    st.warning("Preencha seus dados primeiro!")
