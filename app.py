import streamlit as st
import time
from utils.helpers import get_todays_date, get_timestamp
from services.sheets_service import get_google_sheet
from components.batch_selector import render_batch_selector
from components.empty_or_full_selector import render_empty_or_full_selector
from components.aksel_selector import render_aksel_selector
from components.image_uploader import render_proof_image_uploader
from services.upload_to_drive import upload_to_drive

# Konfig
st.set_page_config(page_title="Weight Registration", page_icon="📱", initial_sidebar_state="collapsed")

# Caching
@st.cache_resource
def get_measurement_sheet():
    return get_google_sheet("Tankbil-CC", "Measurements")

@st.cache_data(ttl=300)
def get_batch_info():
    return get_google_sheet("Tankbil-CC", "Batches").get_all_records()

@st.cache_data(ttl=300)
def get_user_info():
    return get_google_sheet("Tankbil-CC", "Users").get_all_records()

# --- Login system ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.name = ""

if not st.session_state.logged_in:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log in"):
        users = get_user_info()
        for user in users:
            if user["username"] == username and user["password"] == password and str(user.get("valid", "TRUE")).upper() == "TRUE":
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.name = user.get("name", username)
                st.success(f"Welcome, {st.session_state.name}!")
                st.rerun()
        else:
            st.error("Invalid username or password, or access not granted.")
    st.stop()

# Init
sheet = get_measurement_sheet()
batch_info = get_batch_info()
todays_date = get_todays_date()
available_batches = [r['Batch ID'] for r in batch_info if r['Date of analysis'].strip() == todays_date]

# Session state defaults
for key, default in {
    "selected_batch": None,
    "filling_status": None,
    "axle": None,
    "weight_input": 0,
    "uploaded_image": None,
    "show_confirmation": False
}.items():
    st.session_state.setdefault(key, default)

# --- INPUTS ---
st.markdown("## Weight Registration - Carbon Centric")

st.session_state.selected_batch = render_batch_selector(available_batches, todays_date)
st.session_state.filling_status = render_empty_or_full_selector()
st.session_state.axle = render_aksel_selector()
st.session_state.weight_input = st.number_input("Weight (kg)", value=st.session_state.weight_input, step=1)

render_proof_image_uploader()

# --- Submit ---
if st.button("Submit"):
    if all([st.session_state.selected_batch, st.session_state.filling_status, st.session_state.axle, st.session_state.weight_input > 0]):
        st.session_state.show_confirmation = True
    else:
        st.error("Please fill in all fields.")

# --- Confirm ---
if st.session_state.show_confirmation:
    st.markdown("### Review before sending:")
    st.write(f"**Batch:** {st.session_state.selected_batch}")
    st.write(f"**Filling status:** {st.session_state.filling_status}")
    st.write(f"**Axle:** {st.session_state.axle}")
    st.write(f"**Weight (kg):** {st.session_state.weight_input}")
    if st.session_state.uploaded_image:
        st.image(st.session_state.uploaded_image, caption="Selected image", use_container_width=True)
    else:
        st.write("*No proof image uploaded.*")

    if st.button("Confirm and send"):
        timestamp = get_timestamp()
        sheet.append_row([
            timestamp,
            st.session_state.name,  # who submitted
            st.session_state.filling_status,
            st.session_state.axle,
            st.session_state.selected_batch,
            st.session_state.weight_input
        ])
        if st.session_state.uploaded_image:
            filename = f"{timestamp}_{st.session_state.selected_batch}.png".replace(" ", "_")
            try:
                file_id = upload_to_drive(
                    st.session_state.uploaded_image,
                    filename,
                    folder_id=st.secrets["google"]["drive_folder_id"]
                )
                drive_url = f"https://drive.google.com/file/d/{file_id}/view"
                st.success(f"✅ Uploaded to Drive: [View image]({drive_url})")
            except Exception as e:
                st.warning(f"Upload failed: {e}")
        else:
            st.success("✅ Registration submitted!")

        # Rydd opp
        for key in ["selected_batch", "filling_status", "axle", "weight_input", "uploaded_image", "show_confirmation"]:
            st.session_state[key] = None

        # Nedtelling
        with st.empty():
            for i in range(5, 0, -1):
                st.info(f"Returning to fresh form in {i} seconds...")
                time.sleep(1)
        st.rerun()
