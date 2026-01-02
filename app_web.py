import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- CONFIGURAÇÕES DE ACESSO ---
FILE_KEY = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']
AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

# Função para conectar e tratar erros de autenticação
def conectar():
    try:
        creds = service_account.Credentials.from_service_account_file(FILE_KEY, scopes=SCOPES)
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Erro ao carregar credenciais: {e}")
        return None

# Função para verificar limite de agendamentos
def buscar_agendamentos(service, celular):
    if not service: return []
    encontrados = []
    agora = datetime.utcnow().isoformat() + 'Z'
    for ag_id in AGENDAS.values():
        try:
            res = service.events().list(calendarId=ag_id, timeMin=agora, q=celular, singleEvents=True).execute()
            encontrados.extend(res.get('items', []))
        except:
            continue
    return encontrados

# --- INTERFACE DO SITE ---
st.set_page_config(page_title="Barber Agendamento", page_icon="💈")
st.title("💈 Sistema de Agendamento")

service = conectar()

tab1, tab2 = st.tabs(["📅 Novo Horário", "🔍 Meus Horários"])

with tab1:
    nome = st.text_input("Seu Nome ou Apelido")
    celular = st.text_input("Celular com DDD (apenas números)")
    
    if celular and len(celular) >= 10:
        meus_horarios = buscar_agendamentos(service, celular)
        
        # Aplicando a trava de segurança
        if len(meus_horarios) >= 2:
            st.error(f"Atenção: Você já possui {len(meus_horarios)} agendamentos ativos. O limite é 2 por cliente.")
        else:
            st.success("Tudo certo! Você pode realizar seu agendamento.")
            prof = st.selectbox("Escolha o Profissional", list(AGENDAS.keys()))
            
            # Escolha de data com calendário
            data_sel = st.date_input("Escolha a Data", min_value=datetime.now() + timedelta(days=1))
            
            # Tradução dos dias
            dias_pt = {
                "Monday": "Segunda-feira", "Tuesday": "Terça-feira", "Wednesday": "Quarta-feira",
                "Thursday": "Quinta-feira", "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"
            }
            st.write(f"Dia selecionado: **{dias_pt[data_sel.strftime('%A')]}**")
            
            if st.button("Finalizar Agendamento"):
                st.balloons()
                st.info(f"Horário solicitado com {prof} para {data_sel.strftime('%d/%m')}! Verifique seu calendário.")

with tab2:
    st.subheader("Consultar Meus Agendamentos")
    cel_cons = st.text_input("Digite seu celular", key="cons")
    if st.button("Buscar"):
        meus = buscar_agendamentos(service, cel_cons)
        if meus:
            for m in meus:
                st.write(f"✅ {m['start'].get('dateTime', m['start'].get('date'))} - {m['summary']}")
        else:
            st.info("Nenhum agendamento encontrado.")
