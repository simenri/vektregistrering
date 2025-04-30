import streamlit as st
import json
import base64
import gspread
from google.oauth2.service_account import Credentials
from utils.helpers import get_todays_date, get_timestamp
from components.batch_selector import render_batch_selector
from components.empty_or_full_selector import render_empty_or_full_selector
from components.aksel_selector import render_aksel_selector
from components.image_uploader import render_proof_image_uploader
from services.sheets_service import get_google_sheet
import services.upload_to_drive
import time


# --- Config ---
st.set_page_config(page_title="Weight Registration - Carbon Centric", page_icon="📱", initial_sidebar_state="collapsed")

# --- Cache: Sheets connection ---
@st.cache_resource
def get_measurement_sheet():
    return get_google_sheet("Tankbil-CC", "Measurements")

@st.cache_data(ttl=300)
def get_batch_info():
    sheet = get_google_sheet("Tankbil-CC", "Batches")
    return sheet.get_all_records()

sheet = get_measurement_sheet()
batch_info = get_batch_info()

# --- Today's available batches ---
todays_date = get_todays_date()
available_batches = [r['Batch ID'] for r in batch_info if r['Date of analysis'].strip() == todays_date]

# --- Session state init ---
for key, default in {
    "selected_batch": None,
    "filling_status": None,
    "axle": None,
    "weight_input": 0,
    "show_confirmation": False
}.items():
    st.session_state.setdefault(key, default)

# --- UI ---
st.markdown("<h2>Weight Registration - Carbon Centric AS</h2>", unsafe_allow_html=True)

# --- Input Form ---
with st.form("registration_form"):
    st.session_state.selected_batch = render_batch_selector(available_batches, todays_date)
    st.session_state.filling_status = render_empty_or_full_selector()
    st.session_state.axle = render_aksel_selector()
    st.session_state.weight_input = st.number_input("Weight (kg)", value=st.session_state.weight_input, step=1)
    render_proof_image_uploader()
    submitted = st.form_submit_button("Submit")

if submitted:
    if all([
        st.session_state.selected_batch,
        st.session_state.filling_status,
        st.session_state.axle,
        st.session_state.weight_input > 0
    ]):
        st.session_state.show_confirmation = True
    else:
        st.error("Please fill in all fields.")

# --- Confirmation ---
if st.session_state.show_confirmation:
    with st.expander("Review your registration before final submission"):
        st.write(f"**Batch:** {st.session_state.selected_batch}")
        st.write(f"**Filling status:** {st.session_state.filling_status}")
        st.write(f"**Axle:** {st.session_state.axle}")
        st.write(f"**Weight (kg):** {st.session_state.weight_input}")

        if st.button("Confirm and send"):
            timestamp = get_timestamp()

            # Send data til Google Sheets
            sheet.append_row([
                timestamp,
                st.session_state.filling_status,
                st.session_state.axle,
                st.session_state.selected_batch,
                st.session_state.weight_input
            ])

            # Valgfri opplasting av bilde til Google Drive
            if st.session_state.uploaded_image:
                from services.upload_to_drive import upload_to_drive
                filename = f"{timestamp}_{st.session_state.selected_batch}.jpg".replace(" ", "_")
                upload_to_drive(
                    st.session_state.uploaded_image,
                    filename,
                    folder_id=st.secrets["google"].get("drive_folder_id")
                )

            # Vis suksessmelding
            st.success("✅ Registration submitted!")

            # Vis nedtelling
            with st.empty():
                for i in range(3, 0, -1):
                    st.info(f"Returning to new form in {i} seconds...")
                    time.sleep(1)

            # Nullstill skjema
            for key in ["selected_batch", "filling_status", "axle", "weight_input", "show_confirmation", "uploaded_image"]:
                st.session_state[key] = None

            st.rerun()


# --- Footer ---
st.markdown("<div class='footer'>© 2025 Carbon Centric AS | Weight Registration</div>", unsafe_allow_html=True)
