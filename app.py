import streamlit as st
import base64
import json
from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO
from services.sheets_service import get_google_sheet
from utils.helpers import get_todays_date, get_timestamp
from components.batch_selector import render_batch_selector

# Konfigurasjon
st.set_page_config(page_title="Vektregistrering Carbon Centric", page_icon="📱", initial_sidebar_state="collapsed")

# Tilkobling til Sheets
sheet = get_google_sheet("Tankbil-CC", "Measurements")
batch_sheet = get_google_sheet("Tankbil-CC", "Batches")

batch_info = batch_sheet.get_all_records()
todays_date = get_todays_date()

dagens_batches = [r['Batch nr'] for r in batch_info if r['Dato for henting'] == todays_date]

# UI
st.markdown("<h2>Vektregistrering Carbon Centric AS</h2>", unsafe_allow_html=True)

custom_batch = render_batch_selector(dagens_batches, todays_date)
st.write(f"Valgt batchnummer: {custom_batch}")

vekt_input = st.text_input("Vekt (kg)", value="")

# Send til Sheets
if st.button("Send inn"):
    if custom_batch and vekt_input:
        timestamp = get_timestamp()
        sheet.append_row([timestamp, custom_batch, vekt_input])
        st.success("Data registrert!")
    else:
        st.error("Vennligst fyll inn alle felt")

st.markdown("<div class='footer'>© 2025 Carbon Centric AS | Vektregistrering </div>", unsafe_allow_html=True)
