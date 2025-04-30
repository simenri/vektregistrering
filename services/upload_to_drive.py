import base64
import json
import io
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

def upload_to_drive(file, filename, folder_id=None):
    encoded_creds = st.secrets["google"]["google_credentials"]
    padding = len(encoded_creds) % 4
    if padding != 0:
        encoded_creds += "=" * (4 - padding)

    creds_dict = json.loads(base64.b64decode(encoded_creds))
    scopes = ["https://www.googleapis.com/auth/drive.file"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    drive_service = build("drive", "v3", credentials=creds)

    media = MediaIoBaseUpload(io.BytesIO(file.getvalue()), mimetype=file.type)
    body = {
        "name": filename,
        "parents": [folder_id] if folder_id else []
    }

    uploaded_file = drive_service.files().create(body=body, media_body=media, fields="id").execute()
    return uploaded_file.get("id")
