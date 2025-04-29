import base64
import json
import gspread
import streamlit as st
from io import BytesIO
import os
import tempfile

def set_enivronment_variable():

    #Henter først ut credentials fra secrets:
    encoded_creds = st.secrets["google"]["google_credentials"]
    padding = len(encoded_creds) % 4
    if padding != 0: # Sjekker om den faktisk opprettholder kravet om at det skal være delelig på fire og legger på padding dersom det ikke er det.
        encoded_creds += "=" * (4 - padding)
    creds_json = base64.b64decode(encoded_creds)

    #Lager så en midlertidig fil
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
        tmp_file.write(creds_json)
        tmp_file_path = tmp_file.name

    return tmp_file_path
