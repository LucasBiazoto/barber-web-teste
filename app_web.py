import streamlit as st
from datetime import datetime, timedelta
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build

# =========================================================
# 1. CONFIGURAÇÕES E IDs
# =========================================================
AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

st.set_page_config(page_title="Barber Shop Premium", page_icon="💈", layout="centered")
fuso = pytz.timezone('America/Sao_Paulo')

# =========================================================
# 2. ESTILO VISUAL (IMAGEM DE FUNDO E TEXTO BRANCO)
# =========================================================
st.markdown("""
    <style>
    /* Imagem de fundo e escurecimento */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
        url("https://images.unsplash.com/photo-1503951914875-452162b0f3f1?q=80&w=2070");
        background-size: cover;
        background-attachment: fixed;
    }

    /* Forçar labels (Nomes dos campos) para Branco */
    .stMarkdown p, label, .stWidgetLabel {
        color: white !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }

    /* Container dos inputs com transparência elegante */
    div[data-testid="stVerticalBlock"] > div {
        background: rgba(30, 30, 30, 0.5);
        padding: 10px;
        border-radius: 10px;
    }

    /* Título Dourado */
    h1 { color: #D4AF37 !important; text-shadow: 2px 2px 4px #000; }
    
    /* Botões */
    div.stButton > button {
        background-color: #D4AF37 !important;
        color: black !important;
        font-weight: bold;
        border: none;
        width: 100%;
    }
    
    /* Abas */
    .stTabs [data-baseweb="tab"] { color: white !important; }
    .stTabs [aria-selected="true"] { border-bottom-color: #D4AF37 !important; }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. CONEXÃO E LÓGICA
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
        st.error(f"Erro: {e}")
        return None

service = conectar()

def get_ocupados(calendar_id, data):
    try:
        min_t = datetime.combine(data, datetime.min.time()).astimezone(fuso).isoformat()
        max_t = datetime.combine(data, datetime.max.time()).astimezone(fuso).isoformat()
        events_result = service.events().list(calendarId=calendar_id, timeMin=min_t, timeMax=max_t, singleEvents=True).execute()
        return [ev['start'].get('dateTime', '')[11:16] for ev in events_result.get('items', [])]
    except: return []

# =========================================================
# 4. INTERFACE
# =========================================================
st.title("💈 BARBER SHOP PREMIUM")
aba1, aba2 = st.tabs(["📅 AGENDAR", "❌ CANCELAR"])

with aba1:
    # Textos alterados conforme solicitado
    nome = st.text_input("Nome completo ou apelido")
    col1, col2 = st.columns(2)
    with col1: celular = st.text_input("Telefone com o DDD")
    with col2: senha = st.text_input("Crie uma senha", type="password")
    
    col3, col4 = st.columns(2)
    with col3: prof = st.selectbox("Barbeiro", list(AGENDAS.keys()))
    with col4: servico = st.selectbox("Serviço", ["Corte", "Barba", "Combo Premium"])
    
    data_sel = st.date_input("Data do agendamento", min_value=datetime.now(fuso).date())
    
    st.write("### 🕒 Horários Disponíveis")
    todos = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    ocupados = get_ocupados(AGENDAS[prof], data_sel)
    cols = st.columns(3)

    for i, h in enumerate(todos):
        with cols[i % 3]:
            if h in ocupados:
                st.button(f"🚫 {h}", disabled=True, key=f"d_{h}")
            else:
                if st.button(h, key=f"b_{h}"):
                    if nome and celular and senha:
                        try:
                            data_hora_string = f"{data_sel} {h}"
                            inicio = datetime.strptime(data_hora_string, "%Y-%m-%d %H:%M").replace(tzinfo=fuso)
                            evento = {
                                'summary': f"{servico}: {nome}",
                                'description': f"TEL: {celular} | SENHA: {senha}",
                                'start': {'dateTime': inicio.isoformat(), 'timeZone': 'America/Sao_Paulo'},
                                'end': {'dateTime': (inicio + timedelta(minutes=45)).isoformat(), 'timeZone': 'America/Sao_Paulo'},
                            }
                            service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
                            st.success(f"✅ Agendado para às {h}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
                    else: st.warning("Preencha todos os campos!")

with aba2:
    st.write("### 🔍 Localizar para Cancelar")
    if "lista_cancelar" not in st.session_state: st.session_state.lista_cancelar = []
    
    c_tel = st.text_input("Telefone com DDD cadastrado", key="c_tel_in")
    c_senha = st.text_input("Senha cadastrada", type="password", key="c_senha_in")
    c_prof = st.selectbox("Barbeiro agendado", list(AGENDAS.keys()), key="c_prof_in")

    if st.button("BUSCAR HORÁRIO"):
        agora = datetime.now(fuso).isoformat()
        eventos = service.events().list(calendarId=AGENDAS[c_prof], timeMin=agora, singleEvents=True).execute().get('items', [])
        st.session_state.lista_cancelar = [ev for ev in eventos if f"TEL: {c_tel}" in ev.get('description', '') and f"SENHA: {c_senha}" in ev.get('description', '')]
    
    if st.session_state.lista_cancelar:
        for ev in st.session_state.lista_cancelar:
            ini_dt = datetime.fromisoformat(ev['start']['dateTime'].replace('Z', '+00:00')).astimezone(fuso)
            st.info(f"📅 {ini_dt.strftime('%d/%m/%Y')} às {ini_dt.strftime('%H:%M')}")
            if st.button(f"CONFIRMAR CANCELAMENTO", key=f"del_{ev['id']}", type="primary"):
                service.events().delete(calendarId=AGENDAS[c_prof], eventId=ev['id']).execute()
                st.session_state.lista_cancelar = []
                st.rerun()
