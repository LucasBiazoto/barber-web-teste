import streamlit as st
from datetime import datetime, timedelta, time
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configurações de Agenda
AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

DURACOES = {
    "Corte": 30,
    "Corte e Barba": 60,
    "Corte e Luzes": 60,
    "Barba": 30,
    "Corte Feminino": 90
}

st.set_page_config(page_title="Barber Shop Premium", page_icon="💈", layout="wide")
fuso = pytz.timezone('America/Sao_Paulo')

# =========================================================
# DESIGN RESPONSIVO (ADAPTAÇÃO AUTOMÁTICA)
# =========================================================
st.markdown("""
    <style>
    /* Fundo Adaptável */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
        url("https://images.unsplash.com/photo-1503951914875-452162b0f3f1?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }

    /* Container Centralizado e Flexível */
    [data-testid="stVerticalBlock"] > div:has(input, select, .stButton) { 
        background: rgba(15, 15, 15, 0.95); 
        border: 2px solid #D4AF37;
        border-radius: 15px; 
        padding: 5% !important;
        margin: auto;
        max-width: 800px; /* Limita largura em TVs e PCs */
    }

    /* Ajuste de Texto para todas as telas */
    h1 { color: #D4AF37 !important; text-align: center; font-size: calc(1.8rem + 1.5vw) !important; }
    h2, h3, h4 { color: white !important; text-align: center; }

    /* Botões Grandes e Touch-Friendly (Celular) */
    div.stButton > button { 
        background-color: #D4AF37 !important; 
        color: black !important; 
        font-weight: bold; 
        min-height: 60px;
        font-size: 1.1rem !important;
        border-radius: 12px;
        border: none;
        margin-bottom: 10px;
    }

    /* Botão Vermelho de Cancelar */
    div.stButton > button[key^="del_"] { background-color: #cc0000 !important; color: white !important; }
    
    /* Mensagem de Confirmação Verde (Destaque) */
    .stSuccess {
        background-color: #28a745 !important;
        color: white !important;
        font-size: 1.2rem;
        text-align: center;
        border-radius: 10px;
        padding: 20px;
    }

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
        min_t = fuso.localize(datetime.combine(data, time.min)).isoformat()
        max_t = fuso.localize(datetime.combine(data, time.max)).isoformat()
        events = service.events().list(calendarId=calendar_id, timeMin=min_t, timeMax=max_t, singleEvents=True).execute().get('items', [])
        ocupados = []
        for ev in events:
            if 'date' in ev['start']: return "BLOQUEADO"
            start_dt = ev['start'].get('dateTime')
            if start_dt:
                ocupados.append(datetime.fromisoformat(start_dt).astimezone(fuso).strftime('%H:%M'))
        return ocupados
    except: return []

# Inicialização de Estados
if 'pagina' not in st.session_state: st.session_state.pagina = 'inicio'
if 'confirmado' not in st.session_state: st.session_state.confirmado = False

# --- TELA DE SUCESSO ---
if st.session_state.confirmado:
    st.title("💈 AGENDAMENTO REALIZADO!")
    st.success("✨ Seu horário foi confirmado na agenda do barbeiro com sucesso!")
    if st.button("FAZER OUTRO AGENDAMENTO / VOLTAR"):
        st.session_state.confirmado = False
        st.session_state.pagina = 'inicio'
        st.rerun()
    st.stop()

# --- TELA INICIAL ---
st.title("💈 BARBER SHOP PREMIUM")

if st.session_state.pagina == 'inicio':
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("📅 AGENDAR NOVO HORÁRIO", use_container_width=True):
            st.session_state.pagina = 'agendar'
            st.rerun()
    with col2:
        if st.button("❌ CANCELAR AGENDAMENTO", use_container_width=True):
            st.session_state.pagina = 'cancelar'
            st.rerun()

# --- FORMULÁRIO AGENDAMENTO ---
elif st.session_state.pagina == 'agendar':
    if st.button("⬅ VOLTAR"): st.session_state.pagina = 'inicio'; st.rerun()
    
    nome = st.text_input("Nome ou apelido")
    colA, colB = st.columns(2)
    with colA: zap = st.text_input("Telefone com o DDD")
    with colB: senha = st.text_input("Crie uma senha", type="password")
    
    prof = st.selectbox("Escolha o Barbeiro", list(AGENDAS.keys()))
    serv_nome = st.selectbox("Selecione o Serviço", list(DURACOES.keys()))
    data_sel = st.date_input("Escolha a Data", min_value=datetime.now(fuso).date())
    
    status = get_status_dia(AGENDAS[prof], data_sel)
    
    if status == "BLOQUEADO":
        st.error("🚫 O barbeiro não atenderá nesta data.")
    else:
        st.write("#### 🕒 Horários Disponíveis")
        todos = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
        # Grid responsiva: 3 colunas no PC, mas Streamlit ajusta no Celular
        cols = st.columns(3)
        for i, h in enumerate(todos):
            with cols[i%3]:
                if h in status: st.button(f"🚫 {h}", disabled=True, key=f"o_{h}")
                else:
                    if st.button(h, key=f"l_{h}", use_container_width=True):
                        if nome and zap and senha:
                            minutos = DURACOES[serv_nome]
                            inicio = fuso.localize(datetime.combine(data_sel, time(int(h.split(':')[0]), 0)))
                            fim = inicio + timedelta(minutes=minutos)
                            corpo = {
                                'summary': f"{serv_nome}: {nome}",
                                'description': f"TEL: {zap} | SENHA: {senha}",
                                'start': {'dateTime': inicio.isoformat()},
                                'end': {'dateTime': fim.isoformat()}
                            }
                            service.events().insert(calendarId=AGENDAS[prof], body=corpo).execute()
                            st.session_state.confirmado = True
                            st.rerun()
                        else: st.warning("Preencha todos os campos!")

# --- FORMULÁRIO CANCELAMENTO ---
elif st.session_state.pagina == 'cancelar':
    if st.button("⬅ VOLTAR"): st.session_state.pagina = 'inicio'; st.rerun()
    
    c_zap = st.text_input("Telefone com o DDD", key="czap")
    c_senha = st.text_input("Senha cadastrada", type="password", key="csenha")
    c_barb = st.selectbox("Barbeiro", list(AGENDAS.keys()))
    
    if st.button("🔍 BUSCAR MEU HORÁRIO"):
        agora = datetime.now(fuso).isoformat()
        evs = service.events().list(calendarId=AGENDAS[c_barb], timeMin=agora, singleEvents=True).execute().get('items', [])
        st.session_state.meus_evs = [e for e in evs if f"TEL: {c_zap}" in e.get('description','') and f"SENHA: {c_senha}" in e.get('description','')]
        if not st.session_state.meus_evs: st.error("Nenhum agendamento encontrado.")

    if 'meus_evs' in st.session_state:
        for ev in st.session_state.meus_evs:
            h_ev = datetime.fromisoformat(ev['start']['dateTime']).astimezone(fuso).strftime('%d/%m às %H:%M')
            st.warning(f"Reserva: {h_ev}")
            if st.button(f"CANCELAR AGENDAMENTO", key=f"del_{ev['id']}"):
                service.events().delete(calendarId=AGENDAS[c_barb], eventId=ev['id']).execute()
                st.session_state.meus_evs = []
                st.success("🗑️ AGENDAMENTO CANCELADO!")
                st.session_state.pagina = 'inicio'
                st.rerun()

st.markdown(f"""<div style="position:fixed; bottom:0; left:0; width:100%; text-align:center; background:rgba(0,0,0,0.9); padding:10px; border-top:1px solid #D4AF37; color:#D4AF37; font-size:12px;">BARBER SHOP PREMIUM © 2026 | Lucas Biazoto</div>""", unsafe_allow_html=True)
