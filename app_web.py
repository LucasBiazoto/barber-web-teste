import streamlit as st
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ===============================
# CONFIGURAÇÃO DA PÁGINA
# ===============================
st.set_page_config(
    page_title="Barber Agendamento",
    page_icon="💈",
    layout="centered"
)

# ===============================
# CSS (Mobile Friendly)
# ===============================
st.markdown("""
<style>
div.stButton > button:first-child {
    width: 100%;
    height: 3.5em;
    font-size: 18px;
    font-weight: bold;
    border-radius: 12px;
}

.stFormSubmitButton > button {
    background-color: #28a745 !important;
    color: white !important;
    width: 100%;
    height: 3.5em;
    font-size: 18px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# GOOGLE CALENDAR
# ===============================
FILE_KEY = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

AGENDAS = {
    "Bruno": "b2f33326cb9d42ddf65423eed8332d70be96f8b21f18a902093ea432d1d523f5@group.calendar.google.com",
    "Duda": "7e95af6d94ea5bcf73f15c8dbc4ddc29fe544728219617478566bca73d05d7d4@group.calendar.google.com",
    "Nenê": "6f51a443e21211459f88c6b6e2c6173c6be31d19e151d8d1a700e96c99519920@group.calendar.google.com"
}

def conectar_google():
    try:
        creds = service_account.Credentials.from_service_account_file(
            FILE_KEY, scopes=SCOPES
