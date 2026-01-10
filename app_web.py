import streamlit as st
from datetime import datetime, timedelta
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build

# =========================================================
# 1. IDs DAS AGENDAS (CONFORME SEUS PRINTS)
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
        min_t = datetime.combine(data, datetime.min.time()).astimezone(fuso).isoformat()
        max_t = datetime.combine(data, datetime.max.time()).astimezone(fuso).isoformat()
        events_result = service.events().list(calendarId=calendar_id, timeMin=min_t, timeMax=max_t, singleEvents=True).execute()
        # Captura apenas HH:mm para comparar com os botões
        return [ev['start'].get('dateTime', '')[11:16] for ev in events_result.get('items', [])]
    except: return []

# =========================================================
# 3. INTERFACE PRINCIPAL
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
                            # FIX: Criar horário redondo (00 segundos) ignorando o relógio atual
                            data_hora_string = f"{data_sel} {h}"
                            inicio = datetime.strptime(data_hora_string, "%Y-%m-%d %H:%M").replace(tzinfo=fuso)
                            fim = inicio + timedelta(minutes=45)
                            
                            evento = {
                                'summary': f"{servico}: {nome}",
                                'description': f"TEL: {celular} | SENHA: {senha}",
                                'start': {'dateTime': inicio.isoformat(), 'timeZone': 'America/Sao_Paulo'},
                                'end': {'dateTime': fim.isoformat(), 'timeZone': 'America/Sao_Paulo'},
                            }
                            service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
                            st.success(f"✅ Agendado com sucesso para às {h}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao agendar no Google: {e}")
                    else: st.warning("Preencha todos os campos para agendar.")

with aba2:
    st.write("### 🔍 Localizar meu Horário")
    
    # Session state para manter a lista visível após o clique no botão de cancelar
    if "lista_cancelar" not in st.session_state:
        st.session_state.lista_cancelar = []

    c_tel = st.text_input("Celular cadastrado", key="c_tel_in")
    c_senha = st.text_input("Sua senha", type="password", key="c_senha_in")
    c_prof = st.selectbox("Com qual barbeiro?", list(AGENDAS.keys()), key="c_prof_in")

    if st.button("BUSCAR MEUS AGENDAMENTOS"):
        if c_tel and c_senha:
            agora_iso = datetime.now(fuso).isoformat()
            eventos = service.events().list(calendarId=AGENDAS[c_prof], timeMin=agora_iso, singleEvents=True).execute().get('items', [])
            
            # Filtra os agendamentos que batem com Tel e Senha
            st.session_state.lista_cancelar = [
                ev for ev in eventos 
                if f"TEL: {c_tel}" in ev.get('description', '') and f"SENHA: {c_senha}" in ev.get('description', '')
            ]
            
            if not st.session_state.lista_cancelar:
                st.error("Nenhum agendamento futuro encontrado com esses dados.")
        else:
            st.warning("Informe telefone e senha para buscar.")

    # Exibe a lista para cancelamento
    if st.session_state.lista_cancelar:
        st.write(f"--- Encontramos {len(st.session_state.lista_cancelar)} agendamento(s) ---")
        agora_dt = datetime.now(fuso)
        
        for ev in st.session_state.lista_cancelar:
            # Converte o tempo do Google para o fuso local
            ini_str = ev['start']['dateTime']
            ini_dt = datetime.fromisoformat(ini_str.replace('Z', '+00:00')).astimezone(fuso)
            
            st.info(f"📍 {ev['summary']} \n 📅 {ini_dt.strftime('%d/%m/%Y')} às {ini_dt.strftime('%H:%M')}")
            
            # Regra de 1 hora antes
            if agora_dt < (ini_dt - timedelta(hours=1)):
                if st.button(f"CONFIRMAR CANCELAMENTO ({ini_dt.strftime('%H:%M')})", key=f"del_{ev['id']}", type="primary"):
                    try:
                        service.events().delete(calendarId=AGENDAS[c_prof], eventId=ev['id']).execute()
                        st.success("✅ Cancelamento realizado com sucesso!")
                        st.session_state.lista_cancelar = [] # Limpa a memória
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir: {e}")
            else:
                st.error("🚫 Bloqueado: Cancelamento permitido apenas até 1h antes do horário.")
