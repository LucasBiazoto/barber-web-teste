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
# ESTILO VISUAL BARBER SHOP (MANTIDO)
# =========================================================
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.65)), 
        url("https://images.unsplash.com/photo-1503951914875-452162b0f3f1?q=80&w=2070");
        background-size: cover;
        background-attachment: fixed;
    }
    .stMarkdown p, label, .stWidgetLabel {
        color: white !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 2px #000;
    }
    div[data-testid="stVerticalBlock"] > div {
        background: rgba(20, 20, 20, 0.5);
        padding: 15px;
        border-radius: 15px;
        max-width: 92%;
        margin: auto;
    }
    h1 { color: #D4AF37 !important; text-align: center; text-shadow: 2px 2px 4px #000; }
    div.stButton > button {
        background-color: #D4AF37 !important;
        color: black !important;
        font-weight: bold;
        border: none;
    }
    #MainMenu, footer, header {visibility: hidden;}
    .footer-custom {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(0, 0, 0, 0.9);
        color: white;
        text-align: center;
        padding: 12px;
        border-top: 1px solid #D4AF37;
        z-index: 999;
    }
    .footer-custom a { color: #D4AF37; text-decoration: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# LÓGICA DE CONEXÃO E BLOQUEIO DE DIA INTEIRO
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
    except: return None

service = conectar()

def get_status_dia(calendar_id, data):
    try:
        # Busca eventos do dia inteiro usando o fuso correto
        min_t = fuso.localize(datetime.combine(data, time.min)).isoformat()
        max_t = fuso.localize(datetime.combine(data, time.max)).isoformat()
        
        events_result = service.events().list(calendarId=calendar_id, timeMin=min_t, timeMax=max_t, singleEvents=True).execute()
        eventos = events_result.get('items', [])
        ocupados = []
        
        for ev in eventos:
            # BLOQUEIO DE DIA INTEIRO (ex: seu evento do dia 13)
            if 'date' in ev['start']:
                return "BLOQUEADO"
            
            # BLOQUEIO DE HORÁRIOS COMUNS
            start_dt = ev['start'].get('dateTime')
            if start_dt:
                hora_formatada = datetime.fromisoformat(start_dt).astimezone(fuso).strftime('%H:%M')
                ocupados.append(hora_formatada)
        return ocupados
    except: return []

# =========================================================
# INTERFACE PRINCIPAL
# =========================================================
st.title("💈 BARBER SHOP PREMIUM")
aba1, aba2 = st.tabs(["📅 AGENDAR", "❌ CANCELAR AGENDAMENTO"])

with aba1:
    nome = st.text_input("Nome completo ou apelido")
    col1, col2 = st.columns(2)
    with col1: celular = st.text_input("Telefone com o DDD")
    with col2: senha = st.text_input("Crie uma senha", type="password")
    
    prof = st.selectbox("Barbeiro", list(AGENDAS.keys()))
    servico = st.selectbox("Serviço", ["Corte", "Barba", "Combo Premium"])
    data_sel = st.date_input("Data", min_value=datetime.now(fuso).date())
    
    status = get_status_dia(AGENDAS[prof], data_sel)
    
    if status == "BLOQUEADO":
        st.error(f"🚫 O barbeiro {prof} está indisponível nesta data (Evento de dia inteiro).")
    else:
        st.write("### 🕒 Horários Disponíveis")
        todos = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
        cols = st.columns(3)
        for i, h in enumerate(todos):
            with cols[i % 3]:
                if h in status:
                    st.button(f"🚫 {h}", disabled=True, key=f"d_{h}", use_container_width=True)
                else:
                    if st.button(h, key=f"b_{h}", use_container_width=True):
                        if nome and celular and senha:
                            try:
                                # FORÇA MINUTO ZERO (Corrige os 6 minutos de diferença)
                                h_int = int(h.split(':')[0])
                                inicio = fuso.localize(datetime.combine(data_sel, time(hour=h_int, minute=0, second=0)))
                                
                                # Verifica duplicidade de última hora
                                status_agora = get_status_dia(AGENDAS[prof], data_sel)
                                if h in status_agora:
                                    st.error("Ops! Alguém acabou de pegar esse horário.")
                                else:
                                    evento = {
                                        'summary': f"{servico}: {nome}",
                                        'description': f"TEL: {celular} | SENHA: {senha}",
                                        'start': {'dateTime': inicio.isoformat()},
                                        'end': {'dateTime': (inicio + timedelta(minutes=45)).isoformat()},
                                    }
                                    service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
                                    st.success(f"✅ Agendado para às {h}!")
                                    st.rerun()
                            except Exception as e: st.error(f"Erro: {e}")
                        else: st.warning("Preencha todos os campos!")

# Rodapé com seu link
st.markdown(f"""<div class="footer-custom">Desenvolvido por Lucas Biazoto | <a href="https://github.com/LBiazoto" target="_blank">GitHub</a></div>""", unsafe_allow_html=True)
