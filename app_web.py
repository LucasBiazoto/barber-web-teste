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

# Duração oculta (apenas para a lógica da agenda)
DURACOES = {
    "Corte": 30,
    "Corte e Barba": 60,
    "Corte e Luzes": 60,
    "Barba": 30,
    "Corte Feminino": 90
}

st.set_page_config(page_title="Barber Shop Premium", page_icon="💈", layout="centered")
fuso = pytz.timezone('America/Sao_Paulo')

# =========================================================
# ESTILO VISUAL (BOTÕES DE CARTÃO E QUADRO)
# =========================================================
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), 
        url("https://images.unsplash.com/photo-1503951914875-452162b0f3f1?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }
    .stMarkdown p, label, .stWidgetLabel { color: white !important; font-weight: bold !important; text-shadow: 1px 1px 2px #000; }
    
    /* Quadro Principal */
    div[data-testid="stVerticalBlock"] > div:has(input, select, .stButton) { 
        background: rgba(15, 15, 15, 0.9); 
        border: 2px solid #D4AF37;
        border-radius: 20px; 
        padding: 30px; 
    }
    
    h1 { color: #D4AF37 !important; text-align: center; font-size: 2.8em; letter-spacing: 2px; }

    /* Estilo dos Botões Iniciais (Menu Principal) */
    .menu-btn {
        display: block;
        width: 100%;
        padding: 40px 20px;
        margin: 10px 0;
        text-align: center;
        background: rgba(212, 175, 55, 0.1);
        border: 2px solid #D4AF37;
        color: #D4AF37;
        font-size: 24px;
        font-weight: bold;
        border-radius: 15px;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    /* Botão Dourado de Ação */
    div.stButton > button { 
        background-color: #D4AF37 !important; 
        color: black !important; 
        font-weight: bold; 
        height: 55px;
        border-radius: 12px;
        font-size: 18px;
        border: none;
    }

    /* Botão VERMELHO de Cancelar Agendamento */
    div.stButton > button[key^="del_"] { 
        background-color: #cc0000 !important; 
        color: white !important;
        border: 2px solid white;
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

if 'pagina' not in st.session_state:
    st.session_state.pagina = 'inicio'

st.title("💈 BARBER SHOP PREMIUM")

# --- MENU INICIAL ---
if st.session_state.pagina == 'inicio':
    st.write("## Escolha uma opção:")
    if st.button("📅 AGENDAR NOVO HORÁRIO", key="btn_ir_agendar"):
        st.session_state.pagina = 'agendar'
        st.rerun()
    
    st.write("") # Espaçamento
    
    if st.button("❌ CANCELAR AGENDAMENTO", key="btn_ir_cancelar"):
        st.session_state.pagina = 'cancelar'
        st.rerun()

# --- FORMULÁRIO DE AGENDAMENTO ---
elif st.session_state.pagina == 'agendar':
    if st.button("⬅ VOLTAR AO MENU", key="voltar"):
        st.session_state.pagina = 'inicio'
        st.rerun()

    st.write("### 📅 NOVO AGENDAMENTO")
    nome = st.text_input("Nome ou apelido")
    col1, col2 = st.columns(2)
    with col1: zap = st.text_input("Telefone com o DDD")
    with col2: senha = st.text_input("Crie uma senha", type="password")
    
    prof = st.selectbox("Escolha o Barbeiro", list(AGENDAS.keys()))
    # Nomes dos serviços limpos (sem minutos no texto)
    serv_nome = st.selectbox("Selecione o Serviço", list(DURACOES.keys()))
    data_sel = st.date_input("Escolha a Data", min_value=datetime.now(fuso).date())
    
    status = get_status_dia(AGENDAS[prof], data_sel)
    
    if status == "BLOQUEADO":
        st.error("🚫 O barbeiro não atenderá nesta data.")
    else:
        st.write("#### 🕒 Horários Disponíveis")
        todos = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
        cols = st.columns(3)
        for i, h in enumerate(todos):
            with cols[i%3]:
                if h in status: st.button(f"🚫 {h}", disabled=True, key=f"o_{h}")
                else:
                    if st.button(h, key=f"l_{h}"):
                        if nome and zap and senha:
                            # Aqui o sistema usa os minutos corretos nos bastidores
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
                            st.success(f"✅ Reservado: {h}!")
                            st.session_state.pagina = 'inicio'
                            st.rerun()
                        else: st.warning("Preencha todos os campos!")

# --- FORMULÁRIO DE CANCELAMENTO ---
elif st.session_state.pagina == 'cancelar':
    if st.button("⬅ VOLTAR AO MENU", key="voltar"):
        st.session_state.pagina = 'inicio'
        st.rerun()

    st.write("### ❌ CANCELAR AGENDAMENTO")
    c_zap = st.text_input("Telefone com o DDD", key="czap")
    c_senha = st.text_input("Senha cadastrada", type="password", key="csenha")
    c_barb = st.selectbox("Barbeiro do agendamento", list(AGENDAS.keys()), key="cbarb")
    
    if 'eventos_encontrados' not in st.session_state:
        st.session_state.eventos_encontrados = []

    if st.button("🔍 BUSCAR MEU HORÁRIO"):
        agora = datetime.now(fuso).isoformat()
        evs = service.events().list(calendarId=AGENDAS[c_barb], timeMin=agora, singleEvents=True).execute().get('items', [])
        st.session_state.eventos_encontrados = [e for e in evs if f"TEL: {c_zap}" in e.get('description', '') and f"SENHA: {c_senha}" in e.get('description', '')]
        
        if not st.session_state.eventos_encontrados:
            st.error("Nenhum agendamento encontrado.")

    for ev in st.session_state.eventos_encontrados:
        h_ev = datetime.fromisoformat(ev['start']['dateTime']).astimezone(fuso).strftime('%d/%m às %H:%M')
        st.warning(f"Reserva: {h_ev}")
        # Botão Vermelho conforme solicitado
        if st.button(f"CANCELAR AGENDAMENTO", key=f"del_{ev['id']}"):
            service.events().delete(calendarId=AGENDAS[c_barb], eventId=ev['id']).execute()
            st.session_state.eventos_encontrados = []
            st.success("🗑️ AGENDAMENTO CANCELADO!")
            st.rerun()

st.markdown(f"""<div style="position:fixed; bottom:0; width:100%; text-align:center; background:rgba(0,0,0,0.95); padding:10px; border-top:1px solid #D4AF37; color:#D4AF37; font-weight:bold;">BARBER SHOP PREMIUM © 2026 | Desenvolvido por Lucas Biazoto</div>""", unsafe_allow_html=True)
