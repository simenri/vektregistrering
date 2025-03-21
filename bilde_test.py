import streamlit as st
from google.cloud import vision
import io
import os

# Sett Google credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_sheet_creds.json"

st.title("Vektregistrering med bilde")

# Ta bilde med kamera
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
