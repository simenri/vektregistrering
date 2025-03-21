import base64
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import streamlit as st
from io import BytesIO

def get_google_sheet(sheet_name, worksheet_name="Sheet1"):
    encoded_creds = st.secrets["google"]["google_credentials"]
    creds_json = base64.b64decode(encoded_creds)
    creds_file = BytesIO(creds_json)

    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).worksheet(worksheet_name)
    return sheet
