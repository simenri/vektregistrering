import streamlit as st
from PIL import Image
import pytesseract
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
#import pyrebase


scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("google_sheet_creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Tankbil-CC").sheet1


st.set_page_config(
    page_title="Vektregistrering Carbon Centric",
    page_icon="📱",
    layout="wide",  # Bruk "wide" for bedre plass på mobil
    initial_sidebar_state="collapsed"
)

st.markdown("<h2>Vektregistrering Carbon Centric</h2>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# Lager litt info bare for å vise frem:

# Forslag til registreringsnummer basert på dato (mock)
heutige_dato = datetime.now().strftime('%Y-%m-%d')
forventede_biler = {
    "2025-03-19": ["AB12345", "CD67890"],
    "2025-03-20": ["EF12345"]
}

forslag_regnr = forventede_biler.get(heutige_dato, [])
regnr = st.selectbox("Batchnummer", forslag_regnr + ["Annet..."])
if regnr == "Annet...":
    regnr = st.text_input("Skriv inn batchnummer")

# Last opp bilde og kjør OCR
# uploaded_file = st.file_uploader("Last opp bilde av vekt-display")
vekt_detected = ""

# if uploaded_file:
#     image = Image.open(uploaded_file)
#     st.image(image, caption="Opplastet bilde", use_column_width=True)
#     vekt_detected = pytesseract.image_to_string(image, config='--psm 7 digits')
#     st.write(f"Gjenkjent vekt: {vekt_detected.strip()}")

# Tillat overstyring
vekt_input = st.text_input("Vekt (kg)", value=vekt_detected.strip())

# Send til Google Sheet
if st.button("Send inn"):
    if regnr and vekt_input:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, regnr, vekt_input])
        st.success("Data registrert!")
    else:
        st.error("Vennligst fyll inn alle felt")


st.markdown("<div class='footer'>© 2025 Carbon Centric AS | Vektregistrering </div>", unsafe_allow_html=True)
