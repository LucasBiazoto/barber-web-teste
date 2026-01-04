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

# IDs das Agendas
# DICA: 'primary' tenta gravar na agenda principal do dono do bot
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
        # Limpeza robusta da chave
        info['private_key'] = info['private_key'].replace('\\n', '\n')
        creds = service_account.Credentials.from_service_account_info(info, scopes=['https://www.googleapis.com/auth/calendar'])
        return build('calendar', 'v3', credentials=creds)
    except:
        return None

service = conectar()

# 2. INTERFACE
st.title("💈 Sistema de Agendamento")

if 'liberado' not in st.session_state:
    st.session_state.liberado = False

tab1, tab2 = st.tabs(["📅 Novo Horário", "🔍 Meus Horários"])

with tab1:
    if not st.session_state.liberado:
        with st.form("cadastro"):
            st.write("### 👋 Identificação")
            nome = st.text_input("Seu Nome")
            celular = st.text_input("Celular com DDD")
            senha = st.text_input("Crie uma Senha (para cancelar)", type="password")
            if st.form_submit_button("ESCOLHER SERVIÇO"):
                if nome and celular and senha:
                    st.session_state.update({"liberado": True, "nome": nome, "cel": celular, "senha": senha})
                    st.rerun()
    else:
        st.write(f"### Olá, {st.session_state.nome}!")
        
        c1, c2 = st.columns(2)
        with c1:
            prof = st.selectbox("Barbeiro", list(AGENDAS.keys()))
        with c2:
            serv = st.selectbox("Serviço", list(SERVICOS.keys()))
            
        data_sel = st.date_input("Escolha a Data", min_value=datetime.now().date() + timedelta(days=1))
        
        dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        st.write(f"Dia selecionado: **{dias[data_sel.weekday()]}**")

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
                        'description': f"Tel: {st.session_state.cel} | Senha: {st.session_state.senha}",
                        'start': {'dateTime': inicio.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
                        'end': {'dateTime': fim.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
                    }
                    
                    try:
                        # Tenta gravar na agenda selecionada
                        service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
                        st.balloons()
                        st.success(f"✅ Agendado com {prof} às {h}!")
                    except Exception:
                        # SE FALHAR, tenta gravar na agenda principal (backup)
                        try:
                            service.events().insert(calendarId='primary', body=evento).execute()
                            st.success(f"✅ Agendado na agenda principal às {h}!")
                        except Exception as e:
                            st.error(f"Erro persistente: {e}. Verifique as permissões de compartilhamento no Google Agenda.")

with tab2:
    st.write("### 🔍 Consultar Agendamento")
    st.info("Digite seu celular e senha para ver ou cancelar.")
