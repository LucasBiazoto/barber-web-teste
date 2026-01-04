import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

# 1. CONFIGURAÇÕES FIXAS (Serviços e IDs das Agendas)
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

st.set_page_config(page_title="Barber Agendamento", page_icon="💈")

# 2. CONEXÃO SEGURA COM O GOOGLE (Usando Secrets)
def conectar():
    try:
        # Busca a chave limpa salva no painel Secrets do Streamlit
        key = st.secrets["private_key"].replace('\\n', '\n').strip()
        
        info = {
            "type": "service_account",
            "project_id": "winter-anchor-458412-u7",
            "private_key_id": "defe96a8614801119a264b0a9f94a9a609520534",
            "private_key": key,
            "client_email": "bot-salao@winter-anchor-458412-u7.iam.gserviceaccount.com",
            "client_id": "111589643947434085108",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/bot-salao%40winter-anchor-458412-u7.iam.gserviceaccount.com"
        }
        creds = service_account.Credentials.from_service_account_info(info, scopes=['https://www.googleapis.com/auth/calendar'])
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Erro de conexão com o servidor Google: {e}")
        return None

service = conectar()

# 3. INTERFACE DO USUÁRIO
st.title("💈 Sistema de Agendamento")

if 'liberado' not in st.session_state:
    st.session_state.liberado = False

tab1, tab2 = st.tabs(["📅 Novo Horário", "🔍 Meus Horários"])

with tab1:
    if not st.session_state.liberado:
        with st.form("registro"):
            st.write("### 👋 Seja bem-vindo!")
            nome = st.text_input("Seu Nome")
            celular = st.text_input("Celular (DDD + Número)")
            senha = st.text_input("Crie uma Senha (para cancelar depois)", type="password")
            if st.form_submit_button("ESCOLHER SERVIÇO"):
                if nome and celular and senha:
                    st.session_state.update({"liberado": True, "nome": nome, "cel": celular, "senha": senha})
                    st.rerun()
                else:
                    st.warning("Por favor, preencha todos os campos.")
    else:
        st.write(f"### Olá, {st.session_state.nome}!")
        
        col1, col2 = st.columns(2)
        with col1:
            prof = st.selectbox("Selecione o Profissional", list(AGENDAS.keys()))
        with col2:
            servico = st.selectbox("Selecione o Serviço", list(SERVICOS.keys()))
            
        data_sel = st.date_input("Escolha a Data", min_value=datetime.now().date() + timedelta(days=1))
        
        dias_pt = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        st.write(f"Dia selecionado: **{dias_pt[data_sel.weekday()]}**")

        st.write("---")
        st.write("### Escolha o Horário:")
        horas = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
        cols = st.columns(3)
        
        for i, h in enumerate(horas):
            with cols[i % 3]:
                if st.button(h, key=f"h_{h}"):
                    duracao = SERVICOS[servico]
                    inicio = datetime.strptime(f"{data_sel} {h}", "%Y-%m-%d %H:%M")
                    fim = inicio + timedelta(minutes=duracao)
                    
                    evento = {
                        'summary': f"{servico}: {st.session_state.nome}",
                        'description': f"TEL:{st.session_state.cel}|PWD:{st.session_state.senha}",
                        'start': {'dateTime': inicio.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
                        'end': {'dateTime': fim.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
                    }
                    
                    try:
                        service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
                        st.balloons()
                        st.success(f"✅ Agendado! {servico} com {prof} às {h}.")
                    except Exception as e:
                        st.error(f"Erro ao salvar: Verifique se o bot tem acesso à agenda do {prof}. Detalhe: {e}")

with tab2:
    st.write("### 🔍 Consultar Agendamentos")
    cel_busca = st.text_input("Celular cadastrado")
    senha_busca = st.text_input("Sua senha", type="password")
    
    if st.button("BUSCAR HORÁRIOS"):
        if cel_busca and senha_busca:
            encontrados = False
            for p_nome, p_id in AGENDAS.items():
                try:
                    now = datetime.utcnow().isoformat() + 'Z'
                    events_result = service.events().list(calendarId=p_id, timeMin=now, singleEvents=True, orderBy='startTime').execute()
                    for e in events_result.get('items', []):
                        desc = e.get('description', '')
                        if f"TEL:{cel_busca}" in desc and f"PWD:{senha_busca}" in desc:
                            dt = datetime.fromisoformat(e['start']['dateTime'][:-6]).strftime('%d/%m às %H:%M')
                            st.write(f"📌 **{e['summary']}** com {p_nome} em {dt}")
                            if st.button(f"Cancelar ID: {e['id'][:5]}", key=e['id']):
                                service.events().delete(calendarId=p_id, eventId=e['id']).execute()
                                st.success("Cancelado! Atualize a página.")
                            encontrados = True
                except: continue
            if not encontrados:
                st.warning("Nenhum agendamento futuro encontrado.")
        else:
            st.info("Digite seus dados para buscar.")
