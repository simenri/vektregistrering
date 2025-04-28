import streamlit as st
import base64
import json
import re

from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO
from services.sheets_service import get_google_sheet
from utils.helpers import get_todays_date, get_timestamp
from components.batch_selector import render_batch_selector
from components.empty_or_full_selector import render_empty_or_full_selector
from components.aksel_selector import render_aksel_selector
from components.ocr_camera_feature import render_ocr_camera_feature
from services.environment_variable_service import set_enivronment_variable
from google.cloud import vision
import os
import tempfile




# Konfigurasjon
st.set_page_config(page_title="Vektregistrering Carbon Centric", page_icon="📱", initial_sidebar_state="collapsed")

# Tilkobling til Sheets
sheet = get_google_sheet("Tankbil-CC", "Measurements")
batch_sheet = get_google_sheet("Tankbil-CC", "Batches")

batch_info = batch_sheet.get_all_records()
todays_date = get_todays_date()
dagens_batches = [r['Batch ID'] for r in batch_info if r['Date of analysis'] == todays_date]


# UI
st.markdown("<h2>Vektregistrering Carbon Centric AS</h2>", unsafe_allow_html=True)

custom_batch = render_batch_selector(dagens_batches, todays_date)
st.write(f"Valgt batchnummer: {custom_batch}")

fyllingsgrad = render_empty_or_full_selector()
weight_value = 0 # Set weight

col1, col2 = st.columns(2)
with col1:
    aksel = render_aksel_selector()
with col2: 
    use_camera = st.checkbox('Bildegjenkjenning')
# Bruk session_state for å huske verdien mellom reruns
if "detected_num" not in st.session_state:
    st.session_state.detected_num = 0

# Hvis kamera-knappen trykkes, be om bilde
if use_camera:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = set_enivronment_variable()
    img_file = st.camera_input("Ta bilde av vekta")

    if img_file is not None:
        st.image(img_file)

        # Send til Vision API
        image_bytes = img_file.getvalue()
        image = vision.Image(content=image_bytes)
        client = vision.ImageAnnotatorClient()
        response = client.text_detection(image=image)

        texts = response.text_annotations
        if texts:
            detected_text = texts[0].description.strip()
            numbers = re.findall(r'\d+', detected_text)
            if numbers:
                detected_text = ''.join(numbers)
                st.session_state.detected_num = int(detected_text)
                st.success(f"Oppdaget tall: {detected_text}")
            else:
                st.warning("Fant ingen tall i bildet.")
                st.session_state.detected_num = 0
        else:
            st.warning("Fikk ikke tolket noe tekst fra bildet.")
            st.session_state.detected_num = 0
    vekt_input = st.session_state.detected_num
else:
    vekt_input = st.number_input("Vekt (kg)", value=st.session_state.detected_num, step=1)

# Bruk det foreslåtte tallet (eller 0) i tallvelgeren – alltid redigerbar
st.write(f"Registrert vekt: {vekt_input}")

# Send til Sheets
if st.button("Send inn"):
    if custom_batch and vekt_input:
        timestamp = get_timestamp()
        sheet.append_row([timestamp, fyllingsgrad, aksel, custom_batch, vekt_input])
        st.success("Data registrert!")
    else:
        st.error("Vennligst fyll inn alle felt")



st.markdown("<div class='footer'>© 2025 Carbon Centric AS | Vektregistrering </div>", unsafe_allow_html=True)
