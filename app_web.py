import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

# 1. CONFIGURAÇÃO DE SERVIÇOS E AGENDAS
SERVICOS = {
    "Corte": 45,
    "Corte e Barba": 60,
    "Corte e Luzes": 60,
    "Só Barba": 30,
    "Corte Feminino": 60
}

# IDs confirmados via print
AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

st.set_page_config(page_title="Barber Agendamento", page_icon="💈")

def conectar():
    try:
        with open('credentials.json') as f:
            info = json.load(f)
        # Limpeza robusta para evitar o 'Invalid JWT Signature'
        key = info['private_key'].replace('\\n', '\n').strip()
        info['private_key'] = key
        
        creds = service_account.Credentials.from_service_account_info(
            info, 
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        return build('calendar', 'v3', credentials=creds, cache_discovery=False)
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

service = conectar()

# 2. INTERFACE
st.title("💈 Sistema de Agendamento")

if 'liberado' not in st.session_state:
    st.session_state.liberado = False

tab1, tab2 = st.tabs(["📅 Novo Horário", "🔍 Meus Horários"])

with tab1:
    if not st.session_state.liberado:
        with st.form("registro"):
            st.write("### 👋 Seja bem-vindo!")
            nome = st.text_input("Seu Nome")
            celular = st.text_input("Celular com DDD")
            senha = st.text_input("Crie uma Senha", type="password")
            if st.form_submit_button("ESCOLHER SERVIÇO"):
                if nome and celular and senha:
                    st.session_state.update({"liberado": True, "nome": nome, "cel": celular, "senha": senha})
                    st.rerun()
    else:
        st.write(f"### Olá, {st.session_state.nome}!")
        c1, c2 = st.columns(2)
        with c1: prof = st.selectbox("Barbeiro", list(AGENDAS.keys()))
        with c2: serv = st.selectbox("Serviço", list(SERVICOS.keys()))
            
        data_sel = st.date_input("Escolha a Data", min_value=datetime.now().date() + timedelta(days=1))
        
        dias_pt = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        st.write(f"Dia selecionado: **{dias_pt[data_sel.weekday()]}**")

        st.write("---")
        horas = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
        cols = st.columns(3)
        
        for i, h in enumerate(horas):
            with cols[i % 3]:
                if st.button(h, key=f"btn_{h}"):
                    minutos = SERVICOS[serv]
                    inicio = datetime.strptime(f"{data_sel} {h}", "%Y-%m-%d %H:%M")
                    fim = inicio + timedelta(minutes=minutos)
                    
                    evento = {
                        'summary': f"{serv}: {st.session_state.nome}",
                        'description': f"TEL:{st.session_state.cel}|PWD:{st.session_state.senha}",
                        'start': {'dateTime': inicio.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
                        'end': {'dateTime': fim.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
                    }
                    
                    try:
                        # Tenta gravar na agenda específica
                        service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
                        st.balloons()
                        st.success(f"✅ Agendado com {prof} às {h}!")
                    except Exception as e:
                        # Backup de emergência
                        try:
                            service.events().insert(calendarId='primary', body=evento).execute()
                            st.success("✅ Agendado na agenda principal!")
                        except:
                            st.error(f"Erro crítico: {e}. Verifique se o bot ainda tem a permissão 'Fazer alterações' no Google Agenda.")

with tab2:
    st.write("### 🔍 Consultar Agendamento")
    st.info("Digite seu celular e senha para cancelar seu horário.")
