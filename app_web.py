import streamlit as st
from datetime import datetime, timedelta, time
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build

# IDs das Agendas
AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

st.set_page_config(page_title="Barber Shop Premium", page_icon="💈", layout="centered")
fuso = pytz.timezone('America/Sao_Paulo')

# =========================================================
# ESTILO VISUAL (CORES: CANCELAR AMARELO / SUCESSO VERDE)
# =========================================================
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.65)), 
        url("https://images.unsplash.com/photo-1503951914875-452162b0f3f1?q=80&w=2070");
        background-size: cover;
        background-attachment: fixed;
    }
    .stMarkdown p, label, .stWidgetLabel { color: white !important; font-weight: bold !important; }
    div[data-testid="stVerticalBlock"] > div { background: rgba(20, 20, 20, 0.6); border-radius: 15px; padding: 20px; }
    
    /* Títulos e Botões Dourados/Amarelos */
    h1 { color: #D4AF37 !important; text-align: center; }
    div.stButton > button { background-color: #D4AF37 !important; color: black !important; font-weight: bold; border: none; width: 100%; }
    
    /* Mensagem de Sucesso VERDE */
    div[data-testid="stNotification"] { background-color: #28a745 !important; color: white !important; }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def conectar():
    try:
        info = {
            "type": "service_account",
            "project_id": "winter-anchor-458412-u7",
            "private_key": st.secrets["private_key"].replace('\\n', '\n').strip().strip('"'),
            "client_email": "bot-salao@winter-anchor-458412-u7.iam.gserviceaccount.com",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        return build('calendar', 'v3', credentials=service_account.Credentials.from_service_account_info(info, scopes=['https://www.googleapis.com/auth/calendar']))
    except: return None

service = conectar()

def get_status_dia(calendar_id, data):
    try:
        # Busca eventos do dia selecionado
        min_t = fuso.localize(datetime.combine(data, time.min)).isoformat()
        max_t = fuso.localize(datetime.combine(data, time.max)).isoformat()
        events = service.events().list(calendarId=calendar_id, timeMin=min_t, timeMax=max_t, singleEvents=True).execute().get('items', [])
        
        ocupados = []
        for ev in events:
            # BLOQUEIO DEFINITIVO DIA INTEIRO (Campo 'date' sem hora)
            if 'date' in ev['start']:
                return "BLOQUEADO"
            # BLOQUEIO DE HORÁRIOS
            start_dt = ev['start'].get('dateTime')
            if start_dt:
                ocupados.append(datetime.fromisoformat(start_dt).astimezone(fuso).strftime('%H:%M'))
        return ocupados
    except: return []

st.title("💈 BARBER SHOP PREMIUM")
aba1, aba2 = st.tabs(["📅 AGENDAR", "❌ CANCELAR AGENDAMENTO"])

with aba1:
    nome = st.text_input("Seu Nome")
    col1, col2 = st.columns(2)
    with col1: zap = st.text_input("WhatsApp")
    with col2: senha = st.text_input("Senha", type="password")
    
    barbeiro = st.selectbox("Escolha o Barbeiro", list(AGENDAS.keys()))
    data_sel = st.date_input("Data", min_value=datetime.now(fuso).date())
    
    status = get_status_dia(AGENDAS[barbeiro], data_sel)
    
    if status == "BLOQUEADO":
        st.error("🚫 Este barbeiro não atenderá nesta data (Evento de dia inteiro).")
    else:
        st.write("### Horários")
        todos = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
        cols = st.columns(3)
        for i, h in enumerate(todos):
            with cols[i%3]:
                if h in status: st.button(f"🚫 {h}", disabled=True, key=f"o_{h}")
                else:
                    if st.button(h, key=f"l_{h}"):
                        if nome and zap and senha:
                            h_i = int(h.split(':')[0])
                            inicio = fuso.localize(datetime.combine(data_sel, time(h_i, 0)))
                            corpo = {
                                'summary': f"Corte: {nome}",
                                'description': f"TEL: {zap} | SENHA: {senha}",
                                'start': {'dateTime': inicio.isoformat()},
                                'end': {'dateTime': (inicio + timedelta(minutes=45)).isoformat()}
                            }
                            service.events().insert(calendarId=AGENDAS[barbeiro], body=corpo).execute()
                            st.success("✅ AGENDADO COM SUCESSO!") # Aparecerá em VERDE
                            st.rerun()

with aba2:
    st.write("### ❌ Cancelar Horário")
    c_zap = st.text_input("WhatsApp cadastrado")
    c_senha = st.text_input("Senha cadastrada", type="password")
    c_barb = st.selectbox("Barbeiro do agendamento", list(AGENDAS.keys()), key="c_b")
    
    if st.button("BUSCAR MEU HORÁRIO", key="btn_cancel"):
        agora = datetime.now(fuso).isoformat()
        evs = service.events().list(calendarId=AGENDAS[c_barb], timeMin=agora, singleEvents=True).execute().get('items', [])
        # Filtro rigoroso para achar o evento certo
        meus = [e for e in evs if f"TEL: {c_zap}" in e.get('description','') and f"SENHA: {c_senha}" in e.get('description','')]
        
        if meus:
            for ev in meus:
                h_ev = datetime.fromisoformat(ev['start']['dateTime']).astimezone(fuso).strftime('%d/%m às %H:%M')
                st.warning(f"Encontrado: {h_ev}")
                if st.button(f"CONFIRMAR CANCELAMENTO", key=ev['id']):
                    service.events().delete(calendarId=AGENDAS[c_barb], eventId=ev['id']).execute()
                    st.success("CANCELADO COM SUCESSO!")
                    st.rerun() # ESSENCIAL: Recarrega a página e limpa a agenda
        else:
            st.error("Nenhum agendamento encontrado.")
