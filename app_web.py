import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configurações de Serviços e Agendas
SERVICOS = {
    "Corte": 45,
    "Corte e Barba": 60,
    "Corte e Luzes": 60,
    "Só Barba": 30,
    "Corte Feminino": 60
}

AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

st.set_page_config(page_title="Barber Agendamento", page_icon="💈")

def conectar():
    try:
        # Recupera a chave dos Secrets e remove espaços ou aspas extras
        if "private_key" not in st.secrets:
            st.error("Erro: 'private_key' não encontrada nos Secrets.")
            return None
            
        key_content = st.secrets["private_key"].strip().strip('"').strip("'")
        # Converte a string de quebra de linha literal \n em quebras reais
        key_content = key_content.replace('\\n', '\n')
        
        info = {
            "type": "service_account",
            "project_id": "winter-anchor-458412-u7",
            "private_key_id": "defe96a8614801119a264b0a9f94a9a609520534",
            "private_key": key_content,
            "client_email": "bot-salao@winter-anchor-458412-u7.iam.gserviceaccount.com",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        
        creds = service_account.Credentials.from_service_account_info(
            info, 
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Erro na conexão com Google: {e}")
        return None

service = conectar()

st.title("💈 Barber Agendamento")

# Interface Principal
tab1, tab2 = st.tabs(["📅 Novo Horário", "🔍 Meus Horários"])

with tab1:
    nome = st.text_input("Seu Nome")
    celular = st.text_input("Celular")
    
    col1, col2 = st.columns(2)
    with col1:
        prof = st.selectbox("Barbeiro", list(AGENDAS.keys()))
    with col2:
        servico = st.selectbox("Serviço", list(SERVICOS.keys()))
        
    data_sel = st.date_input("Escolha a Data", min_value=datetime.now().date())
    
    st.write("---")
    st.write("### Horários Disponíveis:")
    horas = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    cols = st.columns(3)
    
    for i, h in enumerate(horas):
        with cols[i % 3]:
            if st.button(h, key=f"btn_{h}"):
                if not nome or not celular:
                    st.warning("Preencha seu nome e celular antes de escolher o horário.")
                elif service:
                    try:
                        inicio = datetime.strptime(f"{data_sel} {h}", "%Y-%m-%d %H:%M")
                        fim = inicio + timedelta(minutes=SERVICOS[servico])
                        
                        evento = {
                            'summary': f"{servico}: {nome}",
                            'description': f"Contato: {celular}",
                            'start': {'dateTime': inicio.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
                            'end': {'dateTime': fim.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
                        }
                        
                        service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
                        st.success(f"✅ Agendado para {h}!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Erro ao salvar na agenda: {e}")

with tab2:
    st.info("Funcionalidade de consulta em desenvolvimento.")
