import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# CONFIGURAÇÕES FIXAS
SERVICOS = {"Corte": 45, "Corte e Barba": 60, "Corte e Luzes": 60, "Só Barba": 30, "Corte Feminino": 60}
AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

st.set_page_config(page_title="Barber Agendamento", page_icon="💈")

def conectar():
    try:
        # CHAVE INSERIDA DIRETAMENTE PARA ELIMINAR O ERRO DE ASSINATURA
        private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDOVI4nXYJEUnNb\nHQ6T931Z7ZLCg5nIfqTazKaVMbMyBlAcb/wbsSp+EGdzlRPqemUofI8DuBU7V2uH\nYB0dKirz00yi2NS1qMA7YEEi5MJb0wV8Vyh+N/IGsMswef77tqlZN+VcsmsYn8UL\nQu9C7XzYPNXC74bO92I/SmWOzwJi3KYUTvmIDqzTVlGEbbW8UodLIGE7qKNHgxqr\nasLht+RdA/O3OEv7Znb/bz+VxpeQ4/EmG6zJNkf/z+xZQFPKhY/77H+KJLjFP8U1\nF2idBBp3G2ox6LKgDQMDUzt2orJTyHOgiIBcgc3OUzPp7k3dGuUPmopulB01MNDR\nKC7TzdEZAgMBAAECggEABYwcbk6DTBbzZwW2+J90zVAn2/bx0YQmJoPODsDRUoz8\n5mbUXmI7BDyoq2DcsjcsNRR0O+NdHsVQ7MjWv4v8r6WEr/Qoc+HfmTkTRz7jQti/\nkwI84nfal/d03w7InjfhAbcRAZcCbh0NjSn1iNUdwCqSjLUn6LSZ/Z2gcWB7bfD4\nYZJiR20MjfDMytsNyDwXO128eKssAa1rsi4DkoImQn/hvEDdZJFY87qH9S5icgsX\nFN4gaodI85Q8CNXCQRIcJCu5V1R0xnFcG5cQrN8LkyeimEKYXtXJ2ffeyBxIwgox\nxKbLziMrFEH0UWv/BW81NzBhY7AFHQKZIorsXBjaAQKBgQDrK3ji9w8kkGEw/Op6\nNlLjVcWo2S70S4tFHKdQM7SnGxUxVQQWieHEI0XbrN47oAt9KoEFJLvpks23BQQM\nTrmdqegfzic1XnJm0PNN8jm8sje9kqofO15sBvqx72mgIRhhZNLR3gQ7+NUhBaGp\nE8Hs21nwNPg1w6G3/kwM3pYCuQKBgQDgmyP8Jr5yCKUcguK9g/umXKjo2j7jdKQ9\nD9KYFqlWu/SJaRczyEs7211zD8ulZSUAoQ79jwTCjMzMRlFVT5Nl7hPYdkfi3xUP\ny/9z4lToWJ5DKDmLVwBu69LDEM1uQ7GNUNcIJbj2KsXDXSJyBJej4Oo3axfdagu7\n9pe3KsyRYQKBgQC/RgR01e2DF8t1RMCR1k1kigbSZpNCL49/Ducm3Gc641RBY5yH\nmG4AUZAoNFostOejTkbSICaWu8iF65Z3TDC8g81A0TQivEbgSWMbKsC7MVkU341v\nCaKqyqJsxwVqMIDb9l1iROm8vY7b5PCvzFoWg/KK5Qpc8FlAhZzlesUYQQKBgQCH\nuPfLvNXELrknO2gsQP7mDoP7ATaTV76PL2qAgOEfCkDAcAKXRedAalRT3S2f6jir\n4qceTTgBH/f5UFyBgq59H5paaU8TJt6hRxI8Qn4wUKyBxGLRcmdOn64iNZsNkFZQ\nIJNv1uunxTzvyu2vnFrNqnGdv1cScqxYjrAq/O/UwQKBgHKI6o81or0V+vOr5WO1\n5TFE1SrFoR4KLC1dvzWzs7e3KwBoS+RWGSAmhPAAt0tDYHWKzd0bpNCcPqBeeogZ\n5m6Sx3Rez5VLz3OPylnZ+si7Bjqe+YVNGvngc2rlpODSaRRH0zO4smZO0Q+Rfb8g\nhRF4nL2nQtCv+v+djNpTLCGm\n-----END PRIVATE KEY-----\n"
        
        info = {
            "type": "service_account",
            "project_id": "winter-anchor-458412-u7",
            "private_key": private_key.replace('\\n', '\n'),
            "client_email": "bot-salao@winter-anchor-458412-u7.iam.gserviceaccount.com",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=['https://www.googleapis.com/auth/calendar']
        )
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Erro na conexão Google: {e}")
        return None

service = conectar()

st.title("💈 Barber Agendamento")

tab1, tab2 = st.tabs(["📅 Novo Horário", "🔍 Meus Horários"])

with tab1:
    nome = st.text_input("Seu Nome")
    celular = st.text_input("Celular (DDD + Número)")
    senha = st.text_input("Crie uma Senha para cancelamentos", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        prof = st.selectbox("Barbeiro", list(AGENDAS.keys()))
    with col2:
        servico = st.selectbox("Serviço", list(SERVICOS.keys()))
        
    data_sel = st.date_input("Escolha a Data", min_value=datetime.now().date())
    
    st.write("---")
    st.write("### Horários Disponíveis:")
    horas = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    cols = st.columns(3)
    
    for i, h in enumerate(horas):
        with cols[i % 3]:
            if st.button(h, key=f"h_{h}"):
                if not (nome and celular and senha):
                    st.warning("Preencha Nome, Celular e Senha.")
                elif service:
                    try:
                        inicio = datetime.strptime(f"{data_sel} {h}", "%Y-%m-%d %H:%M")
                        fim = inicio + timedelta(minutes=SERVICOS[servico])
                        
                        evento = {
                            'summary': f"{servico}: {nome}",
                            'description': f"TEL: {celular} | SENHA: {senha}",
                            'start': {'dateTime': inicio.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
                            'end': {'dateTime': fim.strftime('%Y-%m-%dT%H:%M:00-03:00'), 'timeZone': 'America/Sao_Paulo'},
                        }
                        
                        service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
                        st.success(f"✅ Agendado com sucesso para {h}!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Erro ao salvar na agenda: {e}")

with tab2:
    st.info("Em breve: Consulta e cancelamento de horários.")
