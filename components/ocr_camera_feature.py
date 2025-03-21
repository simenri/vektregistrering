import streamlit as st
import re
from google.cloud import vision



def render_ocr_camera_feature():
    img_file = st.camera_input("Ta bilde av vekta")
    detected_num = 0

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
            numbers = re.findall(r'\d+', detected_text)
            if numbers:
                detected_text = ''.join(numbers)
                detected_num = int(detected_text)
            st.success(f"Oppdaget tall: {detected_text}")
        else:
            st.warning("Fikk ikke tolket noe tall fra bildet.")
    return detected_num
