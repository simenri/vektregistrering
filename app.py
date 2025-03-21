import streamlit as st
import base64
import json
from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO
from services.sheets_service import get_google_sheet
from utils.helpers import get_todays_date, get_timestamp
from components.batch_selector import render_batch_selector
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

dagens_batches = [r['Batch nr'] for r in batch_info if r['Dato for henting'] == todays_date]

# UI
st.markdown("<h2>Vektregistrering Carbon Centric AS</h2>", unsafe_allow_html=True)

custom_batch = render_batch_selector(dagens_batches, todays_date)
st.write(f"Valgt batchnummer: {custom_batch}")

vekt_input = st.number_input("Vekt (kg)", value=0)

# Send til Sheets
if st.button("Send inn"):
    if custom_batch and vekt_input:
        timestamp = get_timestamp()
        sheet.append_row([timestamp, custom_batch, vekt_input])
        st.success("Data registrert!")
    else:
        st.error("Vennligst fyll inn alle felt")


encoded_creds = st.secrets["google"]["google_credentials"]
padding = len(encoded_creds) % 4
if padding != 0: # Sjekker om den faktisk opprettholder kravet om at det skal være delelig på fire og legger på padding dersom det ikke er det.
    encoded_creds += "=" * (4 - padding)
creds_json = base64.b64decode(encoded_creds)
with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
    tmp_file.write(creds_json)
    tmp_file_path = tmp_file.name

# Sett miljøvariabelen til den midlertidige filen
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_file_path


img_file = st.camera_input("Ta bilde av vekta")

if img_file is not None:
    # Vis bilde
    st.image(img_file)

    # Lagre bildet midlertidig for Vision API
    image_bytes = img_file.getvalue()
    image = vision.Image(content=image_bytes)

    # Initier Vision-klient
    client = vision.ImageAnnotatorClient()
    response = client.text_detection(image=image)

    texts = response.text_annotations
    if texts:
        # Første element er hele teksten, resten er delene
        detected_text = texts[0].description.strip()
        st.success(f"Oppdaget tall: {detected_text}")
    else:
        st.warning("Fikk ikke tolket noe tall fra bildet.")

st.markdown("<div class='footer'>© 2025 Carbon Centric AS | Vektregistrering </div>", unsafe_allow_html=True)
