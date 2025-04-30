import base64
import json
import io
import streamlit as st
import mimetypes
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

def upload_to_drive(file, filename, folder_id=None):
    # Step 1: Decode credentials
    encoded_creds = st.secrets["google"]["google_credentials"]
    padding = len(encoded_creds) % 4
    if padding != 0:
        encoded_creds += "=" * (4 - padding)
    creds_dict = json.loads(base64.b64decode(encoded_creds))

    # Step 2: Set up Drive API
    scopes = ["https://www.googleapis.com/auth/drive.file"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    drive_service = build("drive", "v3", credentials=creds)

    # Step 3: Guess MIME type
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type is None:
        mime_type = "image/jpeg"

    # Step 4: Get file content
    file_bytes = file.getvalue()
    file_size = len(file_bytes)
    if file_size == 0:
        raise ValueError("The uploaded file is empty!")

    # # Log file info for debug
    # st.write({
    #     "Uploading file": filename,
    #     "Mime type": mime_type,
    #     "Size (bytes)": file_size,
    #     "To folder": folder_id
    # })

    # Step 5: Upload
    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime_type)
    metadata = {"name": filename}
    if folder_id:
        metadata["parents"] = [folder_id]

    uploaded_file = drive_service.files().create(
        body=metadata,
        media_body=media,
        fields="id"
    ).execute()

    return uploaded_file.get("id")
