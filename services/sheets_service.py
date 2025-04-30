import base64
import json
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

def get_google_sheet(sheet_name, worksheet_name="Sheet1"):
    encoded_creds = st.secrets["google"]["google_credentials"]

    # Fix base64 padding
    padding = len(encoded_creds) % 4
    if padding != 0:
        encoded_creds += "=" * (4 - padding)

    creds_json = base64.b64decode(encoded_creds)
    creds_dict = json.loads(creds_json)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file"
    ]

    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open(sheet_name).worksheet(worksheet_name)
