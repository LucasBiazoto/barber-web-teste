import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

# 1. CONFIGURAÇÃO E ESTILO
st.set_page_config(page_title="Barber Agendamento", page_icon="💈", layout="centered")

# Dicionário de Serviços com durações ocultas
SERVICOS = {
    "Corte": 45,
    "Corte e Barba": 60,
    "Corte e Luzes": 60,
    "Só Barba": 30,
    "Corte Feminino": 60
}

AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

def conectar():
    try:
        with open('credentials.json') as f:
            info = json.load(f)
        # Limpeza profunda da chave para evitar erro de assinatura
        info['private_key'] = info['private_key'].replace('\\n', '\n').encode().decode('unicode_escape').replace('\\n', '\n')
        creds = service_account.Credentials.from_service_account_info(info, scopes=['https://www.googleapis.com/auth/calendar'])
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        return None

service = conectar()

# 2. INTERFACE EM PORTUGUÊS
st.title("💈 Sistema de Agendamento")

if 'liberado' not in st.session_state: st.session_state.liberado = False

tab1, tab2 = st.tabs(["📅 Novo Horário", "🔍 Meus Horários"])

with tab1:
    if not st.session_state.liberado:
        with st.form("dados_cliente"):
            st.write("### 👋 Passo 1: Identificação")
            nome = st.text_input("Seu Nome")
            celular = st.text_input("Celular (DDD + Número)")
            senha = st.text_input("Crie uma Senha (para cancelar)", type="password")
            if st.form_submit_button("VER HORÁRIOS DISPONÍVEIS"):
                if nome and len(celular) >= 10 and senha:
                    st.session_state.update({"liberado": True, "nome": nome, "cel": celular, "senha": senha})
                    st.rerun()
                else:
                    st.error("Por favor, preencha todos os campos.")
    else:
        st.write(f"### Olá {st.session_state.nome}!")
        
        c1, c2 = st.columns(2)
        with c1:
            prof = st.selectbox("Escolha o Barbeiro", list(AGENDAS.keys()))
        with c2:
            serv_escolhido = st.selectbox("Escolha o Serviço", list(SERVICOS.keys()))
            
        # Data em Português
        data_sel = st.date_input("Escolha a Data", min_value=datetime.now() + timedelta(days=1))
        
        st.write("---")
        st.write("### Horários Disponíveis:")
        horas = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
        cols = st.columns(3)
        
        for i, h in enumerate(horas):
            with cols[i % 3]:
                if st.button(h, key=f"h_{h}"):
                    # Cálculo do tempo de término baseado no serviço
                    duracao = SERVICOS[serv_escolhido]
                    inicio = datetime.strptime(f"{data_sel} {h}", "%Y-%m-%d %H:%M")
                    fim = inicio + timedelta(minutes=duracao)
                    
                    evento = {
                        'summary': f"{serv_escolhido}: {st.session_state.nome}",
                        'description': f"Tel: {st.session_state.cel} | Senha: {st.session_state.senha}",
                        'start': {'dateTime': inicio.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
                        'end': {'dateTime': fim.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
                    }
                    
                    if service:
                        try:
                            service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
                            st.balloons()
                            st.success(f"✅ Reservado! {serv_escolhido} com {prof} às {h}.")
                            st.info(f"Duração prevista na agenda: {duracao} minutos.")
                        except Exception as e:
                            st.error(f"Erro no Google Agenda. Verifique se o e-mail do bot tem acesso à agenda.")
                    else:
                        st.error("Erro de autenticação. Reinicie o App no Streamlit.")

with tab2:
    st.write("### 🔍 Meus Agendamentos")
    st.info("Em breve você poderá cancelar seus horários aqui usando sua senha.")
