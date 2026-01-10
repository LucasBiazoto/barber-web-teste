import streamlit as st
from datetime import datetime, timedelta
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build

# IDs das Agendas - MANTENHA OS SEUS IDs CORRETOS AQUI
AGENDAS = {
    "Bruno": "COLE_SEU_ID_DO_BRUNO_AQUI", 
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

st.set_page_config(page_title="Barber Shop", page_icon="💈")

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
fuso = pytz.timezone('America/Sao_Paulo')

def get_ocupados(calendar_id, data):
    try:
        min_time = datetime.combine(data, datetime.min.time()).isoformat() + "Z"
        max_time = datetime.combine(data, datetime.max.time()).isoformat() + "Z"
        events_result = service.events().list(calendarId=calendar_id, timeMin=min_time, timeMax=max_time, singleEvents=True).execute()
        return [ev['start'].get('dateTime', '')[11:16] for ev in events_result.get('items', [])]
    except: return []

st.title("💈 Barber Shop")
aba1, aba2 = st.tabs(["📅 Agendar", "❌ Cancelar Horário"])

with aba1:
    nome = st.text_input("Seu Nome", key="ag_nome")
    celular = st.text_input("Celular (Ex: 11999999999)", key="ag_tel")
    senha = st.text_input("Crie uma Senha", type="password", key="ag_senha")

    col_p, col_s = st.columns(2)
    with col_p: prof = st.selectbox("Barbeiro", list(AGENDAS.keys()), key="ag_prof")
    with col_s: servico = st.selectbox("Serviço", ["Corte", "Barba", "Corte e Barba"], key="ag_serv")

    data_sel = st.date_input("Data", min_value=datetime.now().date(), key="ag_data")
    
    st.write("### Horários Disponíveis:")
    todos = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    ocupados = get_ocupados(AGENDAS[prof], data_sel)
    cols = st.columns(3)

    for i, h in enumerate(todos):
        with cols[i % 3]:
            if h in ocupados:
                st.button(f"🚫 {h}", disabled=True, use_container_width=True, key=f"d_{h}")
            else:
                if st.button(h, use_container_width=True, key=f"b_{h}"):
                    if nome and celular and senha:
                        inicio = datetime.strptime(f"{data_sel} {h}", "%Y-%m-%d %H:%M")
                        evento = {
                            'summary': f"{servico}: {nome}",
                            'description': f"TEL: {celular} | SENHA: {senha}",
                            'start': {'dateTime': inicio.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
                            'end': {'dateTime': (inicio + timedelta(minutes=45)).strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
                        }
                        service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
                        st.success(f"✅ Agendado para {h}!")
                        st.rerun()
                    else: st.warning("Preencha todos os campos!")

with aba2:
    st.write("### ❌ Cancelar meu Horário")
    c_tel = st.text_input("Celular cadastrado", key="c_tel_input")
    c_senha = st.text_input("Sua senha", type="password", key="c_senha_input")
    c_prof = st.selectbox("Com qual barbeiro?", list(AGENDAS.keys()), key="c_prof_input")

    if st.button("BUSCAR MEU AGENDAMENTO"):
        if c_tel and c_senha:
            # Busca eventos futuros (a partir de hoje)
            hoje = datetime.now(fuso).isoformat()
            eventos = service.events().list(calendarId=AGENDAS[c_prof], timeMin=hoje, singleEvents=True).execute().get('items', [])
            
            encontrados = []
            for ev in eventos:
                desc = ev.get('description', '')
                if f"TEL: {c_tel}" in desc and f"SENHA: {c_senha}" in desc:
                    encontrados.append(ev)
            
            if encontrados:
                st.write(f"--- Encontramos {len(encontrados)} agendamento(s) ---")
                agora = datetime.now(fuso)
                
                for ev in encontrados:
                    inicio_str = ev['start']['dateTime']
                    # Converter string do Google para objeto datetime real
                    inicio_dt = datetime.fromisoformat(inicio_str.replace('Z', '+00:00')).astimezone(fuso)
                    
                    data_formatada = inicio_dt.strftime('%d/%m/%Y')
                    hora_formatada = inicio_dt.strftime('%H:%M')
                    
                    st.info(f"📍 {ev['summary']} \n 📅 Data: {data_formatada} às {hora_formatada}")
                    
                    # Lógica de 1 hora antes
                    limite_cancelamento = inicio_dt - timedelta(hours=1)
                    
                    if agora < limite_cancelamento:
                        if st.button(f"CONFIRMAR CANCELAMENTO ({hora_formatada})", key=f"del_{ev['id']}", type="primary"):
                            service.events().delete(calendarId=AGENDAS[c_prof], eventId=ev['id']).execute()
                            st.success("❌ Cancelado com sucesso!")
                            st.rerun()
                    else:
                        st.error(f"⚠️ O horário das {hora_formatada} não pode mais ser cancelado pelo site (limite de 1h antes). Entre em contato com a barbearia.")
            else:
                st.error("Nenhum agendamento encontrado com esses dados.")
        else:
            st.warning("Preencha telefone e senha.")
