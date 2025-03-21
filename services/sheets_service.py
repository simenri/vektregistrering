import base64
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import streamlit as st
from io import BytesIO

def get_google_sheet(sheet_name, worksheet_name="Sheet1"):
    #Henter først ut credentials fra secrets:

    encoded_creds = st.secrets["google"]["google_credentials"]
    padding = len(encoded_creds) % 4
    if padding != 0: # Sjekker om den faktisk opprettholder kravet om at det skal være delelig på fire og legger på padding dersom det ikke er det.
        encoded_creds += "=" * (4 - padding)
    creds_json = base64.b64decode(encoded_creds)
    creds_dict = json.loads(creds_json)

    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).worksheet(worksheet_name)
    return sheet
