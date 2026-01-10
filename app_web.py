import streamlit as st
from datetime import datetime, timedelta
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build

# =========================================================
# 1. IDs DAS AGENDAS (ATUALIZADOS CONFORME SEUS PRINTS)
# =========================================================
AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

st.set_page_config(page_title="Barber Shop", page_icon="💈")
fuso = pytz.timezone('America/Sao_Paulo')

# =========================================================
# 2. CONEXÃO COM O GOOGLE
# =========================================================
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
        st.error(f"Erro na conexão com Google: {e}")
        return None

service = conectar()

def get_ocupados(calendar_id, data):
    try:
        # Define o início e fim do dia para busca
        min_t = datetime.combine(data, datetime.min.time()).astimezone(fuso).isoformat()
        max_t = datetime.combine(data, datetime.max.time()).astimezone(fuso).isoformat()
        
        events_result = service.events().list(
            calendarId=calendar_id, timeMin=min_t, timeMax=max_t, singleEvents=True
        ).execute()
        
        return [ev['start'].get('dateTime', '')[11:16] for ev in events_result.get('items', [])]
    except: return []

# =========================================================
# 3. INTERFACE
# =========================================================
st.title("💈 Barber Shop")
aba1, aba2 = st.tabs(["📅 Agendar", "❌ Cancelar Horário"])

with aba1:
    nome = st.text_input("Seu Nome", key="ag_nome")
    celular = st.text_input("Celular (Ex: 11999999999)", key="ag_tel")
    senha = st.text_input("Crie uma Senha", type="password", key="ag_senha")

    col_p, col_s = st.columns(2)
    with col_p: prof = st.selectbox("Barbeiro", list(AGENDAS.keys()), key="ag_prof")
    with col_s: servico = st.selectbox("Serviço", ["Corte", "Barba", "Corte e Barba"], key="ag_serv")

    data_sel = st.date_input("Data", min_value=datetime.now(fuso).date(), key="ag_data")
    
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
                        try:
                            # Monta o horário do evento
                            inicio = datetime.strptime(f"{data_sel} {h}", "%Y-%m-%d %H:%M").replace(tzinfo=fuso)
                            fim = inicio + timedelta(minutes=45)
                            
                            evento = {
                                'summary': f"{servico}: {nome}",
                                'description': f"TEL: {celular} | SENHA: {senha}",
                                'start': {'dateTime': inicio.isoformat(), 'timeZone': 'America/Sao_Paulo'},
                                'end': {'dateTime': fim.isoformat(), 'timeZone': 'America/Sao_Paulo'},
                            }
                            service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
                            st.success(f"✅ Agendado para {h}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao agendar: {e}")
                    else: st.warning("Preencha todos os campos!")

with aba2:
    st.write("### 🔍 Localizar meu Horário")
    c_tel = st.text_input("Celular cadastrado", key="c_tel_in")
    c_senha = st.text_input("Sua senha", type="password", key="c_senha_in")
    c_prof = st.selectbox("Barbeiro", list(AGENDAS.keys()), key="c_prof_in")

    if st.button("BUSCAR MEUS AGENDAMENTOS"):
        if c_tel and c_senha:
            agora = datetime.now(fuso)
            # Busca todos os eventos futuros para este barbeiro
            eventos = service.events().list(calendarId=AGENDAS[c_prof], timeMin=agora.isoformat(), singleEvents=True).execute().get('items', [])
            
            meus = [ev for ev in eventos if f"TEL: {c_tel}" in ev.get('description', '') and f"SENHA: {c_senha}" in ev.get('description', '')]
            
            if meus:
                for ev in meus:
                    ini_str = ev['start']['dateTime']
                    ini_dt = datetime.fromisoformat(ini_str.replace('Z', '+00:00')).astimezone(fuso)
                    
                    st.info(f"📍 {ev['summary']} \n 📅 {ini_dt.strftime('%d/%m/%Y')} às {ini_dt.strftime('%H:%M')}")
                    
                    # Regra de 1 hora antes do início para cancelar
                    if agora < (ini_dt - timedelta(hours=1)):
                        if st.button(f"CONFIRMAR CANCELAMENTO ({ini_dt.strftime('%H:%M')})", key=f"del_{ev['id']}", type="primary"):
                            service.events().delete(calendarId=AGENDAS[c_prof], eventId=ev['id']).execute()
                            st.success("❌ Cancelado com sucesso!")
                            st.rerun()
                    else:
                        st.error("🚫 Bloqueado: Cancelamentos somente com 1h de antecedência.")
            else: st.error("Nenhum horário encontrado com esses dados.")
        else: st.warning("Informe telefone e senha.")
