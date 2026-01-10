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
# ESTILO VISUAL (CORES AJUSTADAS)
# =========================================================
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.65)), 
        url("https://images.unsplash.com/photo-1503951914875-452162b0f3f1?q=80&w=2070");
        background-size: cover;
        background-attachment: fixed;
    }
    /* Labels Brancas */
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
    h1 { color: #D4AF37 !important; text-align: center; }
    
    /* Botões de Horário e Agendar (Dourado/Amarelo) */
    div.stButton > button {
        background-color: #D4AF37 !important;
        color: black !important;
        font-weight: bold;
        border: none;
    }
    
    /* Cor de sucesso do agendamento (Verde) */
    .stSuccess {
        background-color: rgba(40, 167, 69, 0.8) !important;
        color: white !important;
        font-weight: bold !important;
    }

    /* Esconder elementos padrão */
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
# LÓGICA DE CONEXÃO E BLOQUEIO REAL DE DIA INTEIRO
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
        # Busca estendida para pegar eventos de dia inteiro corretamente
        min_t = fuso.localize(datetime.combine(data, time.min)).isoformat()
        max_t = fuso.localize(datetime.combine(data, time.max)).isoformat()
        
        events_result = service.events().list(calendarId=calendar_id, timeMin=min_t, timeMax=max_t, singleEvents=True).execute()
        eventos = events_result.get('items', [])
        ocupados = []
        
        for ev in eventos:
            # Se o evento for de dia inteiro, o Google retorna apenas 'date' em vez de 'dateTime'
            if 'date' in ev['start']:
                # Verifica se a data do evento coincide com a data selecionada
                if ev['start']['date'] == data.strftime('%Y-%m-%d'):
                    return "BLOQUEADO"
            
            start_dt = ev['start'].get('dateTime')
            if start_dt:
                hora = datetime.fromisoformat(start_dt).astimezone(fuso).strftime('%H:%M')
                ocupados.append(hora)
        return ocupados
    except: return []

# =========================================================
# INTERFACE
# =========================================================
st.title("💈 BARBER SHOP PREMIUM")
aba1, aba2 = st.tabs(["📅 AGENDAR", "❌ CANCELAR AGENDAMENTO"])

with aba1:
    nome = st.text_input("Nome completo ou apelido")
    col1, col2 = st.columns(2)
    with col1: celular = st.text_input("WhatsApp com DDD")
    with col2: senha = st.text_input("Senha de Cancelamento", type="password")
    
    prof = st.selectbox("Barbeiro", list(AGENDAS.keys()))
    servico = st.selectbox("Serviço", ["Corte", "Barba", "Combo Premium"])
    data_sel = st.date_input("Data", min_value=datetime.now(fuso).date())
    
    status = get_status_dia(AGENDAS[prof], data_sel)
    
    if status == "BLOQUEADO":
        st.error(f"🚫 O barbeiro {prof} está indisponível em {data_sel.strftime('%d/%m/%Y')} (Folga/Evento dia todo).")
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
                            # Força o minuto zero para evitar os 6 minutos de diferença
                            h_int = int(h.split(':')[0])
                            inicio = fuso.localize(datetime.combine(data_sel, time(hour=h_int, minute=0)))
                            evento = {
                                'summary': f"{servico}: {nome}",
                                'description': f"TEL: {celular} | SENHA: {senha}",
                                'start': {'dateTime': inicio.isoformat()},
                                'end': {'dateTime': (inicio + timedelta(minutes=45)).isoformat()},
                            }
                            service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
                            st.success(f"✅ Agendamento realizado para às {h}!")
                            st.rerun()
                        else: st.warning("Preencha todos os campos!")

with aba2:
    st.write("### 🔍 Cancelar seu Horário")
    c_tel = st.text_input("Digite o WhatsApp cadastrado")
    c_senha = st.text_input("Digite a senha cadastrada", type="password")
    c_prof = st.selectbox("Selecione o Barbeiro", list(AGENDAS.keys()), key="cancel_prof")

    if st.button("BUSCAR MEU AGENDAMENTO", use_container_width=True):
        agora = datetime.now(fuso).isoformat()
        evs = service.events().list(calendarId=AGENDAS[c_prof], timeMin=agora, singleEvents=True).execute().get('items', [])
        meus_agendamentos = [e for e in evs if f"TEL: {c_tel}" in e.get('description', '') and f"SENHA: {c_senha}" in e.get('description', '')]
        
        if meus_agendamentos:
            for ev in meus_agendamentos:
                dt_inicio = datetime.fromisoformat(ev['start']['dateTime']).astimezone(fuso)
                st.warning(f"Agendamento: {dt_inicio.strftime('%d/%m/%Y')} às {dt_inicio.strftime('%H:%M')}")
                if st.button("CONFIRMAR CANCELAMENTO", key=f"del_{ev['id']}", use_container_width=True):
                    service.events().delete(calendarId=AGENDAS[c_prof], eventId=ev['id']).execute()
                    st.success("Cancelado com sucesso!")
                    st.rerun()
        else:
            st.error("Nenhum agendamento encontrado com esses dados.")

st.markdown(f"""<div class="footer-custom">Desenvolvido por Lucas Biazoto | <a href="https://github.com/LBiazoto" target="_blank">GitHub</a></div>""", unsafe_allow_html=True)
