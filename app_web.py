import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# IDs das Agendas dos Barbeiros
AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

st.set_page_config(page_title="Barber Agendamento", page_icon="💈")

def conectar():
    try:
        # A chave é colada aqui com aspas triplas para preservar as quebras de linha exatas
        pk = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDOVI4nXYJEUnNb
HQ6T931Z7ZLCg5nIfqTazKaVMbMyBlAcb/wbsSp+EGdzlRPqemUofI8DuBU7V2uH
YB0dKirz00yi2NS1qMA7YEEi5MJb0wV8Vyh+N/IGsMswef77tqlZN+VcsmsYn8UL
Qu9C7XzYPNXC74bO92I/SmWOzwJi3KYUTvmIDqzTVlGEbbW8UodLIGE7qKNHgxqr
asLht+RdA/O3OEv7Znb/bz+VxpeQ4/EmG6zJNkf/z+xZQFPKhY/77H+KJLjFP8U1
F2idBBp3G2ox6LKgDQMDUzt2orJTyHOgiIBcgc3OUzPp7k3dGuUPmopulB01MNDR
KC7TzdEZAgMBAAECggEABYwcbk6DTBbzZwW2+J90zVAn2/bx0YQmJoPODsDRUoz8
5mbUXmI7BDyoq2DcsjcsNRR0O+NdHsVQ7MjWv4v8r6WEr/Qoc+HfmTkTRz7jQti/
kwI84nfal/d03w7InjfhAbcRAZcCbh0NjSn1iNUdwCqSjLUn6LSZ/Z2gcWB7bfD4
YZJiR20MjfDMytsNyDwXO128eKssAa1rsi4DkoImQn/hvEDdZJFY87qH9S5icgsX
FN4gaodI85Q8CNXCQRIcJCu5V1R0xnFcG5cQrN8LkyeimEKYXtXJ2ffeyBxIwgox
xKbLziMrFEH0UWv/BW81NzBhY7AFHQKZIorsXBjaAQKBgQDrK3ji9w8kkGEw/Op6
NlLjVcWo2S70S4tFHKdQM7SnGxUxVQQWieHEI0XbrN47oAt9KoEFJLvpks23BQQM
Trmdqegfzic1XnJm0PNN8jm8sje9kqofO15sBvqx72mgIRhhZNLR3gQ7+NUhBaGp
E8Hs21nwNPg1w6G3/kwM3pYCuQKBgQDgmyP8Jr5yCKUcguK9g/umXKjo2j7jdKQ9
D9KYFqlWu/SJaRczyEs7211zD8ulZSUAoQ79jwTCjMzMRlFVT5Nl7hPYdkfi3xUP
y/9z4lToWJ5DKDmLVwBu69LDEM1uQ7GNUNcIJbj2KsXDXSJyBJej4Oo3axfdagu7
9pe3KsyRYQKBgQC/RgR01e2DF8t1RMCR1k1kigbSZpNCL49/Ducm3Gc641RBY5yH
mG4AUZAoNFostOejTkbSICaWu8iF65Z3TDC8g81A0TQivEbgSWMbKsC7MVkU341v
CaKqyqJsxwVqMIDb9l1iROm8vY7b5PCvzFoWg/KK5Qpc8FlAhZzlesUYQQKBgQCH
uPfLvNXELrknO2gsQP7mDoP7ATaTV76PL2qAgOEfCkDAcAKXRedAalRT3S2f6jir
4qceTTgBH/f5UFyBgq59H5paaU8TJt6hRxI8Qn4wUKyBxGLRcmdOn64iNZsNkFZQ
IJNv1uunxTzvyu2vnFrNqnGdv1cScqxYjrAq/O/UwQKBgHKI6o81or0V+vOr5WO1
5TFE1SrFoR4KLC1dvzWzs7e3KwBoS+RWGSAmhPAAt0tDYHWKzd0bpNCcPqBeeogZ
5m6Sx3Rez5VLz3OPylnZ+si7Bjqe+YVNGvngc2rlpODSaRRH0zO4smZO0Q+Rfb8g
hRF4nL2nQtCv+v+djNpTLCGm
-----END PRIVATE KEY-----"""

        info = {
            "type": "service_account",
            "project_id": "winter-anchor-458412-u7",
            "private_key": pk,
            "client_email": "bot-salao@winter-anchor-458412-u7.iam.gserviceaccount.com",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        
        # Cria a credencial e o serviço do Google Calendar
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=['https://www.googleapis.com/auth/calendar']
        )
        return build('calendar', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Erro crítico na conexão: {e}")
        return None

# Inicializa o serviço
service = conectar()

st.title("💈 Barber Agendamento")

# Interface de Agendamento
with st.container():
    nome = st.text_input("Seu Nome")
    celular = st.text_input("Celular (Ex: 11984681343)")
    senha = st.text_input("Crie uma Senha (para cancelar depois)", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        prof = st.selectbox("Barbeiro", list(AGENDAS.keys()))
    with col2:
        servico = st.selectbox("Serviço", ["Corte", "Barba", "Corte e Barba"])
        
    data_sel = st.date_input("Escolha a Data", min_value=datetime.now().date())

st.write("---")
st.write("### Horários Disponíveis:")

# Grade de horários
horas = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
cols = st.columns(3)

for i, h in enumerate(horas):
    with cols[i % 3]:
        if st.button(h, key=f"btn_{h}", use_container_width=True):
            if not (nome and celular and senha):
                st.warning("⚠️ Por favor, preencha todos os campos antes de escolher o horário.")
            elif service:
                try:
                    # Configura o evento para o Google Calendar
                    inicio = datetime.strptime(f"{data_sel} {h}", "%Y-%m-%d %H:%M")
                    fim = inicio + timedelta(minutes=45)
                    
                    evento = {
                        'summary': f"{servico}: {nome}",
                        'description': f"TEL: {celular} | SENHA: {senha}",
                        'start': {
                            'dateTime': inicio.strftime('%Y-%m-%dT%H:%M:00-03:00'),
                            'timeZone': 'America/Sao_Paulo',
                        },
                        'end': {
                            'dateTime': fim.strftime('%Y-%m-%dT%H:%M:00-03:00'),
                            'timeZone': 'America/Sao_Paulo',
                        },
                    }
                    
                    # Tenta inserir na agenda correspondente
                    service.events().insert(calendarId=AGENDAS[prof], body=evento).execute()
                    st.success(f"✅ Sucesso! Agendado com {prof} às {h}.")
                    st.balloons()
                except Exception as e:
                    # Exibe erro detalhado caso a assinatura falhe novamente
                    st.error(f"Erro ao salvar na agenda: {e}")
