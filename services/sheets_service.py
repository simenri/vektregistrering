import base64
import json
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from io import BytesIO

def get_google_sheet(sheet_name, worksheet_name="Sheet1"):
    # Retrieve credentials from Streamlit secrets
    encoded_creds = st.secrets["google"]["google_credentials"]

    # Fix padding if needed
    padding = len(encoded_creds) % 4
    if padding != 0:
        encoded_creds += "=" * (4 - padding)

    creds_json = base64.b64decode(encoded_creds)
    creds_dict = json.loads(creds_json)

    # Define required scopes
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Create credentials using google.auth
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)

    # Authorize with gspread
    client = gspread.authorize(creds)

    # Open the specified sheet and worksheet
    sheet = client.open(sheet_name).worksheet(worksheet_name)
    return sheet
