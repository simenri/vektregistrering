import streamlit as st
import base64
import json
import re

from io import BytesIO
from services.sheets_service import get_google_sheet
from utils.helpers import get_todays_date, get_timestamp
from components.batch_selector import render_batch_selector
from components.empty_or_full_selector import render_empty_or_full_selector
from components.aksel_selector import render_aksel_selector
from components.ocr_camera_feature import render_ocr_camera_feature
from services.environment_variable_service import set_enivronment_variable
from google.cloud import vision
import os
import tempfile



# Configuration
st.set_page_config(page_title="Weight Registration - Carbon Centric", page_icon="📱", initial_sidebar_state="collapsed")

# Connect to Sheets
@st.cache_data(ttl=300)  # Cache i 5 minutter
def get_measurement_sheet():
    return get_google_sheet("Tankbil-CC", "Measurements")

@st.cache_data(ttl=300)  # Cache i 5 minutter
def get_batch_sheet():
    return get_google_sheet("Tankbil-CC", "Batches")

@st.cache_data(ttl=300)
def get_batch_info():
    batch_sheet = get_google_sheet("Tankbil-CC", "Batches")
    return batch_sheet.get_all_records()


# sheet = get_measurement_sheet()
sheet = get_google_sheet("Tankbil-CC", "Measurements")
batch_sheet = get_batch_sheet()
batch_info = get_batch_info()
todays_date = get_todays_date()
available_batches = [r['Batch ID'] for r in batch_info if r['Date of analysis'].strip() == todays_date]

# UI
st.markdown("<h2>Weight Registration - Carbon Centric AS</h2>", unsafe_allow_html=True)

selected_batch = render_batch_selector(available_batches, todays_date)
st.write(f"Selected batch number: {selected_batch}")

filling_status = render_empty_or_full_selector()
weight_value = 0  # Set default weight

col1, col2 = st.columns(2)
with col1:
    axle = render_aksel_selector()
with col2:
    use_camera = st.checkbox('Use Camera for Weight Detection')

# Session state
if "detected_num" not in st.session_state:
    st.session_state.detected_num = 0
if "uploaded_proof_image" not in st.session_state:
    st.session_state.uploaded_proof_image = None

# --- Weight Detection with Camera and Vision API ---
if use_camera:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = set_enivronment_variable()
    img_file_detection = st.camera_input("Take a picture of the scale for automatic detection")

    if img_file_detection is not None:
        st.image(img_file_detection)
        
        # Vision API
        image_bytes = img_file_detection.getvalue()
        image = vision.Image(content=image_bytes)
        client = vision.ImageAnnotatorClient()
        response = client.text_detection(image=image)

        texts = response.text_annotations
        if texts:
            detected_text = texts[0].description.strip()
            numbers = re.findall(r'\d+', detected_text)
            if numbers:
                detected_text = ''.join(numbers)
                st.session_state.detected_num = int(detected_text)
                st.success(f"Detected number: {detected_text}")
            else:
                st.warning("No numbers detected in the image.")
                st.session_state.detected_num = 0
        else:
            st.warning("Could not extract any text from the image.")
            st.session_state.detected_num = 0

    weight_input = st.session_state.detected_num
else:
    weight_input = st.number_input("Weight (kg)", value=st.session_state.detected_num, step=1)

# Show registered weight
st.write(f"Registered weight: {weight_input}")

# --- Independent Image Upload for Documentation ---
# st.markdown("### Upload a photo as proof (optional)")
# uploaded_proof_image = st.file_uploader("Upload an image file", type=["jpg", "jpeg", "png"])
# if uploaded_proof_image:
#     st.image(uploaded_proof_image, caption="Uploaded Proof Image", width=300)
#     st.session_state.uploaded_proof_image = uploaded_proof_image

# --- Submission confirmation ---
if st.button("Submit"):
    if selected_batch and weight_input:
        st.session_state.show_confirmation = True
        st.session_state.selected_batch = selected_batch
        st.session_state.filling_status = filling_status
        st.session_state.axle = axle
        st.session_state.weight_input = weight_input
    else:
        st.error("Please fill in all fields.")

if st.session_state.get("show_confirmation"):
    with st.expander("Review your registration before final submission"):
        st.write(f"**Batch:** {st.session_state.selected_batch}")
        st.write(f"**Filling status:** {st.session_state.filling_status}")
        st.write(f"**Axle:** {st.session_state.axle}")
        st.write(f"**Weight (kg):** {st.session_state.weight_input}")

        if st.button("Confirm and send"):
            timestamp = get_timestamp()
            sheet.append_row([
                timestamp,
                st.session_state.filling_status,
                st.session_state.axle,
                st.session_state.selected_batch,
                st.session_state.weight_input
            ])
            st.success("Data successfully submitted!")

            # Reset session state after sending
            st.session_state.show_confirmation = False

# Footer
st.markdown("<div class='footer'>© 2025 Carbon Centric AS | Weight Registration</div>", unsafe_allow_html=True)