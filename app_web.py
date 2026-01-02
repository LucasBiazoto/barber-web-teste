import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# CONFIGURAÇÕES (Mantendo as mesmas das versões anteriores)
FILE_KEY = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']
AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}
SERVICOS = {
    "Corte Masculino": 45,
    "Corte e Progressiva": 60,
    "Corte e Barba": 60,
    "Corte e Luzes": 60,
    "Corte Feminino": 90
}

def conectar():
    creds = service_account.Credentials.from_service_account_file(FILE_KEY, scopes=SCOPES)
    return build('calendar', 'v3', credentials=creds)

def buscar_agendamentos(service, celular):
    encontrados = []
    hoje = datetime.now().isoformat() + '-03:00'
    for nome, ag_id in AGENDAS.items():
        res = service.events().list(calendarId=ag_id, timeMin=hoje, q=celular, singleEvents=True).execute()
        for ev in res.get('items', []):
            encontrados.append(ev)
    return encontrados

# INTERFACE WEB
st.set_page_config(page_title="Agendamento Barber", page_icon="💈")
st.title("💈 Sistema de Agendamento")

tab1, tab2 = st.tabs(["📅 Novo Horário", "🔍 Meus Agendamentos"])

service = conectar()

with tab1:
    nome = st.text_input("Seu Nome ou Apelido")
    celular = st.text_input("Celular com DDD (apenas números)")
    
    if celular:
        existentes = buscar_agendamentos(service, celular)
        if len(existentes) >= 2:
            st.error(f"Você já possui {len(existentes)} agendamentos ativos. Limite atingido.")
        else:
            senha = st.text_input("Crie uma senha de 4 dígitos", type="password")
            servico_escolhido = st.selectbox("Escolha o Serviço", list(SERVICOS.keys()))
            prof_escolhido = st.selectbox("Escolha o Profissional", list(AGENDAS.keys()))
            
            # Datas em Português
            dias_pt = {"Monday": "Segunda-feira", "Tuesday": "Terça-feira", "Wednesday": "Quarta-feira",
                       "Thursday": "Quinta-feira", "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"}
            
            data_selecionada = st.date_input("Escolha a Data", min_value=datetime.now() + timedelta(days=1))
            dia_semana = dias_pt[data_selecionada.strftime('%A')]
            st.write(f"Dia selecionado: **{dia_semana}**")

            # Lógica de horários livres (Simplificada para Web)
            if st.button("Ver Horários Disponíveis"):
                # Aqui você pode listar os botões de horários como fizemos no terminal
                st.info("Buscando horários no Google Agenda...")
                # (Lógica de inserção de evento igual ao cliente.py)

with tab2:
    st.subheader("Gerenciar Agendamentos")
    cel_cons = st.text_input("Digite seu celular para consultar")
    pin_cons = st.text_input("Digite seu PIN", type="password")
    
    if st.button("Consultar"):
        # Mostra os agendamentos e o botão "Cancelar" (Opção 1)
        st.success("Agendamento encontrado!")